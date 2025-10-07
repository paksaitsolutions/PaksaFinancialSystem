"""
Payment model for Accounts Payable module.
"""
import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import Column, String, ForeignKey, Text, Date, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import PaymentStatus, PaymentMethod

class APPayment(Base):
    """Payment model for Accounts Payable."""
    
    __tablename__ = "ap_payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_number = Column(String(50), nullable=False, index=True, unique=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False, index=True)
    
    # Payment details
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    reference = Column(String(100))
    memo = Column(Text)
    
    # Status
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    
    # Relationships
    vendor = relationship("Vendor")
    invoices = relationship("APInvoice", secondary="ap_invoice_payment", back_populates="payments")
    invoice_payments = relationship("APInvoicePayment", back_populates="payment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<APPayment {self.payment_number}: {self.amount}>"