from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import date
from enum import Enum

class BudgetStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class BudgetType(str, Enum):
    OPERATIONAL = "operational"
    CAPITAL = "capital"
    PROJECT = "project"
    DEPARTMENT = "department"

class BudgetBase(BaseModel):
    name: str
    description: Optional[str] = None
    budget_type: BudgetType
    start_date: date
    end_date: date
    total_amount: float

class BudgetLineBase(BaseModel):
    account_id: int
    department_id: Optional[int] = None
    project_id: Optional[int] = None
    amount: float
    description: Optional[str] = None

class BudgetAllocationBase(BaseModel):
    department_id: Optional[int] = None
    project_id: Optional[int] = None
    amount: float
    percentage: Optional[float] = None
    description: Optional[str] = None

class BudgetRuleBase(BaseModel):
    rule_type: str
    rule_data: Dict
    description: Optional[str] = None

class BudgetCreate(BudgetBase):
    lines: List[BudgetLineBase]
    allocations: List[BudgetAllocationBase]
    rules: List[BudgetRuleBase]

class BudgetUpdate(BudgetBase):
    status: Optional[BudgetStatus] = None
    lines: Optional[List[BudgetLineBase]] = None
    allocations: Optional[List[BudgetAllocationBase]] = None
    rules: Optional[List[BudgetRuleBase]] = None

class BudgetApprovalBase(BaseModel):
    approver_id: str
    notes: Optional[str] = None

class BudgetApprovalCreate(BudgetApprovalBase):
    pass

class BudgetLine(BudgetLineBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BudgetAllocation(BudgetAllocationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BudgetRule(BudgetRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BudgetApproval(BudgetApprovalBase):
    id: int
    approved_at: datetime

    class Config:
        orm_mode = True

class Budget(BudgetBase):
    id: int
    status: BudgetStatus
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: Optional[str] = None
    lines: List[BudgetLine]
    allocations: List[BudgetAllocation]
    rules: List[BudgetRule]
    approvals: List[BudgetApproval]

    class Config:
        orm_mode = True

class BudgetResponse(Budget):
    pass

class BudgetListResponse(BaseModel):
    budgets: List[Budget]
    total: int
    page: int
    limit: int

    class Config:
        orm_mode = True
