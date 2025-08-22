from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.schemas.base import BaseSchema


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    WIRE_TRANSFER = "wire_transfer"
    CHECK = "check"
    CASH = "cash"
    OTHER = "other"


class TaxPaymentBase(BaseModel):
    payment_date: datetime
    amount: float = Field(..., gt=0, description="Payment amount must be greater than 0")
    currency: str = Field("USD", max_length=3, description="ISO 4217 currency code")
    payment_method: PaymentMethod
    reference_number: Optional[str] = Field(None, max_length=100)
    status: PaymentStatus = PaymentStatus.PENDING
    notes: Optional[str] = Field(None, max_length=500)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('currency')
    def currency_must_be_uppercase(cls, v):
        return v.upper()


class TaxPaymentCreate(TaxPaymentBase):
    tax_return_id: UUID
    created_by: UUID


class TaxPaymentUpdate(BaseModel):
    payment_date: Optional[datetime] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    payment_method: Optional[PaymentMethod] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    status: Optional[PaymentStatus] = None
    notes: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None


class TaxPaymentInDB(TaxPaymentBase):
    id: UUID
    tax_return_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TaxPaymentResponse(BaseSchema):
    success: bool = True
    data: TaxPaymentInDB


class TaxPaymentListResponse(BaseSchema):
    success: bool = True
    data: List[TaxPaymentInDB]
    total: int
    page: int
    limit: int


class TaxPaymentFilter(BaseModel):
    tax_return_id: Optional[UUID] = None
    status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    currency: Optional[str] = None
    search: Optional[str] = None


class TaxPaymentSummary(BaseModel):
    total_paid: float
    total_refunded: float
    currency: str
    payment_count: int
    by_status: Dict[PaymentStatus, int]
    by_method: Dict[PaymentMethod, int]


class TaxPaymentSummaryResponse(BaseSchema):
    success: bool = True
    data: TaxPaymentSummary
