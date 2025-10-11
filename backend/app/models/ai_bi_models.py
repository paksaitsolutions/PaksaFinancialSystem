"""
AI/BI Module Database Models
"""
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.core_models import Company
from app.models.base import Base, AuditMixin


class AIInsight(Base, AuditMixin):
    __tablename__ = "ai_insights"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    insight_type = Column(String(50), nullable=False)  # anomaly, prediction, recommendation
    module = Column(String(50), nullable=False)  # gl, ap, ar, cash, etc.
    priority = Column(String(20), default="Medium")  # High, Medium, Low
    confidence_score = Column(Float, default=0.0)
    status = Column(String(20), default="Active")  # Active, Dismissed, Applied
    meta_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIRecommendation(Base, AuditMixin):
    __tablename__ = "ai_recommendations"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    recommendation_type = Column(String(50), nullable=False)
    module = Column(String(50), nullable=False)
    priority = Column(String(20), default="Medium")
    confidence_score = Column(Float, default=0.0)
    estimated_impact = Column(Float, default=0.0)
    action_items = Column(JSON, default=[])
    status = Column(String(20), default="Pending")  # Pending, Applied, Dismissed
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIAnomaly(Base, AuditMixin):
    __tablename__ = "ai_anomalies"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    anomaly_type = Column(String(50), nullable=False)
    module = Column(String(50), nullable=False)
    severity = Column(String(20), default="Medium")  # Critical, High, Medium, Low
    anomaly_score = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    affected_records = Column(JSON, default=[])
    status = Column(String(20), default="Open")  # Open, Investigating, Resolved, False_Positive
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIPrediction(Base, AuditMixin):
    __tablename__ = "ai_predictions"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    prediction_type = Column(String(50), nullable=False)  # cash_flow, revenue, expense
    module = Column(String(50), nullable=False)
    target_date = Column(DateTime, nullable=False)
    predicted_value = Column(Float, nullable=False)
    confidence_interval = Column(JSON, default={})  # {"lower": 0.0, "upper": 0.0}
    accuracy_score = Column(Float, default=0.0)
    model_version = Column(String(50), nullable=False)
    input_features = Column(JSON, default={})
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIModelMetrics(Base, AuditMixin):
    __tablename__ = "ai_model_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # classification, regression, clustering
    version = Column(String(20), nullable=False)
    accuracy = Column(Float, default=0.0)
    precision = Column(Float, default=0.0)
    recall = Column(Float, default=0.0)
    f1_score = Column(Float, default=0.0)
    training_data_size = Column(Integer, default=0)
    last_trained = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    hyperparameters = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIAnalyticsReport(Base, AuditMixin):
    __tablename__ = "ai_analytics_reports"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)
    module = Column(String(50), nullable=False)
    data_range_start = Column(DateTime, nullable=False)
    data_range_end = Column(DateTime, nullable=False)
    report_data = Column(JSON, nullable=False)
    insights_count = Column(Integer, default=0)
    anomalies_count = Column(Integer, default=0)
    recommendations_count = Column(Integer, default=0)
    generated_by = Column(String(100), nullable=False)
    status = Column(String(20), default="Generated")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)