from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date
from uuid import UUID
from enum import Enum

class PaymentMethod(str, Enum):
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    ACH = "ach"

class PaymentBase(BaseModel):
    customer_id: UUID
    invoice_id: UUID
    amount: Decimal
    payment_date: date
    payment_method: PaymentMethod
    reference: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: UUID
    payment_number: str
    
    class Config:
        from_attributes = True