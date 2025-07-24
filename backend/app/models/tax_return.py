from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.db.base import Base
from app.models.mixins import TimestampMixin


class TaxReturnStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    FILED = "filed"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class TaxFilingFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    AD_HOC = "ad_hoc"


class TaxReturnType(str, Enum):
    VAT = "vat"
    GST = "gst"
    SALES_TAX = "sales_tax"
    INCOME_TAX = "income_tax"
    WITHHOLDING_TAX = "withholding_tax"
    DIGITAL_SERVICES_TAX = "digital_services_tax"
    CUSTOM = "custom"


class TaxReturn(Base, TimestampMixin):
    """Model for storing tax return information"""
    __tablename__ = "tax_returns"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    return_type = Column(String(50), nullable=False)
    filing_frequency = Column(String(20), nullable=False)
    tax_period_start = Column(DateTime, nullable=False)
    tax_period_end = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    filing_date = Column(DateTime, nullable=True)
    status = Column(String(20), default=TaxReturnStatus.DRAFT, nullable=False)
    jurisdiction_code = Column(String(10), nullable=False)
    tax_authority_id = Column(String(100), nullable=True)
    
    # Financial amounts - stored as JSON to support multiple currencies
    # Format: {"USD": 1000.00, "EUR": 850.00}
    total_taxable_amount = Column(JSON, default={})
    total_tax_amount = Column(JSON, default={})
    total_paid_amount = Column(JSON, default={})
    total_due_amount = Column(JSON, default={})
    
    # Filing details
    filing_reference = Column(String(100), nullable=True)  # External reference from tax authority
    confirmation_number = Column(String(100), nullable=True)  # Confirmation/tracking number
    notes = Column(String(1000), nullable=True)  # Internal notes
    
    # Audit fields
    created_by = Column(PG_UUID(as_uuid=True), nullable=False)  # User who created the return
    approved_by = Column(PG_UUID(as_uuid=True), nullable=True)  # User who approved the return
    approved_at = Column(DateTime, nullable=True)  # When the return was approved
    filed_by = Column(PG_UUID(as_uuid=True), nullable=True)  # User who filed the return
    
    # Relationships
    line_items = relationship(
        "TaxReturnLineItem", 
        back_populates="tax_return",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    payments = relationship(
        "TaxPayment", 
        back_populates="tax_return",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    attachments = relationship(
        "TaxReturnAttachment", 
        back_populates="tax_return",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self):
        return f"<TaxReturn {self.return_type} - {self.tax_period_start.date()} to {self.tax_period_end.date()}>"


class TaxReturnLineItem(Base, TimestampMixin):
    """Line items for tax returns"""
    __tablename__ = "tax_return_line_items"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_return_id = Column(PG_UUID(as_uuid=True), ForeignKey("tax_returns.id"), nullable=False)
    line_item_code = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(JSON, nullable=False)  # {currency: amount} format
    tax_type = Column(String(50), nullable=True)
    tax_rate = Column(JSON, nullable=True)  # {rate: decimal, type: string}
    tax_amount = Column(JSON, nullable=True)  # {currency: amount} format
    
    # Relationships
    tax_return = relationship("TaxReturn", back_populates="line_items")
    
    def __repr__(self):
        return f"<TaxReturnLineItem {self.line_item_code} - {self.amount}>"
