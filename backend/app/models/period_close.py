"""
Period close models for managing accounting period closures.
"""
from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Text, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class PeriodType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PeriodStatus(str, Enum):
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"
    REOPENED = "reopened"


class CloseTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AccountingPeriod(BaseModel):
    """
    Represents an accounting period (month, quarter, year).
    """
    __tablename__ = "accounting_periods"
    
    # Period identification
    period_name = Column(String(50), nullable=False)
    period_type = Column(SQLEnum(PeriodType), nullable=False)
    
    # Period dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(PeriodStatus), nullable=False, default=PeriodStatus.OPEN)
    
    # Close information
    closed_by = Column(GUID(), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    period_closes = relationship("PeriodClose", back_populates="period")
    
    def __repr__(self) -> str:
        return f"<AccountingPeriod(id={self.id}, name='{self.period_name}', status='{self.status}')>"


class PeriodClose(BaseModel):
    """
    Represents a period close process.
    """
    __tablename__ = "period_closes"
    
    # Close identification
    close_number = Column(String(50), unique=True, index=True, nullable=False)
    period_id = Column(GUID(), ForeignKey("accounting_periods.id"), nullable=False)
    
    # Close details
    close_type = Column(SQLEnum(PeriodType), nullable=False)
    status = Column(SQLEnum(PeriodStatus), nullable=False, default=PeriodStatus.CLOSING)
    
    # Dates
    initiated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # User information
    initiated_by = Column(GUID(), nullable=False)
    completed_by = Column(GUID(), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    period = relationship("AccountingPeriod", back_populates="period_closes")
    close_tasks = relationship("PeriodCloseTask", back_populates="period_close", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<PeriodClose(id={self.id}, number='{self.close_number}', status='{self.status}')>"


class PeriodCloseTask(BaseModel):
    """
    Individual tasks within a period close process.
    """
    __tablename__ = "period_close_tasks"
    
    # Task identification
    period_close_id = Column(GUID(), ForeignKey("period_closes.id"), nullable=False)
    task_name = Column(String(100), nullable=False)
    task_description = Column(Text, nullable=True)
    
    # Task configuration
    task_order = Column(Integer, nullable=False)
    is_required = Column(Boolean, nullable=False, default=True)
    is_automated = Column(Boolean, nullable=False, default=False)
    
    # Task status
    status = Column(SQLEnum(CloseTaskStatus), nullable=False, default=CloseTaskStatus.PENDING)
    
    # Execution details
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    assigned_to = Column(GUID(), nullable=True)
    completed_by = Column(GUID(), nullable=True)
    
    # Results
    result_message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    period_close = relationship("PeriodClose", back_populates="close_tasks")
    
    def __repr__(self) -> str:
        return f"<PeriodCloseTask(id={self.id}, name='{self.task_name}', status='{self.status}')>"