"""
Budget Module - Database Models
"""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, Numeric, ForeignKey, Date, DateTime, Boolean, Enum as SQLEnum, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base

class BudgetFrequency(str, Enum):
    """Budget frequency options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    BIANNUAL = "bi_annual"
    ANNUAL = "annual"
    CUSTOM = "custom"

class BudgetStatus(str, Enum):
    """Budget status options"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class BudgetType(str, Enum):
    """Budget type options"""
    OPERATING = "operating"
    CAPITAL = "capital"
    REVENUE = "revenue"
    EXPENSE = "expense"
    PROJECT = "project"
    DEPARTMENT = "department"

class Budget(Base):
    """Budget model for financial planning"""
    __tablename__ = "budgets"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    frequency = Column(SQLEnum(BudgetFrequency), nullable=False, default=BudgetFrequency.MONTHLY)
    status = Column(SQLEnum(BudgetStatus), nullable=False, default=BudgetStatus.DRAFT)
    budget_type = Column(SQLEnum(BudgetType), nullable=False, default=BudgetType.OPERATING)
    currency = Column(String(3), default="USD", nullable=False)
    total_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    variance = Column(Numeric(15, 2), default=0.00, nullable=False)
    notes = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    department_id = Column(PG_UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    budget_items = relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")
    adjustments = relationship("BudgetAdjustment", back_populates="budget", cascade="all, delete-orphan")
    department = relationship("Department", back_populates="budgets")
    project = relationship("Project", back_populates="budgets")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    __table_args__ = (
        CheckConstraint('end_date > start_date', name='check_budget_dates'),
    )

class BudgetItem(Base):
    """Individual line items within a budget"""
    __tablename__ = "budget_items"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    budget_id = Column(PG_UUID(as_uuid=True), ForeignKey("budgets.id"), nullable=False)
    gl_account_id = Column(PG_UUID(as_uuid=True), ForeignKey("gl_accounts.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    variance = Column(Numeric(15, 2), default=0.00, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    budget = relationship("Budget", back_populates="budget_items")
    gl_account = relationship("GLAccount")
    transactions = relationship("BudgetTransaction", back_populates="budget_item")

class BudgetAdjustment(Base):
    """Tracks adjustments made to a budget"""
    __tablename__ = "budget_adjustments"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    budget_id = Column(PG_UUID(as_uuid=True), ForeignKey("budgets.id"), nullable=False)
    adjustment_date = Column(Date, nullable=False, default=date.today)
    amount = Column(Numeric(15, 2), nullable=False)
    previous_amount = Column(Numeric(15, 2), nullable=False)
    reason = Column(Text, nullable=False)
    adjusted_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    budget = relationship("Budget", back_populates="adjustments")
    adjusted_by_user = relationship("User")

class BudgetTransaction(Base):
    """Tracks actual transactions against budget items"""
    __tablename__ = "budget_transactions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    budget_item_id = Column(PG_UUID(as_uuid=True), ForeignKey("budget_items.id"), nullable=False)
    transaction_date = Column(Date, nullable=False, default=date.today)
    amount = Column(Numeric(15, 2), nullable=False)
    reference_type = Column(String(50), nullable=True)  # e.g., 'invoice', 'expense', 'journal', etc.
    reference_id = Column(String(100), nullable=True)   # ID of the referenced document
    description = Column(Text, nullable=True)
    
    # Relationships
    budget_item = relationship("BudgetItem", back_populates="transactions")

class BudgetVersion(Base):
    """Tracks different versions of a budget"""
    __tablename__ = "budget_versions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    budget_id = Column(PG_UUID(as_uuid=True), ForeignKey("budgets.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    is_current = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    budget = relationship("Budget")
    creator = relationship("User")
    
    __table_args__ = (
        CheckConstraint('version_number > 0', name='check_version_positive'),
    )
