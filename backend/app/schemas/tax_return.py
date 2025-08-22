from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator
from pydantic.networks import AnyHttpUrl

from app.schemas.base import BaseSchema


class TaxReturnStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    FILED = "filed"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class TaxFilingFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    AD_HOC = "ad_hoc"


class TaxReturnType(str, Enum):
    VAT = "vat"
    GST = "gst"
    SALES_TAX = "sales_tax"
    INCOME_TAX = "income_tax"
    WITHHOLDING_TAX = "withholding_tax"
    DIGITAL_SERVICES_TAX = "digital_services_tax"
    CUSTOM = "custom"


class TaxReturnLineItemBase(BaseModel):
    line_item_code: str = Field(..., max_length=50)
    description: str = Field(..., max_length=255)
    amount: Dict[str, float]  # {currency: amount}
    tax_type: Optional[str] = None
    tax_rate: Optional[Dict[str, Any]] = None  # {rate: float, type: str}
    tax_amount: Optional[Dict[str, float]] = None  # {currency: amount}

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class TaxReturnLineItemCreate(TaxReturnLineItemBase):
    pass


class TaxReturnLineItemUpdate(TaxReturnLineItemBase):
    pass


class TaxReturnLineItemInDB(TaxReturnLineItemBase):
    id: UUID
    tax_return_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TaxReturnBase(BaseModel):
    return_type: str = Field(..., max_length=50)
    filing_frequency: TaxFilingFrequency
    tax_period_start: date
    tax_period_end: date
    due_date: date
    jurisdiction_code: str = Field(..., max_length=10)
    tax_authority_id: Optional[str] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('tax_period_end')
    def validate_period_dates(cls, v, values):
        if 'tax_period_start' in values and v < values['tax_period_start']:
            raise ValueError('tax_period_end must be after tax_period_start')
        return v


class TaxReturnCreate(TaxReturnBase):
    line_items: List[TaxReturnLineItemCreate] = Field(default_factory=list)


class TaxReturnUpdate(BaseModel):
    status: Optional[TaxReturnStatus] = None
    filing_date: Optional[date] = None
    filing_reference: Optional[str] = None
    confirmation_number: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TaxReturnInDB(TaxReturnBase):
    id: UUID
    company_id: UUID
    status: TaxReturnStatus
    total_taxable_amount: Dict[str, float]
    total_tax_amount: Dict[str, float]
    total_paid_amount: Dict[str, float]
    total_due_amount: Dict[str, float]
    filing_reference: Optional[str] = None
    confirmation_number: Optional[str] = None
    created_by: UUID
    approved_by: Optional[UUID] = None
    filed_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    line_items: List[TaxReturnLineItemInDB] = []

    class Config:
        orm_mode = True


class TaxReturnResponse(BaseSchema):
    success: bool = True
    data: TaxReturnInDB


class TaxReturnListResponse(BaseSchema):
    success: bool = True
    data: List[TaxReturnInDB]
    total: int
    page: int
    limit: int


class TaxReturnFilter(BaseModel):
    status: Optional[TaxReturnStatus] = None
    return_type: Optional[str] = None
    filing_frequency: Optional[TaxFilingFrequency] = None
    tax_period_start: Optional[date] = None
    tax_period_end: Optional[date] = None
    jurisdiction_code: Optional[str] = None
    search: Optional[str] = None


class TaxFilingCalendarEntry(BaseModel):
    id: UUID
    return_type: str
    jurisdiction_code: str
    period_start: date
    period_end: date
    due_date: date
    status: TaxReturnStatus
    is_upcoming: bool
    is_overdue: bool


class TaxFilingCalendarResponse(BaseSchema):
    success: bool = True
    data: List[TaxFilingCalendarEntry]


class TaxReturnGenerate(BaseModel):
    """Schema for generating a new tax return."""
    return_type: str = Field(..., description="Type of tax return (e.g., 'vat', 'gst', 'income_tax')")
    tax_period_start: date = Field(..., description="Start date of the tax period")
    tax_period_end: date = Field(..., description="End date of the tax period")
    jurisdiction_code: str = Field(..., description="Tax jurisdiction code")
    filing_frequency: Optional[TaxFilingFrequency] = Field(
        None, 
        description="Filing frequency (defaults to monthly if not specified)"
    )
    force_recalculation: Optional[bool] = Field(
        False, 
        description="If True, recalculates the return even if one exists for the period"
    )
    generate_pdf: Optional[bool] = Field(
        False, 
        description="If True, generates a PDF version of the tax return"
    )
    include_attachments: Optional[bool] = Field(
        False, 
        description="If True, includes attachments in the generated PDF"
    )

    @validator('tax_period_end')
    def validate_period_dates(cls, v, values):
        if 'tax_period_start' in values and v < values['tax_period_start']:
            raise ValueError('tax_period_end must be after tax_period_start')
        return v


class TaxReturnSubmitRequest(BaseModel):
    notes: Optional[str] = None
    file_now: bool = False
    

class EfileStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ERROR = "error"


class TaxReturnEfileResponse(BaseModel):
    success: bool
    status: EfileStatus
    message: Optional[str] = None
    confirmation_number: Optional[str] = None
    submission_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
