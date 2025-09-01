"""
Budget models placeholder (conflicts resolved).
"""
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

from sqlalchemy import Column, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from .....database import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget_type = Column(String, nullable=False) # e.g., 'operational', 'capital'
    status = Column(String, default='active') # e.g., 'active', 'archived'
    created_by = Column(UUID(as_uuid=True), nullable=False)

    items = relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")
    adjustments = relationship("BudgetAdjustment", back_populates="budget")

class BudgetItem(Base):
    __tablename__ = "budget_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey('budgets.id'), nullable=False)
    account_id = Column(UUID(as_uuid=True), nullable=False) # FK to ChartOfAccounts
    amount = Column(Float, nullable=False)
    description = Column(String)

    budget = relationship("Budget", back_populates="items")
    transactions = relationship("BudgetTransaction", back_populates="item")

class BudgetAdjustment(Base):
    __tablename__ = "budget_adjustments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey('budgets.id'), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey('budget_items.id'), nullable=False)
    adjustment_amount = Column(Float, nullable=False)
    reason = Column(String, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    budget = relationship("Budget", back_populates="adjustments")

class BudgetTransaction(Base):
    __tablename__ = "budget_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey('budget_items.id'), nullable=False)
    transaction_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String)
    # Link to an actual transaction (e.g., from GL or AP)
    # related_transaction_id = Column(UUID(as_uuid=True))

    item = relationship("BudgetItem", back_populates="transactions")
=======
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
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
