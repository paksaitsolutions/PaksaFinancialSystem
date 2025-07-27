from sqlalchemy import Column, String, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, GUID

class Budget(BaseModel):
    __tablename__ = "budgets"
    
    tenant_id = Column(GUID(), nullable=False, index=True)
    budget_name = Column(String(200), nullable=False)
    budget_year = Column(Integer, nullable=False)
    budget_period = Column(String(50))  # annual, quarterly, monthly
    total_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='draft')  # draft, approved, active
    
    # Relationships
    line_items = relationship("BudgetLineItem", back_populates="budget", cascade="all, delete-orphan")

class BudgetLineItem(BaseModel):
    __tablename__ = "budget_line_items"
    
    tenant_id = Column(GUID(), nullable=False, index=True)
    budget_id = Column(GUID(), ForeignKey('budgets.id'), nullable=False)
    account_id = Column(GUID(), nullable=False)
    account_name = Column(String(200))
    budgeted_amount = Column(Numeric(15, 2), default=0)
    actual_amount = Column(Numeric(15, 2), default=0)
    variance = Column(Numeric(15, 2), default=0)
    
    # Relationships
    budget = relationship("Budget", back_populates="line_items")