import uuid
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Column, DateTime, Enum as SQLEnum, ForeignKey, Numeric, String, Text, Date, func
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base

# Enum for Bill Status
class BillStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"  # Waiting for approval
    APPROVED = "APPROVED"    # Approved for payment
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    VOID = "VOID"

# Enum for Payment Status
class PaymentStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Vendor(Base):
    __tablename__ = 'ap_vendors'
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    address: Mapped[Optional[str]] = mapped_column(Text)
    tax_id: Mapped[Optional[str]] = mapped_column(String(100))
    default_currency: Mapped[str] = mapped_column(String(3), nullable=False, default='USD')
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    bills: Mapped[List["Bill"]] = relationship(back_populates="vendor")
    payments: Mapped[List["Payment"]] = relationship(back_populates="vendor")

class Bill(Base):
    __tablename__ = 'ap_bills'
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('ap_vendors.id'), nullable=False)
    bill_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0.0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='USD')
    status: Mapped[BillStatus] = mapped_column(SQLEnum(BillStatus), nullable=False, default=BillStatus.DRAFT)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    vendor: Mapped["Vendor"] = relationship(back_populates="bills")
    line_items: Mapped[List["BillLineItem"]] = relationship(back_populates="bill", cascade="all, delete-orphan")
    payment_allocations: Mapped[List["PaymentAllocation"]] = relationship(back_populates="bill")

class BillLineItem(Base):
    __tablename__ = 'ap_bill_line_items'
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('ap_bills.id'), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(String(50), nullable=False)  # Simplified for now
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)

    bill: Mapped["Bill"] = relationship(back_populates="line_items")

class Payment(Base):
    __tablename__ = 'ap_payments_new'  # Changed to avoid conflicts
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('ap_vendors.id'), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='USD')
    payment_method: Mapped[Optional[str]] = mapped_column(String(100))
    reference_number: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    vendor: Mapped["Vendor"] = relationship(back_populates="payments")
    allocations: Mapped[List["PaymentAllocation"]] = relationship(back_populates="payment", cascade="all, delete-orphan")

class PaymentAllocation(Base):
    __tablename__ = 'ap_payment_allocations'
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('ap_payments_new.id'), nullable=False)
    bill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('ap_bills.id'), nullable=False)
    amount_allocated: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)

    payment: Mapped["Payment"] = relationship(back_populates="allocations")
    bill: Mapped["Bill"] = relationship(back_populates="payment_allocations")