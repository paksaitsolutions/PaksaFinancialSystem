"""
Accounts Payable Database Models
"""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SQLEnum, 
    ForeignKey, Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from core.database import Base


class BillStatus(str, Enum):
    DRAFT = "draft"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CANCELLED = "cancelled"
    VOID = "void"


class PaymentMethod(str, Enum):
    CHECK = "check"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    OTHER = "other"


class Bill(Base):
    """
    Represents a vendor bill in the Accounts Payable system.
    """
    __tablename__ = "ap_bills"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    bill_number = Column(String(50), unique=True, index=True, nullable=False)
    vendor_id = Column(PG_UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    bill_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    reference = Column(String(100))
    terms = Column(String(100))
    status = Column(SQLEnum(BillStatus), default=BillStatus.DRAFT, nullable=False)
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    amount_paid = Column(Numeric(15, 2), nullable=False, default=0)
    balance_due = Column(Numeric(15, 2), nullable=False, default=0)
    notes = Column(Text)
    journal_entry_id = Column(PG_UUID(as_uuid=True), ForeignKey("journal_entries.id"), index=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="bills")
    items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="bill")
    journal_entry = relationship("JournalEntry")
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    
    __table_args__ = (
        UniqueConstraint('bill_number', name='uq_ap_bills_bill_number'),
    )
    
    def __repr__(self):
        return f"<Bill {self.bill_number} - {self.vendor.name} - {self.total_amount}>"


class BillItem(Base):
    """
    Line items for a vendor bill.
    """
    __tablename__ = "ap_bill_items"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    bill_id = Column(PG_UUID(as_uuid=True), ForeignKey("ap_bills.id"), nullable=False)
    account_id = Column(PG_UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"), nullable=False)
    item_description = Column(Text, nullable=False)
    quantity = Column(Numeric(15, 6), nullable=False, default=1)
    unit_price = Column(Numeric(15, 6), nullable=False)
    tax_rate = Column(Numeric(5, 4), default=0)  # 0.05 for 5%
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_percent = Column(Numeric(5, 2), default=0)  # 10.00 for 10%
    discount_amount = Column(Numeric(15, 2), default=0)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    bill = relationship("Bill", back_populates="items")
    account = relationship("ChartOfAccounts")
    
    def __repr__(self):
        return f"<BillItem {self.item_description} - {self.amount}>"


class Payment(Base):
    """
    Represents a payment made against a vendor bill.
    """
    __tablename__ = "ap_payments"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    payment_number = Column(String(50), unique=True, index=True, nullable=False)
    bill_id = Column(PG_UUID(as_uuid=True), ForeignKey("ap_bills.id"), nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    reference = Column(String(100))
    amount = Column(Numeric(15, 2), nullable=False)
    notes = Column(Text)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_at = Column(DateTime)
    journal_entry_id = Column(PG_UUID(as_uuid=True), ForeignKey("journal_entries.id"), index=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    bill = relationship("Bill", back_populates="payments")
    journal_entry = relationship("JournalEntry")
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    
    __table_args__ = (
        UniqueConstraint('payment_number', name='uq_ap_payments_payment_number'),
    )
    
    def __repr__(self):
        return f"<Payment {self.payment_number} - {self.amount} - {self.payment_date}>"
