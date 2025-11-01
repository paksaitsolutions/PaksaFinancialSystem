"""
Schemas for vendor API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator

from app.models.enums import VendorStatus, PaymentTerms

class VendorContactBase(BaseModel):
    """Base schema for vendor contact."""
    name: str
    position: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_primary: bool = False

class VendorContactCreate(VendorContactBase):
    """Schema for creating a vendor contact."""
    pass

class VendorContactUpdate(VendorContactBase):
    """Schema for updating a vendor contact."""
    name: Optional[str] = None

class VendorContactResponse(VendorContactBase):
    """Schema for vendor contact response."""
    id: UUID
    vendor_id: UUID

    class Config:
        orm_mode = True

class VendorBase(BaseModel):
    """Base schema for vendor."""
    code: str
    name: str
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    status: VendorStatus = VendorStatus.ACTIVE
    
    # Contact information
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    
    # Address
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    # Payment information
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    currency_id: Optional[UUID] = None
    default_account_id: Optional[UUID] = None
    
    # 1099 reporting
    is_1099: bool = False
    tax_classification: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None

class VendorCreate(VendorBase):
    """Schema for creating a vendor."""
    contacts: Optional[List[VendorContactCreate]] = None

class VendorUpdate(BaseModel):
    """Schema for updating a vendor."""
    code: Optional[str] = None
    name: Optional[str] = None
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    status: Optional[VendorStatus] = None
    
    # Contact information
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    
    # Address
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    # Payment information
    payment_terms: Optional[PaymentTerms] = None
    currency_id: Optional[UUID] = None
    default_account_id: Optional[UUID] = None
    
    # 1099 reporting
    is_1099: Optional[bool] = None
    tax_classification: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None

class VendorResponse(VendorBase):
    """Schema for vendor response."""
    id: UUID
    contacts: List[VendorContactResponse] = []

    class Config:
        orm_mode = True

class VendorListResponse(BaseModel):
    """Schema for vendor list response."""
    items: List[VendorResponse]
    total: int
    page: int
    page_size: int
    pages: int