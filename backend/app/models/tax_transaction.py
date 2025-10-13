"""
Tax Transaction Models.

This module contains models for tracking tax transactions and their components.
"""
from enum import Enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, Index, Enum as SQLAEnum
from app.models.base import GUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin

class TaxTransactionStatus(str, Enum):
    """Status of a tax transaction."""
    DRAFT = "draft"
    POSTED = "posted"
    VOIDED = "voided"
    ADJUSTED = "adjusted"


class TaxTransactionType(str, Enum):
    """Type of tax transaction."""
    SALE = "sale"
    PURCHASE = "purchase"
    USE = "use"
    IMPORT = "import"
    EXPORT = "export"
    TAX_ADJUSTMENT = "tax_adjustment"

class TaxTransaction(Base, TimestampMixin, SoftDeleteMixin):
    """Stores all tax-related transactions with detailed breakdown"""
    __tablename__ = "tax_transactions"

    id = Column(GUID(), primary_key=True, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    posting_date = Column(DateTime, nullable=True, index=True)
    document_number = Column(String(100), index=True, nullable=False)
    reference_number = Column(String(100), index=True)
    
    # Relationships
    company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="tax_transactions")
    
    # Tax details
    tax_type = Column(String(50), nullable=False, index=True)
    tax_rate_id = Column(GUID(), ForeignKey("tax_rates.id"), nullable=False)
    tax_rate_rel = relationship("TaxRate", viewonly=True)
    
    # Amounts
    taxable_amount = Column(Numeric(19, 4), nullable=False, default=0)
    tax_amount = Column(Numeric(19, 4), nullable=False, default=0)
    total_amount = Column(Numeric(19, 4), nullable=False, default=0)
    
    # Jurisdiction
    jurisdiction_code = Column(String(20), index=True)
    tax_jurisdiction_id = Column(GUID(), ForeignKey("tax_jurisdictions.id"))
    tax_jurisdiction = relationship("TaxJurisdiction")
    
    # Status and type
    status = Column(Enum(TaxTransactionStatus), default=TaxTransactionStatus.DRAFT, index=True)
    transaction_type = Column(Enum(TaxTransactionType), nullable=False, index=True)
    
    # Related documents
    source_document_type = Column(String(50))  # e.g., 'invoice', 'bill', 'journal_entry'
    source_document_id = Column(GUID(), index=True)
    
    # Audit fields
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    posted_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    posted_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    tax_components = relationship("TaxTransactionComponent", back_populates="transaction", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_transactions_company_dates', 'company_id', 'transaction_date', 'posting_date'),
        Index('idx_tax_transactions_source', 'source_document_type', 'source_document_id'),
        Index('idx_tax_transactions_status_type', 'status', 'transaction_type'),
    )

class TaxTransactionComponent(Base, TimestampMixin):
    """Stores detailed tax components for each transaction"""
    __tablename__ = "tax_transaction_components"
    
    id = Column(GUID(), primary_key=True, index=True)
    transaction_id = Column(GUID(), ForeignKey("tax_transactions.id"), nullable=False)
    
    # Tax component details
    tax_component = Column(String(100), nullable=False)  # e.g., 'State Tax', 'County Tax', 'Special District Tax'
    tax_rate = Column(Numeric(10, 6), nullable=False)  # Effective rate for this component
    taxable_amount = Column(Numeric(19, 4), nullable=False)
    tax_amount = Column(Numeric(19, 4), nullable=False)
    
    # Jurisdiction details
    jurisdiction_level = Column(String(50))  # e.g., 'state', 'county', 'city', 'special'
    jurisdiction_name = Column(String(100))
    jurisdiction_code = Column(String(20), index=True)
    
    # Relationships
    transaction = relationship("TaxTransaction", back_populates="tax_components")
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_components_transaction', 'transaction_id'),
        Index('idx_tax_components_jurisdiction', 'jurisdiction_code'),
    )
