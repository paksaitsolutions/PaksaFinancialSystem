from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.modules.core_financials.accounts_payable.models import (
    Payment, PaymentStatus, PaymentMethod, Invoice, Vendor, PaymentInvoice
)
from app.modules.core_financials.accounts_payable.schemas import PaymentCreate, PaymentUpdate
from app.core.exceptions import NotFoundError, ValidationError

class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """Create a new payment"""
        # Validate vendor exists
        vendor = self.db.query(Vendor).filter(Vendor.id == payment_data.vendor_id).first()
        if not vendor:
            raise NotFoundError(f"Vendor with ID {payment_data.vendor_id} not found")
        
        # Create payment
        payment = Payment(
            payment_number=payment_data.payment_number,
            vendor_id=payment_data.vendor_id,
            payment_date=payment_data.payment_date or date.today(),
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            reference_number=payment_data.reference_number,
            currency_code=payment_data.currency_code or vendor.currency_code or 'USD',
            status=PaymentStatus.PENDING,
            notes=payment_data.notes
        )
        
        self.db.add(payment)
        self.db.flush()  # To get the payment ID for invoice applications
        
        # Apply payment to invoices if specified
        total_applied = Decimal("0.00")
        if payment_data.invoice_applications:
            from .invoice_service import InvoiceService
            invoice_service = InvoiceService(self.db)
            
            for app in payment_data.invoice_applications:
                invoice = invoice_service.get_invoice(app.invoice_id)
                
                # Validate invoice belongs to the same vendor
                if invoice.vendor_id != payment.vendor_id:
                    raise ValidationError("Invoice does not belong to the specified vendor")
                
                # Calculate amount to apply (can't exceed invoice balance or payment amount)
                amount_to_apply = min(
                    app.amount_applied or invoice.balance_due,
                    payment.amount - total_applied,
                    invoice.balance_due
                )
                
                if amount_to_apply <= 0:
                    continue
                
                # Create payment application
                payment_invoice = PaymentInvoice(
                    payment_id=payment.id,
                    invoice_id=invoice.id,
                    amount_applied=amount_to_apply,
                    discount_taken=app.discount_taken or Decimal("0.00")
                )
                self.db.add(payment_invoice)
                
                # Update invoice paid amount and status
                invoice.paid_amount += amount_to_apply
                invoice.balance_due = invoice.total_amount - invoice.paid_amount
                
                # Update invoice status if fully paid
                if invoice.balance_due <= 0:
                    invoice.status = InvoiceStatus.PAID
                elif invoice.paid_amount > 0:
                    invoice.status = InvoiceStatus.PARTIALLY_PAID
                
                total_applied += amount_to_apply
                
                # Stop if we've applied the full payment amount
                if total_applied >= payment.amount:
                    break
        
        # Update payment amount to actual applied amount (in case it was less than requested)
        if total_applied > 0 and total_applied != payment.amount:
            payment.amount = total_applied
        
        # If no specific invoices were provided, mark as unapplied
        if not payment_data.invoice_applications and payment.amount > 0:
            payment.status = PaymentStatus.UNAPPLIED
        elif total_applied > 0:
            payment.status = PaymentStatus.APPLIED
        
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment(self, payment_id: int) -> Payment:
        """Get a payment by ID with related data"""
        payment = (
            self.db.query(Payment)
            .options(
                joinedload(Payment.vendor),
                joinedload(Payment.invoice_applications).joinedload(PaymentInvoice.invoice)
            )
            .filter(Payment.id == payment_id)
            .first()
        )
        if not payment:
            raise NotFoundError(f"Payment with ID {payment_id} not found")
        return payment

    def get_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        method: Optional[str] = None,
        vendor_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Payment]:
        """Get a list of payments with optional filtering"""
        query = self.db.query(Payment).options(joinedload(Payment.vendor))
        
        if search:
            search_pattern = f"%{search}%"
            query = query.join(Vendor).filter(
                or_(
                    Payment.payment_number.ilike(search_pattern),
                    Payment.reference_number.ilike(search_pattern),
                    Vendor.name.ilike(search_pattern)
                )
            )
        
        if status:
            try:
                status_enum = PaymentStatus(status)
                query = query.filter(Payment.status == status_enum)
            except ValueError:
                # Skip invalid status values
                pass
                
        if method:
            try:
                method_enum = PaymentMethod(method)
                query = query.filter(Payment.payment_method == method_enum)
            except ValueError:
                # Skip invalid method values
                pass
                
        if vendor_id:
            query = query.filter(Payment.vendor_id == vendor_id)
            
        if date_from:
            query = query.filter(Payment.payment_date >= date_from)
            
        if date_to:
            query = query.filter(Payment.payment_date <= date_to)
        
        return query.order_by(Payment.payment_date.desc()).offset(skip).limit(limit).all()

    def process_payment(self, payment_id: int) -> Payment:
        """Process a payment (e.g., send to bank, record check, etc.)"""
        payment = self.get_payment(payment_id)
        
        if payment.status != PaymentStatus.PENDING:
            raise ValidationError("Only pending payments can be processed")
        
        # Here you would typically integrate with a payment processor or bank API
        # For now, we'll just mark it as processed
        payment.status = PaymentStatus.PROCESSED
        payment.processed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_vendor_payments(self, vendor_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get payment history for a vendor"""
        cutoff_date = date.today() - timedelta(days=days)
        
        payments = (
            self.db.query(Payment)
            .filter(
                Payment.vendor_id == vendor_id,
                Payment.payment_date >= cutoff_date,
                Payment.status.in_([PaymentStatus.PROCESSED, PaymentStatus.APPLIED])
            )
            .order_by(Payment.payment_date.desc())
            .all()
        )
        
        return [
            {
                "id": p.id,
                "payment_number": p.payment_number,
                "payment_date": p.payment_date.isoformat(),
                "amount": float(p.amount),
                "method": p.payment_method.value,
                "reference": p.reference_number,
                "status": p.status.value
            }
            for p in payments
        ]
