from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # OPERATIONAL, CAPITAL, PROJECT, DEPARTMENT
    amount = Column(Numeric(15, 2), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    status = Column(String(50), default="DRAFT")  # DRAFT, PENDING_APPROVAL, APPROVED, REJECTED
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    line_items = relationship("BudgetLineItem", back_populates="budget", cascade="all, delete-orphan")
    actuals = relationship("BudgetActual", back_populates="budget", cascade="all, delete-orphan")

class BudgetLineItem(Base):
    __tablename__ = "budget_line_items"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    amount = Column(Numeric(15, 2), nullable=False)

    # Relationships
    budget = relationship("Budget", back_populates="line_items")

class BudgetActual(Base):
    __tablename__ = "budget_actuals"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    category = Column(String(100), nullable=False)
    actual_amount = Column(Numeric(15, 2), nullable=False)
    period_date = Column(DateTime, nullable=False)

    # Relationships
    budget = relationship("Budget", back_populates="actuals")

class BudgetApproval(Base):
    __tablename__ = "budget_approvals"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    action = Column(String(20), nullable=False)  # APPROVED, REJECTED
    notes = Column(Text)
    approved_by = Column(String(255), nullable=False)
    approved_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    budget = relationship("Budget")