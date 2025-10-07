from sqlalchemy import Column, String, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Vendor(BaseModel):
    __tablename__ = "vendors"
    __table_args__ = {'extend_existing': True}
    
    tenant_id = Column(String, nullable=False, index=True)
    vendor_code = Column(String(20), nullable=False, unique=True)
    vendor_name = Column(String(200), nullable=False)
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
    invoices = relationship("APInvoice", back_populates="vendor")
    payments = relationship("APPayment", back_populates="vendor")

class APInvoice(BaseModel):
    __tablename__ = "ap_invoices"
    __table_args__ = {'extend_existing': True}
    
    tenant_id = Column(String, nullable=False, index=True)
    vendor_id = Column(String, ForeignKey('vendors.id'), nullable=False)
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(String(10), nullable=False)
    due_date = Column(String(10))
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')  # pending, approved, paid
    description = Column(Text)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")

class APPayment(BaseModel):
    __tablename__ = "ap_payments"
    __table_args__ = {'extend_existing': True}
    
    tenant_id = Column(String, nullable=False, index=True)
    vendor_id = Column(String, ForeignKey('vendors.id'), nullable=False)
    payment_number = Column(String(50), nullable=False)
    payment_date = Column(String(10), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50))
    reference = Column(String(100))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="payments")