from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class BudgetForecast(Base):
    __tablename__ = "budget_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    period = Column(String(50), nullable=False)  # next_quarter, next_year, etc.
    method = Column(String(50), nullable=False)  # linear, exponential, etc.
    growth_rate = Column(Numeric(5, 2), default=0.0)
    total_forecast = Column(Numeric(15, 2), default=0.0)
    confidence_level = Column(Integer, default=0)
    risk_level = Column(String(20), default="Medium")
    status = Column(String(20), default="Draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    forecast_details = relationship("BudgetForecastDetail", back_populates="forecast", cascade="all, delete-orphan")

class BudgetForecastDetail(Base):
    __tablename__ = "budget_forecast_details"

    id = Column(Integer, primary_key=True, index=True)
    forecast_id = Column(Integer, ForeignKey("budget_forecasts.id"), nullable=False)
    period = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    historical_amount = Column(Numeric(15, 2), default=0.0)
    forecast_amount = Column(Numeric(15, 2), default=0.0)
    variance = Column(Numeric(15, 2), default=0.0)
    confidence = Column(Integer, default=0)

    # Relationships
    forecast = relationship("BudgetForecast", back_populates="forecast_details")

class BudgetScenario(Base):
    __tablename__ = "budget_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    forecast_id = Column(Integer, ForeignKey("budget_forecasts.id"), nullable=False)
    scenario_type = Column(String(20), nullable=False)  # optimistic, realistic, pessimistic
    growth_rate = Column(Numeric(5, 2), nullable=False)
    q1_amount = Column(Numeric(15, 2), default=0.0)
    q2_amount = Column(Numeric(15, 2), default=0.0)
    q3_amount = Column(Numeric(15, 2), default=0.0)
    q4_amount = Column(Numeric(15, 2), default=0.0)

    # Relationships
    forecast = relationship("BudgetForecast")