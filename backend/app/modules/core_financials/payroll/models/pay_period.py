"""
Pay Period models for the Payroll module.
"""
from datetime import date, datetime
from sqlalchemy import Column, Date, Enum, ForeignKey, String, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class PayPeriod(PayrollBase, Base):
    """Pay Period model representing a specific time period for payroll processing."""
    __tablename__ = "payroll_pay_periods"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Pay period identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Date range
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    
    # Pay period type (weekly, bi-weekly, semi-monthly, monthly)
    period_type = Column(
        Enum('WEEKLY', 'BI_WEEKLY', 'SEMI_MONTHLY', 'MONTHLY', name='pay_period_type_enum'),
        nullable=False
    )
    
    # Status tracking
    status = Column(
        Enum('DRAFT', 'OPEN', 'PROCESSING', 'PROCESSED', 'PAID', 'CLOSED', 'CANCELLED', 
             name='pay_period_status_enum'),
        default='DRAFT',
        nullable=False,
        index=True
    )
    
    # Financial year/period reference
    fiscal_year = Column(Integer, nullable=False, index=True)
    fiscal_period = Column(Integer, nullable=True, index=True)  # e.g., 1-12 for months, 1-52 for weeks
    
    # Processing information
    processed_at = Column(Date, nullable=True)
    processed_by = Column(String(50), nullable=True)
    
    # Approval workflow
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_at = Column(Date, nullable=True)
    approved_by = Column(String(50), nullable=True)
    
    # Locking mechanism
    is_locked = Column(Boolean, default=False, nullable=False)
    locked_at = Column(Date, nullable=True)
    locked_by = Column(String(50), nullable=True)
    
    # Relationships
    payslips = relationship("Payslip", back_populates="pay_period")
    
    def __repr__(self):
        return f"<PayPeriod {self.name} ({self.start_date} to {self.end_date})>"
    
    @property
    def is_current(self):
        """Check if the current date falls within this pay period."""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_past_due(self):
        """Check if the payment date has passed but the period is not yet paid."""
        today = date.today()
        return today > self.payment_date and self.status != 'PAID' and self.status != 'CANCELLED'
    
    @property
    def duration_days(self):
        """Return the duration of the pay period in days."""
        return (self.end_date - self.start_date).days + 1
    
    def get_status_display(self):
        """Return a user-friendly status name."""
        status_map = {
            'DRAFT': 'Draft',
            'OPEN': 'Open',
            'PROCESSING': 'Processing',
            'PROCESSED': 'Processed',
            'PAID': 'Paid',
            'CLOSED': 'Closed',
            'CANCELLED': 'Cancelled'
        }
        return status_map.get(self.status, self.status)
