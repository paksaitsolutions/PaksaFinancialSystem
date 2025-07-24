"""
Tax filing and payment models for payroll tax reporting.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Date, DateTime, Enum, ForeignKey, 
    Numeric, String, Text, Boolean, Integer, JSON
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.db.base import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class TaxFilingStatus(PyEnum):
    """Status of a tax filing."""
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    FILED = "FILED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    AMENDED = "AMENDED"
    CANCELLED = "CANCELLED"


class TaxPaymentStatus(PyEnum):
    """Status of a tax payment."""
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class TaxFiling(PayrollBase, Base):
    """Tax filing for payroll taxes."""
    __tablename__ = "payroll_tax_filings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Filing identification
    filing_reference = Column(String(50), unique=True, index=True, nullable=False)
    tax_agency_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_tax_agencies.id'), 
        nullable=False,
        index=True
    )
    
    # Filing period
    tax_year = Column(Integer, nullable=False, index=True)
    tax_period = Column(String(20), nullable=False, index=True)  # MONTHLY, QUARTERLY, ANNUAL
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    
    # Status
    status = Column(
        Enum(TaxFilingStatus, name='tax_filing_status_enum'),
        default=TaxFilingStatus.DRAFT,
        nullable=False,
        index=True
    )
    
    # Amounts
    total_taxable_wages = Column(Numeric(15, 2), default=0, nullable=False)
    total_tax_withheld = Column(Numeric(15, 2), default=0, nullable=False)
    total_employer_tax = Column(Numeric(15, 2), default=0, nullable=False)
    total_interest_penalties = Column(Numeric(15, 2), default=0, nullable=False)
    total_amount_due = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Filing details
    filing_method = Column(String(50), nullable=True)  # ELECTRONIC, PAPER, ETC.
    confirmation_number = Column(String(100), nullable=True)
    filed_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejected_reason = Column(Text, nullable=True)
    
    # Payment details
    payment_status = Column(
        Enum(TaxPaymentStatus, name='tax_payment_status_enum'),
        default=TaxPaymentStatus.PENDING,
        nullable=False,
        index=True
    )
    payment_date = Column(Date, nullable=True)
    payment_reference = Column(String(100), nullable=True)
    payment_method = Column(String(50), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    tax_agency = relationship("TaxAgency")
    tax_filing_details = relationship("TaxFilingDetail", back_populates="tax_filing", cascade="all, delete-orphan")
    tax_payments = relationship("TaxPayment", back_populates="tax_filing", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TaxFiling {self.filing_reference}: {self.tax_agency_id} ({self.tax_year} {self.tax_period})>"
    
    def calculate_totals(self):
        """Calculate total amounts for the filing."""
        self.total_taxable_wages = sum(
            detail.taxable_wages for detail in self.tax_filing_details
        )
        self.total_tax_withheld = sum(
            detail.tax_withheld for detail in self.tax_filing_details
        )
        self.total_employer_tax = sum(
            detail.employer_tax for detail in self.tax_filing_details
        )
        self.total_amount_due = (
            self.total_tax_withheld + 
            self.total_employer_tax + 
            self.total_interest_penalties
        )
    
    def mark_as_filed(self, confirmation_number=None, filed_at=None):
        """Mark the filing as filed."""
        if self.status in [TaxFilingStatus.DRAFT, TaxFilingStatus.PENDING]:
            self.status = TaxFilingStatus.FILED
            self.filed_at = filed_at or datetime.utcnow()
            self.confirmation_number = confirmation_number
    
    def mark_as_accepted(self, accepted_at=None):
        """Mark the filing as accepted."""
        if self.status == TaxFilingStatus.FILED:
            self.status = TaxFilingStatus.ACCEPTED
            self.accepted_at = accepted_at or datetime.utcnow()
    
    def mark_as_rejected(self, reason, rejected_at=None):
        """Mark the filing as rejected."""
        if self.status == TaxFilingStatus.FILED:
            self.status = TaxFilingStatus.REJECTED
            self.rejected_at = rejected_at or datetime.utcnow()
            self.rejected_reason = reason


class TaxFilingDetail(PayrollBase, Base):
    """Detailed tax information for a tax filing."""
    __tablename__ = "payroll_tax_filing_details"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Parent filing
    tax_filing_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_tax_filings.id'), 
        nullable=False,
        index=True
    )
    
    # Tax code
    tax_code_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_tax_codes.id'), 
        nullable=False,
        index=True
    )
    
    # Employee information
    employee_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=False,
        index=True
    )
    
    # Tax amounts
    taxable_wages = Column(Numeric(15, 2), default=0, nullable=False)
    tax_withheld = Column(Numeric(15, 2), default=0, nullable=False)
    employer_tax = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Withholding details
    withholding_allowances = Column(Integer, default=0, nullable=False)
    additional_withholding = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    tax_filing = relationship("TaxFiling", back_populates="tax_filing_details")
    tax_code = relationship("TaxCode")
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<TaxFilingDetail {self.tax_code_id}: {self.employee_id} ({self.taxable_wages})>"


class TaxPayment(PayrollBase, Base):
    """Tax payment for a tax filing."""
    __tablename__ = "payroll_tax_payments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Parent filing
    tax_filing_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_tax_filings.id'), 
        nullable=False,
        index=True
    )
    
    # Payment details
    payment_reference = Column(String(50), unique=True, index=True, nullable=False)
    payment_date = Column(Date, nullable=False, index=True)
    payment_method = Column(String(50), nullable=False)  # EFT, CHECK, WIRE, etc.
    payment_status = Column(
        Enum(TaxPaymentStatus, name='tax_payment_status_enum'),
        default=TaxPaymentStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Amounts
    amount = Column(Numeric(15, 2), nullable=False)
    fee_amount = Column(Numeric(15, 2), default=0, nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Bank details
    bank_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_bank_accounts.id'), 
        nullable=True,
        index=True
    )
    
    # Processing
    processed_at = Column(DateTime, nullable=True)
    confirmation_number = Column(String(100), nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # GL posting
    gl_journal_entry_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_journal_entries.id'), 
        nullable=True,
        index=True
    )
    
    # Metadata
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    tax_filing = relationship("TaxFiling", back_populates="tax_payments")
    bank_account = relationship("BankAccount")
    gl_journal_entry = relationship("JournalEntry")
    
    def __repr__(self):
        return f"<TaxPayment {self.payment_reference}: {self.amount} ({self.payment_status})>"
    
    def calculate_totals(self):
        """Calculate total amount including fees."""
        self.total_amount = self.amount + (self.fee_amount or 0)
    
    def mark_as_processing(self, processed_at=None):
        """Mark the payment as processing."""
        if self.payment_status == TaxPaymentStatus.PENDING:
            self.payment_status = TaxPaymentStatus.PROCESSING
            self.processed_at = processed_at or datetime.utcnow()
    
    def mark_as_paid(self, confirmation_number=None, processed_at=None):
        """Mark the payment as paid."""
        if self.payment_status in [TaxPaymentStatus.PENDING, TaxPaymentStatus.PROCESSING]:
            self.payment_status = TaxPaymentStatus.PAID
            self.processed_at = processed_at or datetime.utcnow()
            self.confirmation_number = confirmation_number
    
    def mark_as_failed(self, reason, processed_at=None):
        """Mark the payment as failed."""
        if self.payment_status in [TaxPaymentStatus.PENDING, TaxPaymentStatus.PROCESSING]:
            self.payment_status = TaxPaymentStatus.FAILED
            self.processed_at = processed_at or datetime.utcnow()
            self.failure_reason = reason
