from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal
from datetime import date
from uuid import UUID

class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    payment_terms: int = 30
    is_active: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class Customer(CustomerBase):
    id: UUID
    customer_code: str
    balance: Decimal = Decimal("0.00")
    created_at: date
    
    class Config:
        from_attributes = True