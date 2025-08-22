"""
Paksa Financial System 
GL Period Model

This module defines the GL Period model for managing accounting periods.
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Boolean, ForeignKey, 
    DateTime, Date, Enum as SQLEnum, Text, JSON, CheckConstraint,
    UniqueConstraint, Index, func
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, validates

<<<<<<< HEAD:backend/app/modules/core_financials/accounting/models/gl_period.py
from app.db.base_class import Base
=======
from app.core.db.base import Base
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91:backend/app/models/gl_period.py


class GLPeriodStatus(str, Enum):
    """Status of a GL period."""
    OPEN = 'open'
    CLOSED = 'closed'
    PERMANENTLY_CLOSED = 'permanently_closed'
    FUTURE = 'future'


class GLPeriod(Base):
    """
    Represents an accounting period in the general ledger.
    """
    __tablename__ = 'gl_periods'
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Period Identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Period Dates
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    # Status
    status = Column(SQLEnum(GLPeriodStatus), default=GLPeriodStatus.OPEN, nullable=False, index=True)
    is_adjusting_period = Column(Boolean, default=False, nullable=False)
    
    # Closing Information
    closed_at = Column(DateTime(timezone=True), nullable=True)
    closed_by = Column(PG_UUID(as_uuid=True), nullable=True)
    
    # Parent Period (for year/quarter relationships)
    parent_period_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_periods.id', ondelete='SET NULL'), nullable=True)
    
    # Fiscal Year Information
    fiscal_year = Column(String(10), nullable=False, index=True)  # e.g., 'FY2023'
    period_number = Column(Integer, nullable=False)  # 1-12 for monthly, 1-4 for quarterly
    
    # Metadata
    metadata_ = Column('metadata', JSONB, nullable=True, default=dict)
    
    # Audit Fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=False)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=False)
    
    # Relationships
    journal_entries = relationship('JournalEntry', back_populates='period')
    parent_period = relationship('GLPeriod', remote_side=[id], back_populates='child_periods')
    child_periods = relationship('GLPeriod', back_populates='parent_period')
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('fiscal_year', 'period_number', name='uq_gl_periods_fiscal_year_period'),
        CheckConstraint('end_date >= start_date', name='check_period_dates_valid'),
        Index('ix_gl_periods_date_range', 'start_date', 'end_date'),
        Index('ix_gl_periods_fiscal_year', 'fiscal_year'),
    )
    
    @validates('start_date', 'end_date')
    def validate_dates(self, key: str, value: date) -> date:
        """Validate period dates."""
        if key == 'end_date' and hasattr(self, 'start_date') and value < self.start_date:
            raise ValueError("End date cannot be before start date")
        return value
    
    @validates('status')
    def validate_status(self, key: str, value: GLPeriodStatus) -> GLPeriodStatus:
        """Validate period status transitions."""
        if hasattr(self, 'status') and self.status == GLPeriodStatus.PERMANENTLY_CLOSED:
            raise ValueError("Cannot modify a permanently closed period")
        return value
    
    @property
    def is_open(self) -> bool:
        """Check if the period is open for posting."""
        return self.status == GLPeriodStatus.OPEN
    
    @property
    def is_closed(self) -> bool:
        """Check if the period is closed."""
        return self.status in (GLPeriodStatus.CLOSED, GLPeriodStatus.PERMANENTLY_CLOSED)
    
    def close(self, user_id: UUID, permanent: bool = False) -> None:
        """
        Close the period.
        
        Args:
            user_id: ID of the user performing the close
            permanent: If True, permanently close the period (cannot be reopened)
        """
        if self.is_closed and not permanent:
            raise ValueError("Period is already closed")
            
        if permanent:
            self.status = GLPeriodStatus.PERMANENTLY_CLOSED
        else:
            self.status = GLPeriodStatus.CLOSED
            
        self.closed_at = datetime.utcnow()
        self.closed_by = user_id
    
    def reopen(self, user_id: UUID) -> None:
        """
        Reopen a closed period.
        
        Args:
            user_id: ID of the user performing the reopen
            
        Raises:
            ValueError: If the period is permanently closed or already open
        """
        if self.status == GLPeriodStatus.PERMANENTLY_CLOSED:
            raise ValueError("Cannot reopen a permanently closed period")
            
        if self.status == GLPeriodStatus.OPEN:
            raise ValueError("Period is already open")
            
        self.status = GLPeriodStatus.OPEN
        self.closed_at = None
        self.closed_by = None
    
    def contains_date(self, date_to_check: date) -> bool:
        """
        Check if the given date falls within this period.
        
        Args:
            date_to_check: The date to check
            
        Returns:
            bool: True if the date is within the period, False otherwise
        """
        return self.start_date <= date_to_check <= self.end_date
    
    def __repr__(self) -> str:
        return f"<GLPeriod(id={self.id}, name='{self.name}', " \
               f"{self.start_date} to {self.end_date}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert GL period to dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status.value,
            'is_adjusting_period': self.is_adjusting_period,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'closed_by': str(self.closed_by) if self.closed_by else None,
            'parent_period_id': str(self.parent_period_id) if self.parent_period_id else None,
            'fiscal_year': self.fiscal_year,
            'period_number': self.period_number,
            'is_open': self.is_open,
            'is_closed': self.is_closed,
            'metadata': self.metadata_ or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
        }
