from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.db.base import Base
from app.models.mixins import TimestampMixin


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class TaxPayment(Base, TimestampMixin):
    """Model for tracking tax payments"""
    __tablename__ = "tax_payments"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_return_id = Column(PG_UUID(as_uuid=True), ForeignKey("tax_returns.id"), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    payment_method = Column(String(50), nullable=False)  # bank_transfer, credit_card, etc.
    reference_number = Column(String(100), nullable=True)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    notes = Column(String(500), nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), nullable=False)
    
    # Relationships
    tax_return = relationship("TaxReturn", back_populates="payments")
    
    def __repr__(self):
        return f"<TaxPayment {self.amount} {self.currency} - {self.status}>"


__all__ = ["TaxPayment", "PaymentStatus"]
