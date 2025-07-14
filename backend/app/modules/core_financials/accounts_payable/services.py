from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case, extract
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.modules.core_financials.accounts_payable.models import (
    Vendor, Invoice, InvoiceLine, Payment, PaymentInvoice
)
from app.modules.core_financials.accounts_payable.schemas import (
    VendorCreate, VendorUpdate, InvoiceCreate, InvoiceUpdate,
    PaymentCreate, PaymentUpdate, APSummaryResponse, AgingReportResponse,
    AgingReportItem, VendorSummaryResponse
)
from app.core.exceptions import NotFoundError, ValidationError

class VendorService:
    def __init__(self, db: Session):
        self.db = db

    def create_vendor(self, vendor_data: VendorCreate) -> Vendor:
        # Generate vendor ID
        last_vendor = self.db.query(Vendor).order_by(Vendor.id.desc()).first()
        vendor_id = f"V{str((last_vendor.id if last_vendor else 0) + 1).zfill(3)}"
        
        vendor = Vendor(
            vendor_id=vendor_id,
            **vendor_data.dict()
        )
        self.db.add(vendor)
        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    def get_vendor(self, vendor_id: int) -> Vendor:
        vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise NotFoundError(f"Vendor with id {vendor_id} not found")
        return vendor

    def get_vendors(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Vendor]:
        query = self.db.query(Vendor)
        
        if search:
            query = query.filter(
                or_(
                    Vendor.name.ilike(f"%{search}%"),
                    Vendor.vendor_id.ilike(f"%{search}%"),
                    Vendor.contact_person.ilike(f"%{search}%")
                )
            )
        
        if status:
            query = query.filter(Vendor.status == status)
        
        if category:
            query = query.filter(Vendor.category == category)
        
        return query.offset(skip).limit(limit).all()

    def update_vendor(self, vendor_id: int, vendor_data: VendorUpdate) -> Vendor:
        vendor = self.get_vendor(vendor_id)
        
        for field, value in vendor_data.dict(exclude_unset=True).items():
            setattr(vendor, field, value)
        
        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    def delete_vendor(self, vendor_id: int) -> bool:
        vendor = self.get_vendor(vendor_id)
        
        # Check if vendor has outstanding invoices
        outstanding_invoices = self.db.query(Invoice).filter(
            and_(
                Invoice.vendor_id == vendor_id,
                Invoice.balance_due > 0
            )
        ).count()
        
        if outstanding_invoices > 0:
            raise ValidationError("Cannot delete vendor with outstanding invoices")
        
        self.db.delete(vendor)
        self.db.commit()
        return True

    def get_vendor_summary(self, vendor_id: int) -> VendorSummaryResponse:
        vendor = self.get_vendor(vendor_id)
        
        # Get vendor statistics
        invoice_stats = self.db.query(
            func.count(Invoice.id).label('total_invoices'),
            func.sum(Invoice.balance_due).label('outstanding_balance')
        ).filter(Invoice.vendor_id == vendor_id).first()
        
        # Get last payment date
        last_payment = self.db.query(Payment.payment_date).filter(
            Payment.vendor_id == vendor_id
        ).order_by(Payment.payment_date.desc()).first()
        
        return VendorSummaryResponse(
            vendor_id=vendor.id,
            vendor_name=vendor.name,
            total_invoices=invoice_stats.total_invoices or 0,
            outstanding_balance=invoice_stats.outstanding_balance or Decimal('0.00'),
            last_payment_date=last_payment.payment_date if last_payment else None,
            payment_terms=vendor.payment_terms
        )

