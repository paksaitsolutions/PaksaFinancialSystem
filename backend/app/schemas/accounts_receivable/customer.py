"""
Schemas for customer API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, EmailStr

from app.models.enums import CustomerStatus, PaymentTerms

class CustomerContactBase(BaseModel):
    """Base schema for customer contact."""
    name: str
    position: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_primary: bool = False

class CustomerContactCreate(CustomerContactBase):
    """Schema for creating a customer contact."""
    pass

class CustomerContactResponse(CustomerContactBase):
    """Schema for customer contact response."""
    id: UUID
    customer_id: UUID

    class Config:
        orm_mode = True

class CustomerBase(BaseModel):
    """Base schema for customer."""
    code: str
    name: str
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    status: CustomerStatus = CustomerStatus.ACTIVE
    
    # Contact information
    email: Optional[EmailStr] = None
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
    credit_limit: Optional[Decimal] = None
    
    # Notes
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    """Schema for creating a customer."""
    contacts: Optional[List[CustomerContactCreate]] = None

class CustomerUpdate(BaseModel):
    """Schema for updating a customer."""
    code: Optional[str] = None
    name: Optional[str] = None
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    status: Optional[CustomerStatus] = None
    
    # Contact information
    email: Optional[EmailStr] = None
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
    credit_limit: Optional[Decimal] = None
    
    # Notes
    notes: Optional[str] = None

class CustomerResponse(CustomerBase):
    """Schema for customer response."""
    id: UUID
    contacts: List[CustomerContactResponse] = []

    class Config:
        orm_mode = True