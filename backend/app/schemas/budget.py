from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class BudgetLineItemBase(BaseModel):
    account_code: str
    account_name: str
    category: Optional[str] = None
    budgeted_amount: Decimal

class BudgetLineItemCreate(BudgetLineItemBase):
    pass

class BudgetLineItem(BudgetLineItemBase):
    id: int
    budget_id: int
    actual_amount: Decimal = 0
    variance: Decimal = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    name: str
    description: Optional[str] = None
    fiscal_year: int
    start_date: datetime
    end_date: datetime

class BudgetCreate(BudgetBase):
    line_items: List[BudgetLineItemCreate] = []

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    line_items: Optional[List[BudgetLineItemCreate]] = None

class Budget(BudgetBase):
    id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    line_items: List[BudgetLineItem] = []

    class Config:
        from_attributes = True

class BudgetApprovalBase(BaseModel):
    status: str
    comments: Optional[str] = None

class BudgetApprovalCreate(BudgetApprovalBase):
    budget_id: int
    approver_id: int

class BudgetApproval(BudgetApprovalBase):
    id: int
    budget_id: int
    approver_id: int
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True