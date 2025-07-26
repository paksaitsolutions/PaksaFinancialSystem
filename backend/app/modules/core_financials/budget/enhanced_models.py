import enum
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Date, DateTime, Boolean, ForeignKey, Index, 
    Enum as SQLEnum, JSON as JSONB, func, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from app.core.base import Base

class BudgetType(str, enum.Enum):
    OPERATIONAL = "operational"
    CAPITAL = "capital"
    PROJECT = "project"
    DEPARTMENT = "department"
    MASTER = "master"

class BudgetStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    ARCHIVED = "archived"

class BudgetPeriod(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    CUSTOM = "custom"

class AlertType(str, enum.Enum):
    OVERSPEND = "overspend"
    UNDERSPEND = "underspend"
    VARIANCE = "variance"
    APPROVAL_REQUIRED = "approval_required"

class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    budget_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Budget Classification
    budget_type = Column(SQLEnum(BudgetType, name="budget_type_enum"), nullable=False, index=True)
    status = Column(SQLEnum(BudgetStatus, name="budget_status_enum"), default=BudgetStatus.DRAFT, index=True)
    period_type = Column(SQLEnum(BudgetPeriod, name="budget_period_enum"), nullable=False)
    
    # Financial Information
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    currency_code = Column(String(3), default='USD')
    
    # Period Information
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False, index=True)
    
    # Version Control
    version_number = Column(String(20), default="1.0", index=True)
    parent_budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="SET NULL"), index=True)
    is_current_version = Column(Boolean, default=True, index=True)
    
    # Approval Workflow
    submitted_at = Column(DateTime(timezone=True))
    submitted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    rejected_at = Column(DateTime(timezone=True))
    rejected_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approval_notes = Column(Text)
    rejection_reason = Column(Text)
    
    # Department/Project Association
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id", ondelete="SET NULL"), index=True)
    
    # Template Information
    is_template = Column(Boolean, default=False, index=True)
    template_name = Column(String(255))
    template_category = Column(String(100))
    
    # Consolidation
    is_consolidated = Column(Boolean, default=False, index=True)
    consolidation_level = Column(String(50))  # department, division, company
    
    # Additional Information
    notes = Column(Text)
    tags = Column(JSONB)
    custom_fields = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    line_items = relationship("BudgetLineItem", back_populates="budget", cascade="all, delete-orphan")
    versions = relationship("Budget", remote_side=[id], backref="parent_budget")
    allocations = relationship("BudgetAllocation", back_populates="budget", cascade="all, delete-orphan")
    alerts = relationship("BudgetAlert", back_populates="budget", cascade="all, delete-orphan")
    actuals = relationship("BudgetActual", back_populates="budget", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_budget_type_status', 'budget_type', 'status'),
        Index('idx_budget_period', 'start_date', 'end_date'),
        Index('idx_budget_version', 'parent_budget_id', 'version_number'),
        Index('idx_budget_fiscal_year', 'fiscal_year'),
    )

class BudgetLineItem(Base):
    __tablename__ = "budget_line_items"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    line_number = Column(Integer, nullable=False)
    
    # Item Details
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100))
    description = Column(Text, nullable=False)
    
    # Financial Information
    budgeted_amount = Column(Numeric(15, 2), nullable=False)
    currency_code = Column(String(3), default='USD')
    
    # GL Integration
    gl_account_id = Column(Integer, ForeignKey("gl_accounts.id", ondelete="SET NULL"), index=True)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id", ondelete="SET NULL"), index=True)
    
    # Period Breakdown
    monthly_breakdown = Column(JSONB)  # Store monthly amounts
    quarterly_breakdown = Column(JSONB)  # Store quarterly amounts
    
    # Additional Information
    notes = Column(Text)
    justification = Column(Text)
    priority_level = Column(String(20), default="medium")
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    budget = relationship("Budget", back_populates="line_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_budget_line_budget_number', 'budget_id', 'line_number', unique=True),
        Index('idx_budget_line_category', 'category'),
        Index('idx_budget_line_gl_account', 'gl_account_id'),
    )

class BudgetAllocation(Base):
    __tablename__ = "budget_allocations"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Allocation Details
    allocation_date = Column(Date, nullable=False, index=True)
    allocated_amount = Column(Numeric(15, 2), nullable=False)
    remaining_amount = Column(Numeric(15, 2), nullable=False)
    
    # Allocation Target
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id", ondelete="SET NULL"), index=True)
    
    # Additional Information
    purpose = Column(Text)
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    budget = relationship("Budget", back_populates="allocations")
    
    # Indexes
    __table_args__ = (
        Index('idx_allocation_budget_date', 'budget_id', 'allocation_date'),
        Index('idx_allocation_department', 'department_id'),
    )

class BudgetActual(Base):
    __tablename__ = "budget_actuals"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Actual Data
    period_date = Column(Date, nullable=False, index=True)
    actual_amount = Column(Numeric(15, 2), nullable=False)
    variance_amount = Column(Numeric(15, 2), default=0)
    variance_percentage = Column(Numeric(5, 2), default=0)
    
    # Source Information
    source_type = Column(String(50), nullable=False)  # gl_transaction, manual_entry, import
    source_reference = Column(String(255))
    gl_account_id = Column(Integer, ForeignKey("gl_accounts.id", ondelete="SET NULL"), index=True)
    
    # Additional Information
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    budget = relationship("Budget", back_populates="actuals")
    
    # Indexes
    __table_args__ = (
        Index('idx_actual_budget_period', 'budget_id', 'period_date'),
        Index('idx_actual_gl_account', 'gl_account_id'),
    )

class BudgetAlert(Base):
    __tablename__ = "budget_alerts"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Alert Details
    alert_type = Column(SQLEnum(AlertType, name="alert_type_enum"), nullable=False, index=True)
    severity = Column(SQLEnum(AlertSeverity, name="alert_severity_enum"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Threshold Information
    threshold_percentage = Column(Numeric(5, 2))
    threshold_amount = Column(Numeric(15, 2))
    current_percentage = Column(Numeric(5, 2))
    current_amount = Column(Numeric(15, 2))
    
    # Status and Processing
    is_active = Column(Boolean, default=True, index=True)
    is_acknowledged = Column(Boolean, default=False, index=True)
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime(timezone=True))
    recipients = Column(JSONB)  # List of user IDs or email addresses
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    budget = relationship("Budget", back_populates="alerts")
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_budget_type', 'budget_id', 'alert_type'),
        Index('idx_alert_severity_active', 'severity', 'is_active'),
        Index('idx_alert_created', 'created_at'),
    )

class BudgetTemplate(Base):
    __tablename__ = "budget_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(255), nullable=False, index=True)
    template_category = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    
    # Template Configuration
    budget_type = Column(SQLEnum(BudgetType, name="template_budget_type_enum"), nullable=False)
    period_type = Column(SQLEnum(BudgetPeriod, name="template_period_enum"), nullable=False)
    
    # Template Data
    template_data = Column(JSONB, nullable=False)  # Store template structure
    default_values = Column(JSONB)  # Store default values
    
    # Usage Information
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_public = Column(Boolean, default=False, index=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Indexes
    __table_args__ = (
        Index('idx_template_category_active', 'template_category', 'is_active'),
        Index('idx_template_type', 'budget_type'),
    )