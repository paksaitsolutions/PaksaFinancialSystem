"""
Pydantic models for recurring journal entries and allocation rules.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator

from app.schemas.gl_schemas import JournalEntryLineCreate, JournalEntryCreate


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


# Shared properties
class RecurringJournalBase(BaseModel):
    """Base model for recurring journal entries."""
    name: str = Field(..., max_length=200, description="Name of the recurring entry")
    description: Optional[str] = Field(None, description="Description of the recurring entry")
    
    # Recurrence settings
    frequency: RecurrenceFrequency = Field(..., description="How often the entry recurs")
    interval: int = Field(1, ge=1, le=999, description="Interval between occurrences")
    
    # Start and end dates
    start_date: date = Field(..., description="Date to start generating entries")
    end_type: RecurrenceEndType = Field(RecurrenceEndType.NEVER, description="When to stop generating entries")
    end_after_occurrences: Optional[int] = Field(
        None, 
        ge=1, 
        description="Number of occurrences before ending"
    )
    end_date: Optional[date] = Field(
        None, 
        description="Date to stop generating entries (inclusive)"
    )
    
    # Status
    status: RecurringJournalStatus = Field(
        RecurringJournalStatus.ACTIVE, 
        description="Status of the recurring entry"
    )
    
    # Template data (will be used to create journal entries)
    template_data: Dict[str, Any] = Field(
        ...,
        description="Template data for generating journal entries"
    )
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
        }
    
    @validator('end_after_occurrences')
    def validate_end_after_occurrences(cls, v, values):
        if values.get('end_type') == 'after_occurrences' and v is None:
            raise ValueError("end_after_occurrences is required when end_type is 'after_occurrences'")
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if values.get('end_type') == 'on_date' and v is None:
            raise ValueError("end_date is required when end_type is 'on_date'")
        
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError("end_date must be after start_date")
            
        return v


# Properties to receive on recurring journal creation
class RecurringJournalCreate(RecurringJournalBase):
    """Schema for creating a new recurring journal entry."""
    template_data: Dict[str, Any] = Field(
        ...,
        description="Template data for generating journal entries. Must include 'lines' with debit/credit entries."
    )
    
    @root_validator
    def validate_template_data(cls, values):
        template_data = values.get('template_data', {})
        
        # Check if required fields are present
        if 'lines' not in template_data or not isinstance(template_data['lines'], list):
            raise ValueError("Template data must include 'lines' as a list")
            
        # Validate that the lines balance
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for line in template_data['lines']:
            if not isinstance(line, dict):
                raise ValueError("Each line in 'lines' must be an object")
                
            amount = Decimal(str(line.get('amount', '0')))
            
            if line.get('type') == 'debit':
                total_debit += amount
            elif line.get('type') == 'credit':
                total_credit += amount
                
        if abs(total_debit - total_credit) > Decimal('0.01'):  # Allow for floating point errors
            raise ValueError(f"Debits ({total_debit}) and credits ({total_credit}) must balance")
            
        return values


# Properties to receive on recurring journal update
class RecurringJournalUpdate(BaseModel):
    """Schema for updating an existing recurring journal entry."""
    name: Optional[str] = Field(None, max_length=200, description="Name of the recurring entry")
    description: Optional[str] = Field(None, description="Description of the recurring entry")
    
    # Recurrence settings
    frequency: Optional[RecurrenceFrequency] = Field(None, description="How often the entry recurs")
    interval: Optional[int] = Field(None, ge=1, le=999, description="Interval between occurrences")
    
    # Start and end dates
    start_date: Optional[date] = Field(None, description="Date to start generating entries")
    end_type: Optional[RecurrenceEndType] = Field(None, description="When to stop generating entries")
    end_after_occurrences: Optional[int] = Field(
        None, 
        ge=1, 
        description="Number of occurrences before ending"
    )
    end_date: Optional[date] = Field(
        None, 
        description="Date to stop generating entries (inclusive)"
    )
    
    # Status
    status: Optional[RecurringJournalStatus] = Field(
        None, 
        description="Status of the recurring entry"
    )
    
    # Template data (will be used to create journal entries)
    template_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Template data for generating journal entries"
    )
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
        }
    
    @root_validator
    def validate_dates_and_occurrences(cls, values):
        # If end_type is being updated, validate the corresponding field
        if 'end_type' in values and values['end_type'] is not None:
            if values['end_type'] == 'after_occurrences' and 'end_after_occurrences' not in values:
                raise ValueError("end_after_occurrences is required when end_type is 'after_occurrences'")
            elif values['end_type'] == 'on_date' and 'end_date' not in values:
                raise ValueError("end_date is required when end_type is 'on_date'")
        
        # If end_date is being updated, validate it against start_date if provided
        if 'end_date' in values and values['end_date'] is not None:
            if 'start_date' in values and values['start_date'] is not None:
                if values['end_date'] < values['start_date']:
                    raise ValueError("end_date must be after start_date")
            
        return values


# Properties shared by models stored in DB
class RecurringJournalInDBBase(RecurringJournalBase):
    """Base model for recurring journal entries in the database."""
    id: UUID
    company_id: UUID
    created_by: UUID
    last_run_date: Optional[date] = None
    next_run_date: Optional[date] = None
    total_occurrences: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# Properties to return to client
class RecurringJournal(RecurringJournalInDBBase):
    """Schema for returning a recurring journal entry to the client."""
    pass


# Properties stored in DB
class RecurringJournalInDB(RecurringJournalInDBBase):
    """Schema for a recurring journal entry in the database."""
    pass


# Allocation Rules
class AllocationDestinationBase(BaseModel):
    """Base model for allocation destinations."""
    account_id: UUID = Field(..., description="ID of the account to allocate to")
    percentage: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=100, 
        description="Percentage of amount to allocate (0-100)"
    )
    fixed_amount: Optional[Decimal] = Field(
        None, 
        ge=0, 
        description="Fixed amount to allocate"
    )
    description: Optional[str] = Field(None, description="Description for this allocation")
    reference: Optional[str] = Field(None, max_length=100, description="Reference for this allocation")
    sequence: int = Field(0, ge=0, description="Order of application")
    is_active: bool = Field(True, description="Whether this destination is active")
    
    @root_validator
    def validate_allocation_fields(cls, values):
        percentage = values.get('percentage')
        fixed_amount = values.get('fixed_amount')
        
        if percentage is None and fixed_amount is None:
            raise ValueError("Either percentage or fixed_amount must be provided")
            
        if percentage is not None and fixed_amount is not None:
            raise ValueError("Only one of percentage or fixed_amount can be provided")
            
        return values


class AllocationDestinationCreate(AllocationDestinationBase):
    """Schema for creating an allocation destination."""
    pass


class AllocationDestinationUpdate(AllocationDestinationBase):
    """Schema for updating an allocation destination."""
    account_id: Optional[UUID] = None
    percentage: Optional[Decimal] = None
    fixed_amount: Optional[Decimal] = None
    sequence: Optional[int] = None
    is_active: Optional[bool] = None


class AllocationDestinationInDB(AllocationDestinationBase):
    """Schema for an allocation destination in the database."""
    allocation_rule_id: UUID
    
    class Config:
        orm_mode = True


class AllocationDestination(AllocationDestinationInDB):
    """Schema for returning an allocation destination to the client."""
    pass


class AllocationRuleBase(BaseModel):
    """Base model for allocation rules."""
    name: str = Field(..., max_length=200, description="Name of the allocation rule")
    description: Optional[str] = Field(None, description="Description of the allocation rule")
    is_active: bool = Field(True, description="Whether the rule is active")
    allocation_method: str = Field(..., description="Method of allocation (percentage, fixed, etc.)")
    
    @validator('allocation_method')
    def validate_allocation_method(cls, v):
        if v not in ['percentage', 'fixed']:
            raise ValueError("allocation_method must be 'percentage' or 'fixed'")
        return v


class AllocationRuleCreate(AllocationRuleBase):
    """Schema for creating an allocation rule."""
    destinations: List[AllocationDestinationCreate] = Field(
        ..., 
        min_items=1, 
        description="List of destinations for the allocation"
    )
    
    @root_validator
    def validate_destinations(cls, values):
        destinations = values.get('destinations', [])
        allocation_method = values.get('allocation_method')
        
        if not destinations:
            raise ValueError("At least one destination is required")
            
        if allocation_method == 'percentage':
            total_percent = sum(d.percentage or 0 for d in destinations if d.is_active)
            if abs(total_percent - 100) > 0.01:  # Allow for floating point errors
                raise ValueError(f"Total percentage must be 100% (got {total_percent}%)")
                
        elif allocation_method == 'fixed':
            total_fixed = sum(d.fixed_amount or 0 for d in destinations if d.is_active)
            if total_fixed <= 0:
                raise ValueError("Total fixed amount must be greater than 0")
                
        return values


class AllocationRuleUpdate(AllocationRuleBase):
    """Schema for updating an allocation rule."""
    name: Optional[str] = Field(None, max_length=200, description="Name of the allocation rule")
    description: Optional[str] = Field(None, description="Description of the allocation rule")
    is_active: Optional[bool] = Field(None, description="Whether the rule is active")
    allocation_method: Optional[str] = Field(None, description="Method of allocation (percentage, fixed, etc.)")
    destinations: Optional[List[AllocationDestinationCreate]] = Field(
        None, 
        min_items=1, 
        description="List of destinations for the allocation"
    )
    
    @root_validator
    def validate_destinations(cls, values):
        if 'destinations' in values and values['destinations'] is not None:
            destinations = values['destinations']
            allocation_method = values.get('allocation_method')
            
            if not destinations:
                raise ValueError("At least one destination is required")
                
            if allocation_method == 'percentage':
                total_percent = sum(d.percentage or 0 for d in destinations if d.is_active)
                if abs(total_percent - 100) > 0.01:  # Allow for floating point errors
                    raise ValueError(f"Total percentage must be 100% (got {total_percent}%)")
                    
            elif allocation_method == 'fixed':
                total_fixed = sum(d.fixed_amount or 0 for d in destinations if d.is_active)
                if total_fixed <= 0:
                    raise ValueError("Total fixed amount must be greater than 0")
                    
        return values


class AllocationRuleInDBBase(AllocationRuleBase):
    """Base model for allocation rules in the database."""
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class AllocationRule(AllocationRuleInDBBase):
    """Schema for returning an allocation rule to the client."""
    destinations: List[AllocationDestination] = []


class AllocationRuleInDB(AllocationRuleInDBBase):
    """Schema for an allocation rule in the database."""
    destinations: List[AllocationDestinationInDB] = []


class AllocationResult(BaseModel):
    """Result of applying an allocation rule."""
    account_id: UUID
    amount: Decimal
    description: Optional[str] = None
    reference: Optional[str] = None


class ApplyAllocationRule(BaseModel):
    """Schema for applying an allocation rule."""
    amount: Decimal = Field(..., gt=0, description="Amount to allocate")
    reference: Optional[str] = Field(None, max_length=200, description="Reference for the allocation")
    description: Optional[str] = Field(None, description="Description for the allocation")
