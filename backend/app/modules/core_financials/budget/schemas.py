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
