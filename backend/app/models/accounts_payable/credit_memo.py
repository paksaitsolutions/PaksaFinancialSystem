"""
Credit memo model for Accounts Payable module.
"""
import uuid
from datetime import date
from typing import Optional
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import CreditMemoStatus

class APCreditMemo(Base):
    """Credit memo model for Accounts Payable."""
    
    __tablename__ = "ap_credit_memo"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credit_memo_number = Column(String(50), nullable=False, index=True, unique=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False, index=True)
    
    # Credit memo details
    credit_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    description = Column(Text)
    reference = Column(String(100))
    
    # Status and tracking
    status = Column(Enum(CreditMemoStatus), default=CreditMemoStatus.ACTIVE, nullable=False, index=True)
    applied_amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    remaining_amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    
    # Original invoice reference (if applicable)
    original_invoice_id = Column(UUID(as_uuid=True), ForeignKey("ap_invoice.id"))
    
    # Relationships
    vendor = relationship("Vendor")
    original_invoice = relationship("APInvoice")
    applications = relationship("APCreditApplication", back_populates="credit_memo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<APCreditMemo {self.credit_memo_number}: {self.amount}>"


class APCreditApplication(Base):
    """Credit application to invoices."""
    
    __tablename__ = "ap_credit_application"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credit_memo_id = Column(UUID(as_uuid=True), ForeignKey("ap_credit_memo.id"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("ap_invoice.id"), nullable=False)
    
    # Application details
    application_date = Column(Date, nullable=False, default=date.today)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    notes = Column(Text)
    
    # Relationships
    credit_memo = relationship("APCreditMemo", back_populates="applications")
    invoice = relationship("APInvoice")
    
    def __repr__(self):
        return f"<APCreditApplication: {self.amount}>"