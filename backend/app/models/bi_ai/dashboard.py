"""
BI/AI Dashboard models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base

class Dashboard(Base):
    """Dashboard configuration model."""
    
    __tablename__ = "dashboard"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    layout_config = Column(JSON)  # Dashboard layout and widget positions
    
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KPI(Base):
    """Custom KPI model."""
    
    __tablename__ = "kpi"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    formula = Column(Text, nullable=False)  # SQL or calculation formula
    target_value = Column(String(50))
    unit = Column(String(20))  # currency, percentage, count, etc.
    
    category = Column(String(100))  # financial, operational, hr, etc.
    refresh_frequency = Column(String(20), default="daily")  # real-time, hourly, daily, weekly
    
    is_active = Column(Boolean, default=True)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Anomaly(Base):
    """Anomaly detection result model."""
    
    __tablename__ = "anomaly"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    metric_name = Column(String(200), nullable=False)
    metric_value = Column(String(100), nullable=False)
    expected_range = Column(String(100))
    anomaly_score = Column(String(20))  # 0-1 confidence score
    
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="open")  # open, investigating, resolved, false_positive
    
    description = Column(Text)
    recommendation = Column(Text)
    
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class Prediction(Base):
    """AI prediction model."""
    
    __tablename__ = "prediction"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    prediction_type = Column(String(100), nullable=False)  # revenue_forecast, cash_flow, etc.
    target_metric = Column(String(200), nullable=False)
    
    prediction_data = Column(JSON)  # Prediction results and confidence intervals
    confidence_score = Column(String(20))
    
    prediction_period = Column(String(50))  # next_month, next_quarter, next_year
    model_used = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)