"""
AI Assistant models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base

class AIAssistant(Base):
    """AI Assistant configuration model."""
    
    __tablename__ = "ai_assistant"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    language = Column(String(10), default="en")
    
    # AI Configuration
    model_config = Column(JSON)  # AI model settings
    training_data = Column(JSON)  # Company-specific training data
    custom_prompts = Column(JSON)  # Custom prompt templates
    
    # Capabilities
    enabled_features = Column(JSON)  # List of enabled features
    workflow_templates = Column(JSON)  # Custom workflow definitions
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatSession(Base):
    """Chat session model."""
    
    __tablename__ = "chat_session"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    session_name = Column(String(200))
    context_data = Column(JSON)  # Session context and variables
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    """Chat message model."""
    
    __tablename__ = "chat_message"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    message_type = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata = Column(JSON)  # Additional message metadata
    
    # AI Response data
    confidence_score = Column(String(10))
    processing_time = Column(Integer)  # milliseconds
    
    created_at = Column(DateTime, default=datetime.utcnow)

class AIWorkflow(Base):
    """AI workflow model."""
    
    __tablename__ = "ai_workflow"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    trigger_keywords = Column(JSON)  # Keywords that trigger this workflow
    
    workflow_steps = Column(JSON)  # Workflow definition
    response_template = Column(Text)
    
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AIAnalytics(Base):
    """AI analytics model."""
    
    __tablename__ = "ai_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(String(100), nullable=False)
    metric_data = Column(JSON)
    
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)