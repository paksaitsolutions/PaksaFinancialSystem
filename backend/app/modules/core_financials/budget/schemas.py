from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

class BudgetLineItemBase(BaseModel):
    category: str = Field(..., max_length=100)
    description: str = Field(..., max_length=255)
    amount: Decimal = Field(..., ge=0)

class BudgetLineItemCreate(BudgetLineItemBase):
    pass

class BudgetLineItem(BudgetLineItemBase):
    id: int
    budget_id: int
    
    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    name: str = Field(..., max_length=255)
    amount: Decimal = Field(..., ge=0)
    type: str = Field(..., max_length=50)
    status: str = Field(default="DRAFT", max_length=50)
    start_date: date
    end_date: date
    description: Optional[str] = None

class BudgetCreate(BudgetBase):
    line_items: List[BudgetLineItemCreate] = []

class BudgetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    amount: Optional[Decimal] = Field(None, ge=0)
    type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    line_items: Optional[List[BudgetLineItemCreate]] = None

class Budget(BudgetBase):
    id: int
    line_items: List[BudgetLineItem] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

class BudgetVsActualLineItem(BaseModel):
    category: str
    budgetAmount: float
    actualAmount: float
    variance: float

class BudgetVsActual(BaseModel):
    budgetId: str
    period: str
    budgetAmount: float
    actualAmount: float
    variance: float
    variancePercent: float
    lineItems: List[BudgetVsActualLineItem]