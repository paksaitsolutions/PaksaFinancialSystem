from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.modules.core_financials.accounts_payable.models import Invoice, InvoiceStatus, InvoiceLine, Vendor
from app.modules.core_financials.accounts_payable.schemas import InvoiceCreate, InvoiceUpdate
from app.core.exceptions import NotFoundError, ValidationError

class InvoiceService:
    def __init__(self, db: Session):
        self.db = db

    def create_invoice(self, invoice_data: InvoiceCreate) -> Invoice:
        """Create a new invoice"""
        # Check if vendor exists
        vendor = self.db.query(Vendor).filter(Vendor.id == invoice_data.vendor_id).first()
        if not vendor:
            raise NotFoundError(f"Vendor with ID {invoice_data.vendor_id} not found")

        # Calculate due date if not provided
        due_date = invoice_data.due_date
        if not due_date:
            payment_terms = vendor.payment_terms or "net30"
            days = int(payment_terms.replace("net", ""))
            due_date = (datetime.utcnow() + timedelta(days=days)).date()

        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_data.invoice_number,
            vendor_id=invoice_data.vendor_id,
            invoice_date=invoice_data.invoice_date or date.today(),
            due_date=due_date,
            description=invoice_data.description,
            po_number=invoice_data.po_number,
            status=InvoiceStatus.DRAFT,
            subtotal=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("0.00"),
            balance_due=Decimal("0.00")
        )
        
        self.db.add(invoice)
        self.db.flush()  # To get the invoice ID for line items
        
        # Add line items
        total_amount = Decimal("0.00")
        for line in invoice_data.lines:
            line_total = line.quantity * line.unit_price * (1 - (line.discount_percentage or 0) / 100)
            total_amount += line_total
            
            invoice_line = InvoiceLine(
                invoice_id=invoice.id,
                line_number=line.line_number,
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                discount_percentage=line.discount_percentage,
                line_total=line_total,
                tax_rate=line.tax_rate or Decimal("0.00"),
                tax_amount=line_total * (line.tax_rate or Decimal("0.00")) / 100,
                account_id=line.account_id,
                cost_center=line.cost_center
            )
            self.db.add(invoice_line)
        
        # Update invoice totals
        invoice.subtotal = total_amount
        invoice.tax_amount = sum(line.tax_amount for line in invoice.lines)
        invoice.total_amount = invoice.subtotal + invoice.tax_amount - invoice.discount_amount
        invoice.balance_due = invoice.total_amount
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_invoice(self, invoice_id: int) -> Invoice:
        """Get an invoice by ID with line items"""
        invoice = (
            self.db.query(Invoice)
            .options(joinedload(Invoice.lines))
            .filter(Invoice.id == invoice_id)
            .first()
        )
        if not invoice:
            raise NotFoundError(f"Invoice with ID {invoice_id} not found")
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
        """Get a list of invoices with optional filtering"""
        query = self.db.query(Invoice).options(joinedload(Invoice.vendor))
        
        if search:
            search_pattern = f"%{search}%"
            query = query.join(Vendor).filter(
                or_(
                    Invoice.invoice_number.ilike(search_pattern),
                    Invoice.po_number.ilike(search_pattern),
                    Vendor.name.ilike(search_pattern)
                )
            )
        
        if status:
            try:
                status_enum = InvoiceStatus(status)
                query = query.filter(Invoice.status == status_enum)
            except ValueError:
                # Skip invalid status values
                pass
                
        if vendor_id:
            query = query.filter(Invoice.vendor_id == vendor_id)
            
        if date_from:
            query = query.filter(Invoice.invoice_date >= date_from)
            
        if date_to:
            query = query.filter(Invoice.invoice_date <= date_to)
        
        return query.offset(skip).limit(limit).all()

    def update_invoice(self, invoice_id: int, invoice_data: InvoiceUpdate) -> Invoice:
        """Update an existing invoice"""
        invoice = self.get_invoice(invoice_id)
        
        # Prevent updates to paid or processed invoices
        if invoice.status in [InvoiceStatus.PAID, InvoiceStatus.PROCESSED]:
            raise ValidationError("Cannot modify a paid or processed invoice")
        
        update_data = invoice_data.dict(exclude_unset=True)
        
        # Update basic fields
        for field in ["description", "po_number", "discount_amount"]:
            if field in update_data:
                setattr(invoice, field, update_data[field])
        
        # Recalculate totals if needed
        if any(field in update_data for field in ["discount_amount"]):
            invoice.total_amount = invoice.subtotal + invoice.tax_amount - invoice.discount_amount
            invoice.balance_due = invoice.total_amount - invoice.paid_amount
        
        invoice.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def approve_invoice(self, invoice_id: int, approved_by: str) -> Invoice:
        """Approve an invoice for payment"""
        invoice = self.get_invoice(invoice_id)
        
        if invoice.status != InvoiceStatus.PENDING_APPROVAL:
            raise ValidationError("Only invoices pending approval can be approved")
        
        invoice.status = InvoiceStatus.APPROVED
        invoice.approved_by = approved_by
        invoice.approved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_vendor_invoices(self, vendor_id: int, status: Optional[str] = None) -> List[Invoice]:
        """Get all invoices for a specific vendor"""
        query = self.db.query(Invoice).filter(Invoice.vendor_id == vendor_id)
        
        if status:
            try:
                status_enum = InvoiceStatus(status)
                query = query.filter(Invoice.status == status_enum)
            except ValueError:
                # Skip invalid status values
                pass
                
        return query.order_by(Invoice.due_date).all()

    def get_overdue_invoices(self) -> List[Invoice]:
        """Get all overdue invoices"""
        return (
            self.db.query(Invoice)
            .filter(
                Invoice.status == InvoiceStatus.APPROVED,
                Invoice.due_date < date.today(),
                Invoice.balance_due > 0
            )
            .order_by(Invoice.due_date)
            .all()
        )
