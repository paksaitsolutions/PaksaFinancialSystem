from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, JSON
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class AIInsight(Base):
    __tablename__ = "ai_insights"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    insight_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    confidence_score = Column(Decimal(5, 2))
    data_source = Column(String(100))
    insight_data = Column(JSON)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class BIDashboard(Base):
    __tablename__ = "bi_dashboards"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    dashboard_name = Column(String(255), nullable=False)
    dashboard_type = Column(String(100))
    configuration = Column(JSON)
    widgets = Column(JSON)
    is_public = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Decimal(15, 2))
    metric_data = Column(JSON)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)