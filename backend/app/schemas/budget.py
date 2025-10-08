from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class BudgetLineItemBase(BaseModel):
    category: str
    description: Optional[str] = None
    amount: Decimal

class BudgetLineItemCreate(BudgetLineItemBase):
    pass

class BudgetLineItem(BudgetLineItemBase):
    id: int
    budget_id: int

    class Config:
        from_attributes = True

class BudgetActualBase(BaseModel):
    category: str
    actual_amount: Decimal
    period_date: datetime

class BudgetActualCreate(BudgetActualBase):
    pass

class BudgetActual(BudgetActualBase):
    id: int
    budget_id: int

    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    name: str
    type: str
    amount: Decimal
    period_start: datetime
    period_end: datetime
    status: str = "DRAFT"
    description: Optional[str] = None

class BudgetCreate(BudgetBase):
    line_items: List[BudgetLineItemCreate] = []

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[Decimal] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    status: Optional[str] = None
    description: Optional[str] = None

class Budget(BudgetBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    line_items: List[BudgetLineItem] = []
    actuals: List[BudgetActual] = []

    class Config:
        from_attributes = True

class BudgetSummary(BaseModel):
    total_budgets: int
    total_amount: Decimal
    approved_amount: Decimal
    pending_amount: Decimal
    utilization_rate: float

class BudgetVariance(BaseModel):
    category: str
    budget: Decimal
    actual: Decimal
    variance: Decimal
    variance_percent: float
    status: str