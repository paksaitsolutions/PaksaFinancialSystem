"""
Attendance management schemas
"""
from datetime import date, time, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, validator

class AttendanceRecordBase(BaseModel):
    date: date
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    status: str = "present"
    notes: Optional[str] = None

class AttendanceRecordCreate(AttendanceRecordBase):
    employee_id: UUID
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['present', 'absent', 'late', 'half_day', 'holiday', 'sick_leave']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v

class AttendanceRecordUpdate(BaseModel):
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class AttendanceRecordInDB(AttendanceRecordBase):
    id: UUID
    employee_id: UUID
    hours_worked: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceRecord(AttendanceRecordInDB):
    pass