"""
Schemas for allocation operations.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class AllocationMethod(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    EQUAL = "equal"
    WEIGHTED = "weighted"
    FORMULA = "formula"


class AllocationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class AllocationRuleLineBase(BaseModel):
    """Base schema for allocation rule line operations."""
    target_account_id: UUID = Field(..., description="Target account ID")
    allocation_percentage: Optional[Decimal] = Field(None, description="Allocation percentage")
    fixed_amount: Optional[Decimal] = Field(None, description="Fixed allocation amount")
    weight: Optional[Decimal] = Field(None, description="Weight for weighted allocation")
    line_order: int = Field(1, description="Line order")

    @validator('allocation_percentage')
    def validate_percentage(cls, v):
        """Validate allocation percentage."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Percentage must be between 0 and 100")
        return v


class AllocationRuleLineCreate(AllocationRuleLineBase):
    """Schema for creating allocation rule lines."""
    pass


class AllocationRuleLineResponse(AllocationRuleLineBase):
    """Schema for allocation rule line response."""
    id: UUID = Field(..., description="Line ID")
    allocation_rule_id: UUID = Field(..., description="Parent rule ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class AllocationRuleBase(BaseModel):
    """Base schema for allocation rule operations."""
    rule_name: str = Field(..., description="Rule name")
    rule_code: Optional[str] = Field(None, description="Rule code")
    description: Optional[str] = Field(None, description="Rule description")
    allocation_method: AllocationMethod = Field(..., description="Allocation method")
    status: AllocationStatus = Field(AllocationStatus.ACTIVE, description="Rule status")
    source_account_id: Optional[UUID] = Field(None, description="Source account ID")
    effective_from: date = Field(..., description="Effective from date")
    effective_to: Optional[date] = Field(None, description="Effective to date")
    priority: int = Field(100, description="Rule priority")

    @validator('effective_to')
    def validate_effective_dates(cls, v, values):
        """Validate effective dates."""
        if v and 'effective_from' in values and v < values['effective_from']:
            raise ValueError("Effective to date must be after effective from date")
        return v


class AllocationRuleCreate(AllocationRuleBase):
    """Schema for creating allocation rules."""
    allocation_lines: List[AllocationRuleLineCreate] = Field([], description="Allocation lines")

    @validator('allocation_lines')
    def validate_allocation_lines(cls, v, values):
        """Validate allocation lines based on method."""
        if not v:
            raise ValueError("At least one allocation line is required")
        
        method = values.get('allocation_method')
        
        if method == AllocationMethod.PERCENTAGE:
            total_percentage = sum(line.allocation_percentage or 0 for line in v)
            if abs(total_percentage - 100) > 0.01:
                raise ValueError("Total percentage must equal 100%")
        
        return v


class AllocationRuleUpdate(BaseModel):
    """Schema for updating allocation rules."""
    rule_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AllocationStatus] = None
    effective_to: Optional[date] = None
    priority: Optional[int] = None


class AllocationRuleResponse(AllocationRuleBase):
    """Schema for allocation rule response."""
    id: UUID = Field(..., description="Rule ID")
    allocation_lines: List[AllocationRuleLineResponse] = Field([], description="Allocation lines")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class AllocationEntryResponse(BaseModel):
    """Schema for allocation entry response."""
    id: UUID = Field(..., description="Entry ID")
    allocation_id: UUID = Field(..., description="Parent allocation ID")
    target_account_id: UUID = Field(..., description="Target account ID")
    allocated_amount: Decimal = Field(..., description="Allocated amount")
    allocation_percentage: Optional[Decimal] = Field(None, description="Allocation percentage")
    journal_entry_id: Optional[UUID] = Field(None, description="Generated journal entry ID")
    description: Optional[str] = Field(None, description="Entry description")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True


class AllocationResponse(BaseModel):
    """Schema for allocation response."""
    id: UUID = Field(..., description="Allocation ID")
    allocation_number: str = Field(..., description="Allocation number")
    allocation_date: date = Field(..., description="Allocation date")
    source_journal_entry_id: UUID = Field(..., description="Source journal entry ID")
    source_amount: Decimal = Field(..., description="Source amount")
    allocation_rule_id: UUID = Field(..., description="Allocation rule ID")
    status: str = Field(..., description="Allocation status")
    description: Optional[str] = Field(None, description="Allocation description")
    allocation_entries: List[AllocationEntryResponse] = Field([], description="Allocation entries")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True