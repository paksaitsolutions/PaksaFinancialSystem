from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class TaxReturnBase(BaseModel):
    return_id: str
    tax_year: str
    return_type: str
    ntn: Optional[str] = None
    cnic: Optional[str] = None
    gross_income: Decimal = 0
    taxable_income: Decimal = 0
    tax_liability: Decimal = 0
    advance_tax_paid: Decimal = 0
    due_date: date
    filed_date: Optional[date] = None
    status: str = "draft"
    remarks: Optional[str] = None

class TaxReturnCreate(TaxReturnBase):
    pass

class TaxReturnUpdate(BaseModel):
    return_id: Optional[str] = None
    tax_year: Optional[str] = None
    return_type: Optional[str] = None
    ntn: Optional[str] = None
    cnic: Optional[str] = None
    gross_income: Optional[Decimal] = None
    taxable_income: Optional[Decimal] = None
    tax_liability: Optional[Decimal] = None
    advance_tax_paid: Optional[Decimal] = None
    due_date: Optional[date] = None
    filed_date: Optional[date] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

class TaxReturn(TaxReturnBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaxReturnStats(BaseModel):
    filed: int
    pending: int
    overdue: int
    amendments: int