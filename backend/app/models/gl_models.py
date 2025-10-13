"""
Enhanced General Ledger models with enterprise features.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, Numeric
from app.models.base import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import DECIMAL as Decimal
from datetime import datetime
import uuid
from app.core.database import Base

# Import unified models from core_models
from app.models.core_models import ChartOfAccounts, JournalEntry, JournalEntryLine

# Create aliases for compatibility
GLChartOfAccounts = ChartOfAccounts


class AccountingPeriod(Base):
    """Accounting periods for period-end closing."""
    
    __tablename__ = "accounting_periods"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(255), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    status = Column(String(20), default="open")  # open, closed, locked
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    closed_at = Column(DateTime)
    closed_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


class LedgerBalance(Base):
    """Account balances by period for performance."""
    
    __tablename__ = "ledger_balances"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=False)
    opening_balance = Column(Decimal(15, 2), default=0)
    debit_total = Column(Decimal(15, 2), default=0)
    credit_total = Column(Decimal(15, 2), default=0)
    closing_balance = Column(Decimal(15, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrialBalance(Base):
    """Trial Balance snapshots."""
    
    __tablename__ = "trial_balances"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(255), nullable=False, index=True)
    as_of_date = Column(DateTime, nullable=False)
    total_debits = Column(Decimal(15, 2), nullable=False)
    total_credits = Column(Decimal(15, 2), nullable=False)
    is_balanced = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255), nullable=False)
    
    # Relationships
    accounts = relationship("TrialBalanceAccount", back_populates="trial_balance", cascade="all, delete-orphan")


class TrialBalanceAccount(Base):
    """Trial Balance account details."""
    
    __tablename__ = "trial_balance_accounts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    trial_balance_id = Column(GUID(), ForeignKey("trial_balances.id"), nullable=False)
    account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    account_code = Column(String(20), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)
    debit_amount = Column(Decimal(15, 2), default=0)
    credit_amount = Column(Decimal(15, 2), default=0)
    balance = Column(Decimal(15, 2), default=0)
    
    # Relationships
    trial_balance = relationship("TrialBalance", back_populates="accounts")


class FinancialStatement(Base):
    """Financial Statement templates and generated reports."""
    
    __tablename__ = "financial_statements"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(255), nullable=False, index=True)
    statement_type = Column(String(50), nullable=False)  # balance_sheet, income_statement, cash_flow
    statement_name = Column(String(255), nullable=False)
    as_of_date = Column(DateTime, nullable=False)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    data = Column(Text)  # JSON data of the statement
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255), nullable=False)
    
    # Relationships
    lines = relationship("FinancialStatementLine", back_populates="statement", cascade="all, delete-orphan")


class FinancialStatementLine(Base):
    """Financial Statement line items."""
    
    __tablename__ = "financial_statement_lines"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    statement_id = Column(GUID(), ForeignKey("financial_statements.id"), nullable=False)
    account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"))
    line_number = Column(Integer)
    description = Column(String(255), nullable=False)
    amount = Column(Decimal(15, 2), default=0)
    is_total = Column(Boolean, default=False)
    parent_line_id = Column(GUID(), ForeignKey("financial_statement_lines.id"))
    
    # Relationships
    statement = relationship("FinancialStatement", back_populates="lines")
    parent_line = relationship("FinancialStatementLine", remote_side=[id])


class BudgetEntry(Base):
    """Budget entries for comparison with actuals."""
    
    __tablename__ = "budget_entries"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(255), nullable=False, index=True)
    account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    budget_year = Column(Integer, nullable=False)
    budget_month = Column(Integer, nullable=False)
    budgeted_amount = Column(Decimal(15, 2), nullable=False)
    actual_amount = Column(Decimal(15, 2), default=0)
    variance = Column(Decimal(15, 2), default=0)
    variance_percent = Column(Decimal(5, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AccountType(Base):
    """Account types configuration."""
    
    __tablename__ = "account_types"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    type_name = Column(String(100), nullable=False)
    type_code = Column(String(20), nullable=False, unique=True)
    normal_balance = Column(String(10), nullable=False)  # debit or credit
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccountSubType(Base):
    """Account subtypes configuration."""
    
    __tablename__ = "account_subtypes"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    subtype_name = Column(String(100), nullable=False)
    subtype_code = Column(String(20), nullable=False, unique=True)
    account_type_id = Column(GUID(), ForeignKey("account_types.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccountStatus(Base):
    """Account status configuration."""
    
    __tablename__ = "account_statuses"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    status_name = Column(String(50), nullable=False)
    status_code = Column(String(20), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class JournalEntryStatus(Base):
    """Journal entry status configuration."""
    
    __tablename__ = "journal_entry_statuses"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    status_name = Column(String(50), nullable=False)
    status_code = Column(String(20), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class FinancialStatementSection(Base):
    """Financial Statement sections for grouping."""
    
    __tablename__ = "financial_statement_sections"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    statement_id = Column(GUID(), ForeignKey("financial_statements.id"), nullable=False)
    section_name = Column(String(255), nullable=False)
    section_order = Column(Integer, default=0)
    is_total_section = Column(Boolean, default=False)
    
    # Relationships
    statement = relationship("FinancialStatement")


class FinancialStatementType(Base):
    """Financial Statement types configuration."""
    
    __tablename__ = "financial_statement_types"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    type_name = Column(String(100), nullable=False)
    type_code = Column(String(20), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)