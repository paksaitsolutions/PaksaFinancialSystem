from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from ..core.tax.tax_policy_service import TaxType, TaxJurisdiction
from uuid import UUID

class TaxExemptionBase(BaseModel):
    exemption_code: str = Field(..., min_length=2, max_length=50, regex=r'^[A-Z0-9-_]+$')
    description: str
    certificate_required: bool = False
    valid_from: date = Field(default_factory=date.today)
    valid_to: Optional[date] = None
    tax_types: List[TaxType] = Field(default_factory=list)
    jurisdictions: List[TaxJurisdiction] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    company_id: Optional[UUID] = None

    @validator('valid_to')
    def validate_dates(cls, v, values):
        if v and 'valid_from' in values and v < values['valid_from']:
            raise ValueError("valid_to must be after valid_from")
        return v

class TaxExemptionCreate(TaxExemptionBase):
    pass

class TaxExemptionUpdate(BaseModel):
    description: Optional[str] = None
    certificate_required: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    tax_types: Optional[List[TaxType]] = None
    jurisdictions: Optional[List[TaxJurisdiction]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class TaxExemptionInDBBase(TaxExemptionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID
    is_active: bool

    class Config:
        from_attributes = True

class TaxExemption(TaxExemptionInDBBase):
    pass

class TaxExemptionInDB(TaxExemptionInDBBase):
    pass