class InvoiceService:
    def __init__(self, db: Session):
        self.db = db

    def create_invoice(self, invoice_data: InvoiceCreate) -> Invoice:
        # Generate invoice number if not provided
        if not invoice_data.invoice_number:
            last_invoice = self.db.query(Invoice).order_by(Invoice.id.desc()).first()
            invoice_data.invoice_number = f"INV-{datetime.now().year}-{str((last_invoice.id if last_invoice else 0) + 1).zfill(3)}"
        
        # Create invoice
        invoice_dict = invoice_data.dict(exclude={'lines'})
        invoice = Invoice(**invoice_dict)
        
        # Calculate totals
        subtotal = sum(line.quantity * line.unit_price for line in invoice_data.lines)
        invoice.subtotal = subtotal
        invoice.total_amount = subtotal + invoice_data.tax_amount
        invoice.balance_due = invoice.total_amount
        
        self.db.add(invoice)
        self.db.flush()  # Get invoice ID
        
        # Create invoice lines
        for line_data in invoice_data.lines:
            line = InvoiceLine(
                invoice_id=invoice.id,
                **line_data.dict()
            )
            line.line_total = line.quantity * line.unit_price
            self.db.add(line)
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise NotFoundError(f"Invoice with id {invoice_id} not found")
        return invoice

    def get_invoices(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        vendor_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Invoice]:
        query = self.db.query(Invoice)
        
        if search:
            query = query.filter(
                or_(
                    Invoice.invoice_number.ilike(f"%{search}%"),
                    Invoice.description.ilike(f"%{search}%")
                )
            )
        
        if status:
            query = query.filter(Invoice.status == status)
        
        if vendor_id:
            query = query.filter(Invoice.vendor_id == vendor_id)
        
        if date_from:
            query = query.filter(Invoice.invoice_date >= date_from)
        
        if date_to:
            query = query.filter(Invoice.invoice_date <= date_to)
        
        return query.order_by(Invoice.invoice_date.desc()).offset(skip).limit(limit).all()

    def update_invoice(self, invoice_id: int, invoice_data: InvoiceUpdate) -> Invoice:
        invoice = self.get_invoice(invoice_id)
        
        # Update invoice fields
        for field, value in invoice_data.dict(exclude_unset=True, exclude={'lines'}).items():
            setattr(invoice, field, value)
        
        # Update lines if provided
        if invoice_data.lines is not None:
            # Delete existing lines
            self.db.query(InvoiceLine).filter(InvoiceLine.invoice_id == invoice_id).delete()
            
            # Create new lines
            subtotal = Decimal('0.00')
            for line_data in invoice_data.lines:
                line = InvoiceLine(
                    invoice_id=invoice.id,
                    **line_data.dict()
                )
                line.line_total = line.quantity * line.unit_price
                subtotal += line.line_total
                self.db.add(line)
            
            # Update totals
            invoice.subtotal = subtotal
            invoice.total_amount = subtotal + (invoice.tax_amount or Decimal('0.00'))
            invoice.balance_due = invoice.total_amount - (invoice.paid_amount or Decimal('0.00'))
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def approve_invoice(self, invoice_id: int, approved_by: str) -> Invoice:
        invoice = self.get_invoice(invoice_id)
        
        if invoice.status != 'pending':
            raise ValidationError("Only pending invoices can be approved")
        
        invoice.status = 'approved'
        invoice.approved_by = approved_by
        invoice.approved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_overdue_invoices(self) -> List[Invoice]:
        today = date.today()
        return self.db.query(Invoice).filter(
            and_(
                Invoice.due_date < today,
                Invoice.balance_due > 0,
                Invoice.status.in_(['approved', 'overdue'])
            )
        ).all()

class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_payment(self, payment_data: PaymentCreate) -> Payment:
        # Generate payment number
        last_payment = self.db.query(Payment).order_by(Payment.id.desc()).first()
        payment_number = f"PAY-{datetime.now().year}-{str((last_payment.id if last_payment else 0) + 1).zfill(3)}"
        
        # Create payment
        payment_dict = payment_data.dict(exclude={'invoice_ids'})
        payment = Payment(
            payment_number=payment_number,
            **payment_dict
        )
        
        self.db.add(payment)
        self.db.flush()  # Get payment ID
        
        # Link invoices to payment
        total_applied = Decimal('0.00')
        for invoice_id in payment_data.invoice_ids:
            invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                raise NotFoundError(f"Invoice with id {invoice_id} not found")
            
            # Calculate amount to apply (up to balance due)
            amount_to_apply = min(payment_data.amount - total_applied, invoice.balance_due)
            
            if amount_to_apply > 0:
                payment_invoice = PaymentInvoice(
                    payment_id=payment.id,
                    invoice_id=invoice_id,
                    amount_applied=amount_to_apply
                )
                self.db.add(payment_invoice)
                
                # Update invoice
                invoice.paid_amount = (invoice.paid_amount or Decimal('0.00')) + amount_to_apply
                invoice.balance_due = invoice.total_amount - invoice.paid_amount
                
                if invoice.balance_due <= 0:
                    invoice.status = 'paid'
                
                total_applied += amount_to_apply
        
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment(self, payment_id: int) -> Payment:
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise NotFoundError(f"Payment with id {payment_id} not found")
        return payment

    def get_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        method: Optional[str] = None,
        vendor_id: Optional[int] = None
    ) -> List[Payment]:
        query = self.db.query(Payment)
        
        if search:
            query = query.filter(
                or_(
                    Payment.payment_number.ilike(f"%{search}%"),
                    Payment.reference_number.ilike(f"%{search}%")
                )
            )
        
        if status:
            query = query.filter(Payment.status == status)
        
        if method:
            query = query.filter(Payment.payment_method == method)
        
        if vendor_id:
            query = query.filter(Payment.vendor_id == vendor_id)
        
        return query.order_by(Payment.payment_date.desc()).offset(skip).limit(limit).all()

    def process_payment(self, payment_id: int) -> Payment:
        payment = self.get_payment(payment_id)
        
        if payment.status != 'pending':
            raise ValidationError("Only pending payments can be processed")
        
        payment.status = 'processed'
        payment.processed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payment)
        return payment

class APAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_ap_summary(self) -> APSummaryResponse:
        # Total outstanding
        total_outstanding = self.db.query(
            func.sum(Invoice.balance_due)
        ).filter(Invoice.balance_due > 0).scalar() or Decimal('0.00')
        
        # Overdue amount
        today = date.today()
        overdue_amount = self.db.query(
            func.sum(Invoice.balance_due)
        ).filter(
            and_(
                Invoice.due_date < today,
                Invoice.balance_due > 0
            )
        ).scalar() or Decimal('0.00')
        
        # This month invoices
        current_month = datetime.now().replace(day=1)
        this_month_invoices = self.db.query(
            func.sum(Invoice.total_amount)
        ).filter(
            Invoice.invoice_date >= current_month
        ).scalar() or Decimal('0.00')
        
        # Pending approval
        pending_approval = self.db.query(
            func.sum(Invoice.total_amount)
        ).filter(Invoice.status == 'pending').scalar() or Decimal('0.00')
        
        # Vendor counts
        total_vendors = self.db.query(Vendor).count()
        active_vendors = self.db.query(Vendor).filter(Vendor.status == 'active').count()
        
        return APSummaryResponse(
            total_outstanding=total_outstanding,
            overdue_amount=overdue_amount,
            this_month_invoices=this_month_invoices,
            pending_approval=pending_approval,
            total_vendors=total_vendors,
            active_vendors=active_vendors
        )

    def get_aging_report(self, as_of_date: Optional[date] = None) -> AgingReportResponse:
        if not as_of_date:
            as_of_date = date.today()
        
        # Build aging buckets query
        aging_query = self.db.query(
            Vendor.id.label('vendor_id'),
            Vendor.name.label('vendor_name'),
            func.sum(
                case(
                    (Invoice.due_date >= as_of_date, Invoice.balance_due),
                    else_=0
                )
            ).label('current'),
            func.sum(
                case(
                    (and_(
                        Invoice.due_date < as_of_date,
                        Invoice.due_date >= as_of_date - timedelta(days=30)
                    ), Invoice.balance_due),
                    else_=0
                )
            ).label('days_1_30'),
            func.sum(
                case(
                    (and_(
                        Invoice.due_date < as_of_date - timedelta(days=30),
                        Invoice.due_date >= as_of_date - timedelta(days=60)
                    ), Invoice.balance_due),
                    else_=0
                )
            ).label('days_31_60'),
            func.sum(
                case(
                    (and_(
                        Invoice.due_date < as_of_date - timedelta(days=60),
                        Invoice.due_date >= as_of_date - timedelta(days=90)
                    ), Invoice.balance_due),
                    else_=0
                )
            ).label('days_61_90'),
            func.sum(
                case(
                    (Invoice.due_date < as_of_date - timedelta(days=90), Invoice.balance_due),
                    else_=0
                )
            ).label('over_90_days'),
            func.sum(Invoice.balance_due).label('total_outstanding')
        ).join(Invoice).filter(
            Invoice.balance_due > 0
        ).group_by(Vendor.id, Vendor.name).all()
        
        # Convert to response objects
        items = []
        totals = AgingReportItem(
            vendor_id=0,
            vendor_name="TOTALS",
            current=Decimal('0.00'),
            days_1_30=Decimal('0.00'),
            days_31_60=Decimal('0.00'),
            days_61_90=Decimal('0.00'),
            over_90_days=Decimal('0.00'),
            total_outstanding=Decimal('0.00')
        )
        
        for row in aging_query:
            item = AgingReportItem(
                vendor_id=row.vendor_id,
                vendor_name=row.vendor_name,
                current=row.current or Decimal('0.00'),
                days_1_30=row.days_1_30 or Decimal('0.00'),
                days_31_60=row.days_31_60 or Decimal('0.00'),
                days_61_90=row.days_61_90 or Decimal('0.00'),
                over_90_days=row.over_90_days or Decimal('0.00'),
                total_outstanding=row.total_outstanding or Decimal('0.00')
            )
            items.append(item)
            
            # Add to totals
            totals.current += item.current
            totals.days_1_30 += item.days_1_30
            totals.days_31_60 += item.days_31_60
            totals.days_61_90 += item.days_61_90
            totals.over_90_days += item.over_90_days
            totals.total_outstanding += item.total_outstanding
        
        return AgingReportResponse(
            report_date=as_of_date,
            items=items,
            totals=totals
        )