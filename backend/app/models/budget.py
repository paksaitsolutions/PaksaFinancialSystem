from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum
from pydantic import BaseModel

from .base import Base
from .account import Account
from .department import Department
from .project import Project

class BudgetStatus(str, PyEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class BudgetType(str, PyEnum):
    OPERATIONAL = "operational"
    CAPITAL = "capital"
    PROJECT = "project"
    DEPARTMENT = "department"

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    budget_type = Column(Enum(BudgetType), nullable=False)
    status = Column(Enum(BudgetStatus), default=BudgetStatus.DRAFT)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=False)
    updated_by = Column(String)
    
    # Relationships
    lines = relationship("BudgetLine", back_populates="budget", cascade="all, delete-orphan")
    allocations = relationship("BudgetAllocation", back_populates="budget", cascade="all, delete-orphan")
    approvals = relationship("BudgetApproval", back_populates="budget", cascade="all, delete-orphan")

class BudgetLine(Base):
    __tablename__ = "budget_lines"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    amount = Column(Float, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    budget = relationship("Budget", back_populates="lines")
    account = relationship("Account")
    department = relationship("Department")
    project = relationship("Project")

class BudgetAllocation(Base):
    __tablename__ = "budget_allocations"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    amount = Column(Float, nullable=False)
    percentage = Column(Float)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    budget = relationship("Budget", back_populates="allocations")
    department = relationship("Department")
    project = relationship("Project")

class BudgetApproval(Base):
    __tablename__ = "budget_approvals"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    approver_id = Column(String, nullable=False)
    approved_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String)
    
    # Relationships
    budget = relationship("Budget", back_populates="approvals")

class BudgetRule(Base):
    __tablename__ = "budget_rules"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    rule_type = Column(String, nullable=False)
    rule_data = Column(JSON, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    budget = relationship("Budget", back_populates="rules")
