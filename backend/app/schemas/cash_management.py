from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class BankAccountBase(BaseModel):
    name: str
    account_number: str
    account_type: str
    bank_name: str
    routing_number: Optional[str] = None

class BankAccountCreate(BankAccountBase):
    current_balance: Optional[Decimal] = 0.00

class BankAccountUpdate(BaseModel):
    name: Optional[str] = None
    bank_name: Optional[str] = None
    is_active: Optional[bool] = None

class BankAccountResponse(BankAccountBase):
    id: str
    current_balance: Decimal
    available_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    account_id: str
    transaction_date: datetime
    transaction_type: str
    amount: Decimal
    memo: Optional[str] = None
    payee: Optional[str] = None
    payment_method: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: str
    status: str
    reference_number: Optional[str]
    running_balance: Optional[Decimal]
    is_reconciled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CashFlowSummary(BaseModel):
    total_balance: float
    account_count: int
    recent_transactions: int
    pending_transactions: int