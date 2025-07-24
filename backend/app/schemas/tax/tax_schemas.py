"""
Schemas for tax management.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class TaxRateBase(BaseModel):
    """Base schema for tax rate."""
    name: str
    code: str
    rate: Decimal
    tax_type: str
    jurisdiction: Optional[str] = None
    effective_date: date
    expiry_date: Optional[date] = None
    is_active: bool = True
    description: Optional[str] = None

class TaxRateCreate(TaxRateBase):
    """Schema for creating a tax rate."""
    pass

class TaxRateUpdate(BaseModel):
    """Schema for updating a tax rate."""
    name: Optional[str] = None
    rate: Optional[Decimal] = None
    tax_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None

class TaxRateResponse(TaxRateBase):
    """Schema for tax rate response."""
    id: UUID

    class Config:
        orm_mode = True

class TaxExemptionBase(BaseModel):
    """Base schema for tax exemption."""
    certificate_number: str
    entity_type: str
    entity_id: UUID
    exemption_type: str
    tax_type: str
    jurisdiction: Optional[str] = None
    issue_date: date
    expiry_date: Optional[date] = None
    is_active: bool = True
    notes: Optional[str] = None

class TaxExemptionCreate(TaxExemptionBase):
    """Schema for creating a tax exemption."""
    pass

class TaxExemptionUpdate(BaseModel):
    """Schema for updating a tax exemption."""
    exemption_type: Optional[str] = None
    tax_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    expiry_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class TaxExemptionResponse(TaxExemptionBase):
    """Schema for tax exemption response."""
    id: UUID

    class Config:
        orm_mode = True

class TaxPolicyBase(BaseModel):
    """Base schema for tax policy."""
    name: str
    policy_type: str
    tax_rate_id: UUID
    conditions: Optional[str] = None
    priority: Decimal = 1
    is_active: bool = True

class TaxPolicyCreate(TaxPolicyBase):
    """Schema for creating a tax policy."""
    pass

class TaxPolicyUpdate(BaseModel):
    """Schema for updating a tax policy."""
    name: Optional[str] = None
    policy_type: Optional[str] = None
    tax_rate_id: Optional[UUID] = None
    conditions: Optional[str] = None
    priority: Optional[Decimal] = None
    is_active: Optional[bool] = None

class TaxPolicyResponse(TaxPolicyBase):
    """Schema for tax policy response."""
    id: UUID
    tax_rate: Optional[TaxRateResponse] = None

    class Config:
        orm_mode = True

class TaxCalculationRequest(BaseModel):
    """Schema for tax calculation request."""
    amount: Decimal
    tax_type: str
    jurisdiction: Optional[str] = None
    entity_id: Optional[UUID] = None
    entity_type: Optional[str] = None

class TaxCalculationResponse(BaseModel):
    """Schema for tax calculation response."""
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    tax_rate: Decimal
    tax_details: List[dict]
    exemptions_applied: List[dict]