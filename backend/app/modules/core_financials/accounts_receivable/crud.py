"""
CRUD operations for Accounts Receivable module
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import date, datetime
from decimal import Decimal

from .models import (
    Customer, ARInvoice, ARInvoiceLine, ARPayment, ARPaymentInvoice,
    CreditMemo, CustomerStatus, InvoiceStatus, PaymentStatus
)
from .schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    ARInvoiceCreate, ARInvoiceUpdate, ARInvoiceResponse,
    ARPaymentCreate, ARPaymentUpdate, ARPaymentResponse
)

class CustomerCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, customer_data: CustomerCreate) -> Customer:
        # Generate customer ID
        last_customer = self.db.query(Customer).order_by(desc(Customer.id)).first()
        customer_id = f"C{str((last_customer.id if last_customer else 0) + 1).zfill(6)}"
        
        customer = Customer(
            customer_id=customer_id,
            **customer_data.dict()
        )
        
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def get(self, customer_id: int) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()
    
    def get_by_customer_id(self, customer_id: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[CustomerStatus] = None
    ) -> List[Customer]:
        query = self.db.query(Customer)
        
        if search:
            query = query.filter(
                or_(
                    Customer.name.ilike(f"%{search}%"),
                    Customer.customer_id.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%")
                )
            )
        
        if status:
            query = query.filter(Customer.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def update(self, customer_id: int, customer_data: CustomerUpdate) -> Optional[Customer]:
        customer = self.get(customer_id)
        if not customer:
            return None
        
        update_data = customer_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        customer.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def delete(self, customer_id: int) -> bool:
        customer = self.get(customer_id)
        if not customer:
            return False
        
        # Check for outstanding invoices
        outstanding_invoices = self.db.query(ARInvoice).filter(
            and_(ARInvoice.customer_id == customer_id, ARInvoice.balance_due > 0)
        ).count()
        
        if outstanding_invoices > 0:
            raise ValueError("Cannot delete customer with outstanding invoices")
        
        self.db.delete(customer)
        self.db.commit()
        return True

class ARInvoiceCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, invoice_data: ARInvoiceCreate) -> ARInvoice:
        # Generate invoice number
        last_invoice = self.db.query(ARInvoice).order_by(desc(ARInvoice.id)).first()
        invoice_number = f"INV-{datetime.now().year}-{str((last_invoice.id if last_invoice else 0) + 1).zfill(6)}"
        
        # Calculate totals
        subtotal = sum(line.quantity * line.unit_price - line.discount_amount for line in invoice_data.lines)
        total_amount = subtotal + invoice_data.tax_amount + invoice_data.shipping_amount - invoice_data.discount_amount
        
        invoice = ARInvoice(
            invoice_number=invoice_number,
            customer_id=invoice_data.customer_id,
            invoice_date=invoice_data.invoice_date,
            due_date=invoice_data.due_date,
            description=invoice_data.description,
            so_number=invoice_data.so_number,
            po_number=invoice_data.po_number,
            subtotal=subtotal,
            tax_amount=invoice_data.tax_amount,
            discount_amount=invoice_data.discount_amount,
            shipping_amount=invoice_data.shipping_amount,
            total_amount=total_amount,
            balance_due=total_amount,
            currency_code=invoice_data.currency_code,
            exchange_rate=invoice_data.exchange_rate,
            status=invoice_data.status,
            order_source=invoice_data.order_source,
            marketplace_order_id=invoice_data.marketplace_order_id,
            tags=invoice_data.tags,
            custom_fields=invoice_data.custom_fields
        )
        
        self.db.add(invoice)
        self.db.flush()
        
        # Add invoice lines
        for line_data in invoice_data.lines:
            line_total = line_data.quantity * line_data.unit_price - line_data.discount_amount
            tax_amount = line_total * (line_data.tax_rate / 100) if line_data.tax_rate else 0
            
            line = ARInvoiceLine(
                invoice_id=invoice.id,
                line_number=line_data.line_number,
                product_code=line_data.product_code,
                description=line_data.description,
                category=line_data.category,
                quantity=line_data.quantity,
                unit_of_measure=line_data.unit_of_measure,
                unit_price=line_data.unit_price,
                discount_percentage=line_data.discount_percentage,
                discount_amount=line_data.discount_amount,
                line_total=line_total,
                tax_code=line_data.tax_code,
                tax_rate=line_data.tax_rate,
                tax_amount=tax_amount,
                revenue_account_id=line_data.revenue_account_id
            )
            self.db.add(line)
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
    
    def get(self, invoice_id: int) -> Optional[ARInvoice]:
        return self.db.query(ARInvoice).filter(ARInvoice.id == invoice_id).first()
    
    def get_by_number(self, invoice_number: str) -> Optional[ARInvoice]:
        return self.db.query(ARInvoice).filter(ARInvoice.invoice_number == invoice_number).first()
    
    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        status: Optional[InvoiceStatus] = None,
        overdue_only: bool = False
    ) -> List[ARInvoice]:
        query = self.db.query(ARInvoice)
        
        if customer_id:
            query = query.filter(ARInvoice.customer_id == customer_id)
        
        if status:
            query = query.filter(ARInvoice.status == status)
        
        if overdue_only:
            query = query.filter(
                and_(ARInvoice.due_date < date.today(), ARInvoice.balance_due > 0)
            )
        
        return query.order_by(desc(ARInvoice.created_at)).offset(skip).limit(limit).all()
    
    def update(self, invoice_id: int, invoice_data: ARInvoiceUpdate) -> Optional[ARInvoice]:
        invoice = self.get(invoice_id)
        if not invoice:
            return None
        
        # Check if invoice can be updated
        if invoice.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
            raise ValueError("Cannot update paid or cancelled invoice")
        
        update_data = invoice_data.dict(exclude_unset=True)
        
        # Handle line items update
        if 'lines' in update_data:
            # Delete existing lines
            self.db.query(ARInvoiceLine).filter(ARInvoiceLine.invoice_id == invoice_id).delete()
            
            # Add new lines
            for line_data in update_data['lines']:
                line_total = line_data['quantity'] * line_data['unit_price'] - line_data.get('discount_amount', 0)
                line = ARInvoiceLine(
                    invoice_id=invoice.id,
                    **line_data,
                    line_total=line_total
                )
                self.db.add(line)
            
            del update_data['lines']
        
        # Update invoice fields
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        # Recalculate totals if needed
        if 'lines' in invoice_data.dict(exclude_unset=True):
            self._recalculate_totals(invoice)
        
        invoice.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
    
    def _recalculate_totals(self, invoice: ARInvoice):
        """Recalculate invoice totals based on lines"""
        lines = self.db.query(ARInvoiceLine).filter(ARInvoiceLine.invoice_id == invoice.id).all()
        subtotal = sum(line.line_total for line in lines)
        invoice.subtotal = subtotal
        invoice.total_amount = subtotal + invoice.tax_amount + invoice.shipping_amount - invoice.discount_amount
        invoice.balance_due = invoice.total_amount - invoice.paid_amount

class ARPaymentCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, payment_data: ARPaymentCreate) -> ARPayment:
        # Generate payment number
        last_payment = self.db.query(ARPayment).order_by(desc(ARPayment.id)).first()
        payment_number = f"PAY-{datetime.now().year}-{str((last_payment.id if last_payment else 0) + 1).zfill(6)}"
        
        payment = ARPayment(
            payment_number=payment_number,
            customer_id=payment_data.customer_id,
            payment_date=payment_data.payment_date,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            reference_number=payment_data.reference_number,
            bank_account_id=payment_data.bank_account_id,
            transaction_id=payment_data.transaction_id,
            currency_code=payment_data.currency_code,
            exchange_rate=payment_data.exchange_rate,
            gateway_transaction_id=payment_data.gateway_transaction_id,
            gateway_name=payment_data.gateway_name,
            notes=payment_data.notes,
            tags=payment_data.tags
        )
        
        self.db.add(payment)
        self.db.flush()
        
        # Apply payment to invoices
        remaining_amount = payment_data.amount
        for i, invoice_id in enumerate(payment_data.invoice_ids):
            if remaining_amount <= 0:
                break
            
            invoice = self.db.query(ARInvoice).filter(ARInvoice.id == invoice_id).first()
            if not invoice:
                continue
            
            # Determine amount to apply
            if payment_data.amounts_applied and i < len(payment_data.amounts_applied):
                amount_to_apply = min(payment_data.amounts_applied[i], remaining_amount, invoice.balance_due)
            else:
                amount_to_apply = min(remaining_amount, invoice.balance_due)
            
            if amount_to_apply > 0:
                # Create payment application
                payment_invoice = ARPaymentInvoice(
                    payment_id=payment.id,
                    invoice_id=invoice_id,
                    amount_applied=amount_to_apply
                )
                self.db.add(payment_invoice)
                
                # Update invoice
                invoice.paid_amount += amount_to_apply
                invoice.balance_due -= amount_to_apply
                
                if invoice.balance_due <= 0:
                    invoice.status = InvoiceStatus.PAID
                elif invoice.paid_amount > 0:
                    invoice.status = InvoiceStatus.PARTIAL_PAYMENT
                
                remaining_amount -= amount_to_apply
        
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get(self, payment_id: int) -> Optional[ARPayment]:
        return self.db.query(ARPayment).filter(ARPayment.id == payment_id).first()
    
    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        status: Optional[PaymentStatus] = None
    ) -> List[ARPayment]:
        query = self.db.query(ARPayment)
        
        if customer_id:
            query = query.filter(ARPayment.customer_id == customer_id)
        
        if status:
            query = query.filter(ARPayment.status == status)
        
        return query.order_by(desc(ARPayment.created_at)).offset(skip).limit(limit).all()
    
    def update(self, payment_id: int, payment_data: ARPaymentUpdate) -> Optional[ARPayment]:
        payment = self.get(payment_id)
        if not payment:
            return None
        
        update_data = payment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)
        
        payment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(payment)
        return payment