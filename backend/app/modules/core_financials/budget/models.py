# -*- coding: utf-8 -*-
"""
Paksa Financial System - Budget Models
-------------------------------------
Version: 1.0
Author: Paksa IT Solutions
Copyright © 2023 Paksa IT Solutions
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Budget(Base):
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
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
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)  # FK to users table
    
    # Relationships
    line_items = relationship("BudgetLineItem", back_populates="budget", cascade="all, delete-orphan")

class BudgetLineItem(Base):
    __tablename__ = 'budget_line_items'
    
    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey('budgets.id'), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    budget = relationship("Budget", back_populates="line_items")