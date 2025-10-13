"""
Recurring Journal Entry models for the Paksa Financial System.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SQLEnum, ForeignKey, 
    Integer, Numeric, String, Text, UniqueConstraint, Index, JSON
)
from app.models.base import GUID as PG_UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates


from app.models.base import Base



from app.models import JournalEntry, JournalEntryStatus, GLChartOfAccounts

class RecurrenceFrequency(str, Enum):
    """Frequency of recurring journal entries."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    CUSTOM = "custom"

class RecurrenceEndType(str, Enum):
    """When the recurrence should end."""
    NEVER = "never"
    AFTER_OCCURRENCES = "after_occurrences"
    ON_DATE = "on_date"

class RecurringJournalStatus(str, Enum):
    """Status of a recurring journal entry."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RecurringJournalEntry(Base):
    """Defines a template for recurring journal entries."""
    __tablename__ = "recurring_journal_entries"
    
    id = Column(PG_UUID(), primary_key=True, default=uuid4)
    
    # Basic information
    name = Column(String(200), nullable=False, comment="Name of the recurring entry")
    description = Column(Text, nullable=True, comment="Description of the recurring entry")
    
    # Recurrence settings
    frequency = Column(SQLEnum(RecurrenceFrequency), nullable=False, comment="How often the entry recurs")
    interval = Column(Integer, default=1, nullable=False, comment="Interval between occurrences")
    
    # Start and end dates
    start_date = Column(Date, nullable=False, index=True, comment="Date to start generating entries")
    end_type = Column(SQLEnum(RecurrenceEndType), default=RecurrenceEndType.NEVER, nullable=False, comment="When to stop generating entries")
    end_after_occurrences = Column(Integer, nullable=True, comment="Number of occurrences before ending")
    end_date = Column(Date, nullable=True, index=True, comment="Date to stop generating entries")
    
    # Status and tracking
    status = Column(SQLEnum(RecurringJournalStatus), default=RecurringJournalStatus.ACTIVE, nullable=False, index=True)
    last_run_date = Column(Date, nullable=True, comment="Last date the entry was generated")
    next_run_date = Column(Date, nullable=False, index=True, comment="Next date the entry will be generated")
    total_occurrences = Column(Integer, default=0, nullable=False, comment="Total number of entries generated")
    
    # Company and user references
    company_id = Column(
        PG_UUID(), 
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Company this recurring entry belongs to"
    )
    created_by = Column(
        PG_UUID(),
        ForeignKey("users.id"),
        nullable=False,
        comment="User who created this recurring entry"
    )
    
    # Relationships
    company = relationship("Company")
    template = relationship("RecurringJournalTemplate", uselist=False, back_populates="recurring_entry")
    
    # Indexes
    __table_args__ = (
        Index("idx_recurring_journal_status", "status"),
        Index("idx_recurring_journal_company", "company_id"),
        Index("idx_recurring_journal_next_run", "next_run_date"),
    )
    
    def calculate_next_run(self, current_date: date = None) -> Optional[date]:
        """Calculate the next run date based on the recurrence pattern."""
        if not current_date:
            current_date = date.today()
            
        if self.status != RecurringJournalStatus.ACTIVE:
            return None
            
        if self.end_type == RecurrenceEndType.AFTER_OCCURRENCES and \
           self.total_occurrences >= self.end_after_occurrences:
            self.status = RecurringJournalStatus.COMPLETED
            return None
            
        if self.end_type == RecurrenceEndType.ON_DATE and self.end_date and current_date >= self.end_date:
            self.status = RecurringJournalStatus.COMPLETED
            return None
            
        delta = None
        
        if self.frequency == RecurrenceFrequency.DAILY:
            delta = timedelta(days=1 * self.interval)
        elif self.frequency == RecurrenceFrequency.WEEKLY:
            delta = timedelta(weeks=1 * self.interval)
        elif self.frequency == RecurrenceFrequency.BIWEEKLY:
            delta = timedelta(weeks=2 * self.interval)
        elif self.frequency == RecurrenceFrequency.MONTHLY:
            # Handle month arithmetic
            year = current_date.year + (current_date.month + self.interval - 1) // 12
            month = (current_date.month + self.interval - 1) % 12 + 1
            day = min(current_date.day, 28)  # Handle months with fewer days
            try:
                return current_date.replace(year=year, month=month, day=day)
            except ValueError:
                # Handle invalid dates (e.g., Feb 30)
                return (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif self.frequency == RecurrenceFrequency.QUARTERLY:
            months = 3 * self.interval
            year = current_date.year + (current_date.month + months - 1) // 12
            month = (current_date.month + months - 1) % 12 + 1
            day = min(current_date.day, 28)
            try:
                return current_date.replace(year=year, month=month, day=day)
            except ValueError:
                return (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif self.frequency == RecurrenceFrequency.SEMI_ANNUALLY:
            months = 6 * self.interval
            year = current_date.year + (current_date.month + months - 1) // 12
            month = (current_date.month + months - 1) % 12 + 1
            day = min(current_date.day, 28)
            try:
                return current_date.replace(year=year, month=month, day=day)
            except ValueError:
                return (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif self.frequency == RecurrenceFrequency.ANNUALLY:
            try:
                return current_date.replace(year=current_date.year + 1 * self.interval)
            except ValueError:  # Leap year handling
                return current_date.replace(year=current_date.year + 1 * self.interval, month=3, day=1) - timedelta(days=1)
        
        # For custom or unsupported frequencies, return None
        if not delta:
            return None
            
        next_run = current_date + delta
        
        # Check if we've passed the end date
        if self.end_type == RecurrenceEndType.ON_DATE and self.end_date and next_run > self.end_date:
            self.status = RecurringJournalStatus.COMPLETED
            return None
            
        return next_run
    
    def __repr__(self):
        return f"<RecurringJournalEntry {self.name} ({self.frequency})>"


class RecurringJournalTemplate(Base):
    """Template for the journal entries generated by a recurring journal entry."""
    __tablename__ = "recurring_journal_templates"
    
    recurring_journal_id = Column(
        PG_UUID(),
        ForeignKey("recurring_journal_entries.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Reference to the parent recurring journal entry"
    )
    
    # Template data (stored as JSON to handle dynamic fields)
    template_data = Column(JSONB, nullable=False, comment="Template data for generating journal entries")
    
    # Relationships
    recurring_entry = relationship("RecurringJournalEntry", back_populates="template")
    
    def __repr__(self):
        return f"<RecurringJournalTemplate for {self.recurring_journal_id}>"


class AllocationRule(Base):
    """Rules for allocating amounts across multiple accounts."""
    __tablename__ = "allocation_rules"
    
    id = Column(PG_UUID(), primary_key=True, default=uuid4)
    
    # Basic information
    name = Column(String(200), nullable=False, comment="Name of the allocation rule")
    description = Column(Text, nullable=True, comment="Description of the allocation rule")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether the rule is active")
    
    # Allocation method
    allocation_method = Column(String(50), nullable=False, comment="Method of allocation (percentage, fixed, etc.)")
    
    # Company reference
    company_id = Column(
        PG_UUID(), 
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Company this allocation rule belongs to"
    )
    
    # Relationships
    company = relationship("Company")
    destinations = relationship("AllocationDestination", back_populates="allocation_rule", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_allocation_rule_company", "company_id"),
    )
    
    def allocate_amount(self, amount: Decimal) -> List[Dict[str, Any]]:
        """
        Allocate the given amount according to this rule.
        
        Args:
            amount: The amount to allocate
            
        Returns:
            List of dictionaries with 'account_id' and 'amount' for each destination
        """
        if not self.is_active:
            return []
            
        result = []
        
        if self.allocation_method == "percentage":
            total_percent = sum(d.percentage for d in self.destinations if d.percentage)
            if total_percent != 100:
                raise ValueError(f"Total percentage must be 100%, got {total_percent}%")
                
            remaining = amount
            
            # Sort to ensure consistent ordering
            sorted_destinations = sorted(self.destinations, key=lambda d: d.sequence or 0)
            
            for i, dest in enumerate(sorted_destinations):
                if not dest.is_active:
                    continue
                    
                if i == len(sorted_destinations) - 1:
                    # Last destination gets any remaining amount to avoid rounding errors
                    allocated = remaining
                else:
                    allocated = (amount * Decimal(dest.percentage or 0)) / 100
                    remaining -= allocated
                    
                result.append({
                    "account_id": dest.account_id,
                    "amount": allocated.quantize(Decimal('0.01')),
                    "description": dest.description or f"Allocated from {self.name}",
                    "reference": dest.reference
                })
                
        elif self.allocation_method == "fixed":
            total_fixed = sum(d.fixed_amount for d in self.destinations if d.fixed_amount)
            
            if total_fixed > amount:
                raise ValueError(f"Total fixed amount ({total_fixed}) exceeds available amount ({amount})")
                
            remaining = amount
            
            # Sort to ensure consistent ordering
            sorted_destinations = sorted(self.destinations, key=lambda d: d.sequence or 0)
            
            for i, dest in enumerate(sorted_destinations):
                if not dest.is_active or not dest.fixed_amount:
                    continue
                    
                if i == len(sorted_destinations) - 1:
                    # Last destination gets any remaining amount
                    allocated = remaining
                else:
                    allocated = dest.fixed_amount
                    remaining -= allocated
                    
                result.append({
                    "account_id": dest.account_id,
                    "amount": allocated.quantize(Decimal('0.01')),
                    "description": dest.description or f"Allocated from {self.name}",
                    "reference": dest.reference
                })
                
        return result
    
    def __repr__(self):
        return f"<AllocationRule {self.name} ({self.allocation_method})>"


class AllocationDestination(Base):
    """Destination accounts for an allocation rule."""
    __tablename__ = "allocation_destinations"
    
    # Basic information
    allocation_rule_id = Column(
        PG_UUID(),
        ForeignKey("allocation_rules.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Reference to the allocation rule"
    )
    
    account_id = Column(
        PG_UUID(),
        ForeignKey("chart_of_accounts.id"),
        primary_key=True,
        comment="Account to allocate to"
    )
    
    # Allocation parameters
    percentage = Column(Numeric(5, 2), nullable=True, comment="Percentage of amount to allocate (0-100)")
    fixed_amount = Column(Numeric(20, 6), nullable=True, comment="Fixed amount to allocate")
    
    # Additional information
    description = Column(Text, nullable=True, comment="Description for this allocation")
    reference = Column(String(100), nullable=True, comment="Reference for this allocation")
    sequence = Column(Integer, default=0, nullable=False, comment="Order of application")
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether this destination is active")
    
    # Relationships
    allocation_rule = relationship("AllocationRule", back_populates="destinations")
    account = relationship("ChartOfAccounts")
    
    # Indexes
    __table_args__ = (
        Index("idx_allocation_destination_account", "account_id"),
    )
    
    def __repr__(self):
        if self.percentage is not None:
            return f"<AllocationDestination {self.account_id} ({self.percentage}%)>"
        elif self.fixed_amount is not None:
            return f"<AllocationDestination {self.account_id} (${self.fixed_amount})>"
        return f"<AllocationDestination {self.account_id}>"



