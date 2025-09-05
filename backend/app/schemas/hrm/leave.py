"""
Leave management schemas
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, validator

class LeaveRequestBase(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    days_requested: Decimal
    reason: str

class LeaveRequestCreate(LeaveRequestBase):
    employee_id: UUID
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('days_requested')
    def validate_days_requested(cls, v):
        if v <= 0:
            raise ValueError('Days requested must be positive')
        return v

class LeaveRequestUpdate(BaseModel):
    leave_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    days_requested: Optional[Decimal] = None
    reason: Optional[str] = None
    status: Optional[str] = None

class LeaveRequestInDB(LeaveRequestBase):
    id: UUID
    employee_id: UUID
    status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LeaveRequest(LeaveRequestInDB):
    pass

class LeaveBalanceBase(BaseModel):
    leave_type: str
    total_days: Decimal
    used_days: Decimal
    remaining_days: Decimal
    year: int

class LeaveBalance(LeaveBalanceBase):
    id: UUID
    employee_id: UUID
    
    class Config:
        from_attributes = True