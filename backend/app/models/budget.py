from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class BudgetPlan(Base):
    __tablename__ = "budget_plans"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    plan_name = Column(String(255), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_budget = Column(Decimal(15, 2), default=0)
    status = Column(String(20), default="draft")
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BudgetLine(Base):
    __tablename__ = "budget_lines"
    
    id = Column(String, primary_key=True)
    budget_plan_id = Column(String, ForeignKey("budget_plans.id"), nullable=False)
    account_id = Column(String, ForeignKey("chart_of_accounts.id"), nullable=False)
    department = Column(String(100))
    budgeted_amount = Column(Decimal(15, 2), default=0)
    actual_amount = Column(Decimal(15, 2), default=0)
    variance = Column(Decimal(15, 2), default=0)
    notes = Column(Text)

class BudgetForecast(Base):
    __tablename__ = "budget_forecasts"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    forecast_name = Column(String(255), nullable=False)
    forecast_period = Column(String(50))
    projected_revenue = Column(Decimal(15, 2), default=0)
    projected_expenses = Column(Decimal(15, 2), default=0)
    net_projection = Column(Decimal(15, 2), default=0)
    confidence_level = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

class BudgetScenario(Base):
    __tablename__ = "budget_scenarios"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    scenario_name = Column(String(255), nullable=False)
    scenario_type = Column(String(50))  # optimistic, pessimistic, realistic
    base_budget_id = Column(String, ForeignKey("budget_plans.id"))
    adjustment_factor = Column(Decimal(5, 2), default=1.0)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class BudgetApproval(Base):
    __tablename__ = "budget_approvals"
    
    id = Column(String, primary_key=True)
    budget_plan_id = Column(String, ForeignKey("budget_plans.id"), nullable=False)
    approver_id = Column(String, ForeignKey("users.id"), nullable=False)
    approval_level = Column(Integer, default=1)
    status = Column(String(20), default="pending")
    comments = Column(Text)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)