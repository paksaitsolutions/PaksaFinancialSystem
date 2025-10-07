"""
AI Assistant schemas.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class AIAssistantBase(BaseModel):
    """Base AI assistant schema."""
    name: str
    description: Optional[str] = None
    language: str = "en"
    ai_model_config: Optional[Dict[str, Any]] = None
    training_data: Optional[Dict[str, Any]] = None
    custom_prompts: Optional[Dict[str, Any]] = None
    enabled_features: Optional[List[str]] = None
    workflow_templates: Optional[Dict[str, Any]] = None
    is_active: bool = True

class AIAssistantCreate(AIAssistantBase):
    """Create AI assistant schema."""
    pass

class AIAssistantResponse(AIAssistantBase):
    """AI assistant response schema."""
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ChatSessionBase(BaseModel):
    """Base chat session schema."""
    session_name: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

class ChatSessionCreate(ChatSessionBase):
    """Create chat session schema."""
    pass

class ChatSessionResponse(ChatSessionBase):
    """Chat session response schema."""
    id: UUID
    tenant_id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    last_activity: datetime

    model_config = {"from_attributes": True}

class ChatMessageBase(BaseModel):
    """Base chat message schema."""
    message_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatMessageCreate(ChatMessageBase):
    """Create chat message schema."""
    pass

class ChatMessageResponse(ChatMessageBase):
    """Chat message response schema."""
    id: UUID
    session_id: UUID
    confidence_score: Optional[str] = None
    processing_time: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str
    session_id: Optional[UUID] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Chat response schema."""
    response: str
    session_id: UUID
    confidence: float
    suggestions: Optional[List[str]] = None
    actions: Optional[List[Dict[str, Any]]] = None

class AIWorkflowBase(BaseModel):
    """Base AI workflow schema."""
    name: str
    description: Optional[str] = None
    trigger_keywords: List[str]
    workflow_steps: Dict[str, Any]
    response_template: str
    is_active: bool = True

class AIWorkflowCreate(AIWorkflowBase):
    """Create AI workflow schema."""
    pass

class AIWorkflowResponse(AIWorkflowBase):
    """AI workflow response schema."""
    id: UUID
    tenant_id: UUID
    usage_count: int
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}

class AIAnalyticsData(BaseModel):
    """AI analytics data schema."""
    total_conversations: int
    total_messages: int
    avg_response_time: float
    user_satisfaction: float
    top_queries: List[Dict[str, Any]]
    language_distribution: Dict[str, int]
    workflow_usage: List[Dict[str, Any]]