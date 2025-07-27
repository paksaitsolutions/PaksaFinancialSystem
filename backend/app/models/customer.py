from sqlalchemy import Column, String, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, GUID

class Customer(BaseModel):
    __tablename__ = "customers"
    
    tenant_id = Column(GUID(), nullable=False, index=True)
    customer_code = Column(String(20), nullable=False, unique=True)
    customer_name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    credit_limit = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    invoices = relationship("ARInvoice", back_populates="customer")
    payments = relationship("ARPayment", back_populates="customer")

class ARInvoice(BaseModel):
    __tablename__ = "ar_invoices"
    
    tenant_id = Column(GUID(), nullable=False, index=True)
    customer_id = Column(GUID(), ForeignKey('customers.id'), nullable=False)
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(String(10), nullable=False)
    due_date = Column(String(10))
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')  # pending, paid, overdue
    description = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")

class ARPayment(BaseModel):
    __tablename__ = "ar_payments"
    
    tenant_id = Column(GUID(), nullable=False, index=True)
    customer_id = Column(GUID(), ForeignKey('customers.id'), nullable=False)
    payment_number = Column(String(50), nullable=False)
    payment_date = Column(String(10), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50))
    reference = Column(String(100))
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")