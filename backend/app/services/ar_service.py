from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
import uuid

from app.models.core_models import Customer, ARInvoice, ARPayment

# Use unified models from core_models

class ARService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    # Customer methods
    async def get_customers(self):
        return self.db.query(Customer).filter(Customer.company_id == self.tenant_id).all()
    
    async def get_customer(self, customer_id: str):
        return self.db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.company_id == self.tenant_id
        ).first()
    
    async def create_customer(self, customer_data: dict):
        customer = Customer(
            company_id=self.tenant_id,
            customer_code=f"CUST{len(self.db.query(Customer).all()) + 1:04d}",
            customer_name=customer_data.get("name"),
            email=customer_data.get("email"),
            phone=customer_data.get("phone"),
            address=customer_data.get("address"),
            credit_limit=customer_data.get("creditLimit", 0.0),
            current_balance=customer_data.get("balance", 0.0),
            payment_terms=customer_data.get("paymentTerms", "net30"),
            status=customer_data.get("status", "active")
        )
        
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    async def update_customer(self, customer_id: str, customer_data: dict):
        customer = await self.get_customer(customer_id)
        if not customer:
            return None
        
        for key, value in customer_data.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        
        customer.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    async def delete_customer(self, customer_id: str) -> bool:
        customer = await self.get_customer(customer_id)
        if not customer:
            return False
        
        self.db.delete(customer)
        self.db.commit()
        return True
    
    # Invoice methods
    async def get_invoices(self) -> List[Invoice]:
        return self.db.query(Invoice).filter(Invoice.tenant_id == self.tenant_id).all()
    
    async def create_invoice(self, invoice_data: dict) -> Invoice:
        invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=invoice_data.get("customer_id"),
            invoice_number=invoice_data.get("invoice_number"),
            invoice_date=datetime.fromisoformat(invoice_data.get("invoice_date")),
            due_date=datetime.fromisoformat(invoice_data.get("due_date")),
            total_amount=invoice_data.get("total_amount"),
            status=invoice_data.get("status", "draft")
        )
        
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
    
    # Payment methods
    async def record_payment(self, payment_data: dict) -> Payment:
        payment = Payment(
            tenant_id=self.tenant_id,
            invoice_id=payment_data.get("invoice_id"),
            amount=payment_data.get("amount"),
            payment_date=datetime.fromisoformat(payment_data.get("payment_date")),
            payment_method=payment_data.get("payment_method"),
            reference=payment_data.get("reference")
        )
        
        self.db.add(payment)
        
        # Update invoice paid amount
        invoice = self.db.query(Invoice).filter(Invoice.id == payment_data.get("invoice_id")).first()
        if invoice:
            invoice.paid_amount += payment_data.get("amount")
            if invoice.paid_amount >= invoice.total_amount:
                invoice.status = "paid"
        
        self.db.commit()
        self.db.refresh(payment)
        return payment