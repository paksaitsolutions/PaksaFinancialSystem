from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db.base import BaseModel

class Budget(BaseModel):
    __tablename__ = 'budgets'
    
    name = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(String(50), nullable=False)  # OPERATIONAL, CAPITAL, PROJECT, DEPARTMENT
    status = Column(String(50), default='DRAFT')  # DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, ARCHIVED
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text)
    
    # Approval workflow fields
    submitted_at = Column(DateTime)
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    approval_notes = Column(Text)
    rejection_reason = Column(Text)
    
    # Relationships
    line_items = relationship("BudgetLineItem", back_populates="budget", cascade="all, delete-orphan")

class BudgetLineItem(BaseModel):
    __tablename__ = 'budget_line_items'
    
    budget_id = Column(Integer, ForeignKey('budgets.id'), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    budget = relationship("Budget", back_populates="line_items")