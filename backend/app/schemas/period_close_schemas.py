"""
Schemas for period close operations.
"""
from datetime import date, datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


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


class AccountingPeriodBase(BaseModel):
    """Base schema for accounting period operations."""
    period_name: str = Field(..., description="Period name")
    period_type: PeriodType = Field(..., description="Period type")
    start_date: date = Field(..., description="Period start date")
    end_date: date = Field(..., description="Period end date")

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date."""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError("End date must be after start date")
        return v


class AccountingPeriodCreate(AccountingPeriodBase):
    """Schema for creating accounting periods."""
    pass


class AccountingPeriodResponse(AccountingPeriodBase):
    """Schema for accounting period response."""
    id: UUID = Field(..., description="Period ID")
    status: PeriodStatus = Field(..., description="Period status")
    closed_by: Optional[UUID] = Field(None, description="User who closed the period")
    closed_at: Optional[datetime] = Field(None, description="Close timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class PeriodCloseTaskResponse(BaseModel):
    """Schema for period close task response."""
    id: UUID = Field(..., description="Task ID")
    period_close_id: UUID = Field(..., description="Parent close ID")
    task_name: str = Field(..., description="Task name")
    task_description: Optional[str] = Field(None, description="Task description")
    task_order: int = Field(..., description="Task order")
    is_required: bool = Field(..., description="Whether task is required")
    is_automated: bool = Field(..., description="Whether task is automated")
    status: CloseTaskStatus = Field(..., description="Task status")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    assigned_to: Optional[UUID] = Field(None, description="User assigned to task")
    completed_by: Optional[UUID] = Field(None, description="User who completed task")
    result_message: Optional[str] = Field(None, description="Task result message")
    error_message: Optional[str] = Field(None, description="Task error message")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True


class PeriodCloseResponse(BaseModel):
    """Schema for period close response."""
    id: UUID = Field(..., description="Close ID")
    close_number: str = Field(..., description="Close number")
    period_id: UUID = Field(..., description="Period ID")
    close_type: PeriodType = Field(..., description="Close type")
    status: PeriodStatus = Field(..., description="Close status")
    initiated_at: datetime = Field(..., description="Initiation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    initiated_by: UUID = Field(..., description="User who initiated close")
    completed_by: Optional[UUID] = Field(None, description="User who completed close")
    notes: Optional[str] = Field(None, description="Close notes")
    period: AccountingPeriodResponse = Field(..., description="Associated period")
    close_tasks: List[PeriodCloseTaskResponse] = Field([], description="Close tasks")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True