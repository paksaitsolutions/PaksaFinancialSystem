<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
Paksa Financial System
----------------------
Version: 1.0
Author: Paksa IT Solutions
Copyright © 2023 Paksa IT Solutions

This file is part of the Paksa Financial System.
It is subject to the terms and conditions defined in
file 'LICENSE', which is part of this source code package.
"""

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import date

# Base Schemas
class BudgetItemBase(BaseModel):
    account_id: UUID
    amount: float
    description: Optional[str] = None

class BudgetBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    budget_type: str
    status: str

# Create Schemas
class BudgetItemCreate(BudgetItemBase):
    pass

class BudgetCreate(BudgetBase):
    items: List[BudgetItemCreate] = []

# Update Schemas
class BudgetItemUpdate(BaseModel):
    account_id: Optional[UUID] = None
    amount: Optional[float] = None
    description: Optional[str] = None

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget_type: Optional[str] = None
    status: Optional[str] = None

# Response Schemas
class BudgetItem(BudgetItemBase):
    id: UUID
    budget_id: UUID

    class Config:
        orm_mode = True

class Budget(BudgetBase):
    id: UUID
    created_by: UUID
    items: List[BudgetItem] = []

    class Config:
        orm_mode = True

class BudgetList(BaseModel):
    items: List[Budget]
    total: int

# Other Schemas
class BudgetAdjustmentCreate(BaseModel):
    item_id: UUID
    adjustment_amount: float
    reason: str

class BudgetTransactionCreate(BaseModel):
    item_id: UUID
    transaction_date: date
    amount: float
    description: str
=======
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
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
