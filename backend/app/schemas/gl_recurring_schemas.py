"""
Pydantic schemas for recurring journal entries and allocation rules.
"""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.gl_recurring_models import (
    RecurrenceFrequency,
    RecurrenceEndType,
    RecurringJournalStatus,
)


class RecurrenceFrequencyEnum(str, Enum):
    """Enum for recurrence frequency."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    CUSTOM = "custom"


class RecurrenceEndTypeEnum(str, Enum):
    """Enum for recurrence end type."""
    NEVER = "never"
    AFTER_OCCURRENCES = "after_occurrences"
    ON_DATE = "on_date"


class RecurringJournalStatusEnum(str, Enum):
    """Enum for recurring journal status."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RecurringJournalLineBase(BaseModel):
    """Base schema for recurring journal line items."""
    account_id: UUID = Field(..., description="GL Account ID")
    description: str = Field(..., max_length=200)
    amount: float = Field(..., gt=0, description="Positive amount")
    is_debit: bool = Field(True, description="True for debit, False for credit")
    tax_code: Optional[str] = Field(None, max_length=50)
    cost_center_id: Optional[UUID] = Field(None, description="Cost center ID")
    project_id: Optional[UUID] = Field(None, description="Project ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RecurringJournalBase(BaseModel):
    """Base schema for recurring journal entries."""
    name: str = Field(..., max_length=200, description="Name of the recurring entry")
    description: Optional[str] = Field(None, description="Description of the entry")
    
    # Recurrence settings
    frequency: RecurrenceFrequencyEnum = Field(..., description="How often the entry recurs")
    interval: int = Field(1, ge=1, description="Interval between occurrences")
    
    # Start and end dates
    start_date: date = Field(..., description="Date to start generating entries")
    end_type: RecurrenceEndTypeEnum = Field(
        RecurrenceEndTypeEnum.NEVER,
        description="When to stop generating entries"
    )
    end_after_occurrences: Optional[int] = Field(
        None,
        ge=1,
        description="Number of occurrences before ending"
    )
    end_date: Optional[date] = Field(
        None,
        description="Date to stop generating entries"
    )
    
    # Template data
    lines: List[RecurringJournalLineBase] = Field(
        ...,
        min_items=2,
        description="Journal entry lines (must balance)"
    )
    
    # Additional settings
    auto_post: bool = Field(False, description="Whether to automatically post generated entries")
    notify_users: List[UUID] = Field(
        default_factory=list,
        description="User IDs to notify when entries are generated"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    @validator('lines')
    def validate_balanced_lines(cls, lines):
        """Validate that debits equal credits."""
        total_debit = sum(line.amount for line in lines if line.is_debit)
        total_credit = sum(line.amount for line in lines if not line.is_debit)
        
        if abs(total_debit - total_credit) > 0.01:  # Allow for floating point rounding
            raise ValueError("Total debits must equal total credits")
        
        return lines
    
    @validator('end_after_occurrences')
    def validate_end_after_occurrences(cls, v, values):
        if values.get('end_type') == RecurrenceEndType.AFTER_OCCURRENCES and not v:
            raise ValueError("end_after_occurrences is required when end_type is 'after_occurrences'")
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if values.get('end_type') == RecurrenceEndType.ON_DATE and not v:
            raise ValueError("end_date is required when end_type is 'on_date'")
        
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError("end_date must be after start_date")
            
        return v


class RecurringJournalCreate(RecurringJournalBase):
    """Schema for creating a new recurring journal entry."""
    pass


class RecurringJournalUpdate(BaseModel):
    """Schema for updating an existing recurring journal entry."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[RecurringJournalStatusEnum] = None
    frequency: Optional[RecurrenceFrequencyEnum] = None
    interval: Optional[int] = Field(None, ge=1)
    start_date: Optional[date] = None
    end_type: Optional[RecurrenceEndTypeEnum] = None
    end_after_occurrences: Optional[int] = Field(None, ge=1)
    end_date: Optional[date] = None
    auto_post: Optional[bool] = None
    notify_users: Optional[List[UUID]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic config."""
        extra = "forbid"


class RecurringJournalLineResponse(RecurringJournalLineBase):
    """Response schema for recurring journal line items."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class RecurringJournalResponse(RecurringJournalBase):
    """Response schema for recurring journal entries."""
    id: UUID
    status: RecurringJournalStatusEnum
    last_run_date: Optional[date] = None
    next_run_date: date
    total_occurrences: int = 0
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    company_id: UUID
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class RecurringJournalListResponse(BaseModel):
    """Response schema for paginated list of recurring journal entries."""
    items: List[RecurringJournalResponse]
    total: int
    page: int
    page_size: int


class AllocationRuleBase(BaseModel):
    """Base schema for allocation rules."""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    is_active: bool = True
    allocation_method: str = Field(..., description="Method of allocation (percentage, fixed, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AllocationDestinationBase(BaseModel):
    """Base schema for allocation rule destinations."""
    account_id: UUID = Field(..., description="Destination account ID")
    percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage of amount to allocate")
    fixed_amount: Optional[float] = Field(None, ge=0, description="Fixed amount to allocate")
    description: Optional[str] = None
    reference: Optional[str] = None
    is_active: bool = True


class AllocationRuleCreate(AllocationRuleBase):
    """Schema for creating a new allocation rule."""
    destinations: List[AllocationDestinationBase] = Field(..., min_items=1)


class AllocationRuleUpdate(BaseModel):
    """Schema for updating an allocation rule."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    allocation_method: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AllocationRuleResponse(AllocationRuleBase):
    """Response schema for allocation rules."""
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class AllocationDestinationResponse(AllocationDestinationBase):
    """Response schema for allocation rule destinations."""
    id: UUID
    allocation_rule_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        orm_mode = True
