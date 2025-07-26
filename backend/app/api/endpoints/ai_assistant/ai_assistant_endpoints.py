"""
API endpoints for AI Assistant.
"""
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.db.router import db_router
from app.core.api_response import success_response, error_response
from app.core.permissions import require_permission, Permission
from app.crud.ai_assistant.ai_assistant_crud import ai_assistant_crud
from app.schemas.ai_assistant.ai_assistant_schemas import (
    AIAssistantCreate, AIAssistantResponse,
    ChatSessionCreate, ChatSessionResponse,
    ChatRequest, ChatResponse, ChatMessageResponse,
    AIWorkflowCreate, AIWorkflowResponse,
    AIAnalyticsData
)
from app.services.ai.advanced_nlp_service import AdvancedNLPService

router = APIRouter()

# Mock tenant and user IDs
MOCK_TENANT_ID = UUID("12345678-1234-5678-9012-123456789012")
MOCK_USER_ID = UUID("12345678-1234-5678-9012-123456789012")

# Initialize services
nlp_service = AdvancedNLPService()

# AI Assistant Configuration
@router.post("/configure", response_model=AIAssistantResponse, status_code=status.HTTP_201_CREATED)
async def configure_assistant(
    *,
    db: AsyncSession = Depends(get_db),
    assistant_in: AIAssistantCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Configure AI assistant for tenant."""
    assistant = await ai_assistant_crud.create_assistant(
        db, tenant_id=MOCK_TENANT_ID, obj_in=assistant_in
    )
    return success_response(
        data=assistant,
        message="AI assistant configured successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/configuration", response_model=AIAssistantResponse)
async def get_assistant_config(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get AI assistant configuration."""
    assistant = await ai_assistant_crud.get_assistant(db, tenant_id=MOCK_TENANT_ID)
    if not assistant:
        return error_response(
            message="AI assistant not configured",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return success_response(data=assistant)

# Chat Management
@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    *,
    db: AsyncSession = Depends(get_db),
    chat_request: ChatRequest,
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Chat with AI assistant."""
    response = await ai_assistant_crud.process_chat_message(
        db, tenant_id=MOCK_TENANT_ID, user_id=MOCK_USER_ID, chat_request=chat_request
    )
    return success_response(data=response)

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get user's chat sessions."""
    sessions = await ai_assistant_crud.get_user_sessions(
        db, tenant_id=MOCK_TENANT_ID, user_id=MOCK_USER_ID
    )
    return success_response(data=sessions)

@router.get("/sessions/{session_id}/history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    session_id: UUID,
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get chat history for session."""
    history = await ai_assistant_crud.get_chat_history(db, session_id=session_id)
    return success_response(data=history)

# AI Workflows
@router.post("/workflows", response_model=AIWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    *,
    db: AsyncSession = Depends(get_db),
    workflow_in: AIWorkflowCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create AI workflow."""
    workflow = await ai_assistant_crud.create_workflow(
        db, tenant_id=MOCK_TENANT_ID, created_by=MOCK_USER_ID, obj_in=workflow_in
    )
    return success_response(
        data=workflow,
        message="AI workflow created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/workflows", response_model=List[AIWorkflowResponse])
async def get_workflows(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get AI workflows."""
    workflows = await ai_assistant_crud.get_workflows(db, tenant_id=MOCK_TENANT_ID)
    return success_response(data=workflows)

# AI Analytics
@router.get("/analytics", response_model=AIAnalyticsData)
async def get_ai_analytics(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get AI analytics."""
    analytics = await ai_assistant_crud.get_ai_analytics(db, tenant_id=MOCK_TENANT_ID)
    return success_response(data=analytics)

# Advanced NLP endpoints
@router.post("/nlp/advanced-chat")
async def advanced_chat(
    *,
    db: AsyncSession = Depends(get_db),
    query: str,
    session_id: str = "default",
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Advanced chat with context awareness and multi-language support."""
    nlp_service = AdvancedNLPService()
    
    result = nlp_service.process_advanced_query(
        query=query,
        user_id=str(MOCK_USER_ID),
        session_id=session_id
    )
    
    # Store conversation in database
    await ai_assistant_crud.store_conversation(
        db, 
        tenant_id=MOCK_TENANT_ID,
        user_id=MOCK_USER_ID,
        session_id=session_id,
        query=query,
        response=result["response"],
        intent=result["intent"],
        entities=result["entities"]
    )
    
    return success_response(
        data=result,
        message="Advanced NLP processing completed"
    )

@router.post("/context/reset")
async def reset_conversation_context(
    *,
    session_id: str,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Reset conversation context for session."""
    nlp_service = AdvancedNLPService()
    
    # Clear context for user session
    context_key = f"{MOCK_USER_ID}_{session_id}"
    if context_key in nlp_service.conversation_context:
        del nlp_service.conversation_context[context_key]
    
    return success_response(
        message="Conversation context reset successfully"
    )

@router.get("/context/{session_id}")
async def get_conversation_context(
    *,
    session_id: str,
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get conversation context for session."""
    nlp_service = AdvancedNLPService()
    
    context = nlp_service._get_conversation_context(str(MOCK_USER_ID), session_id)
    
    return success_response(data=context)

# Multi-language support endpoints
@router.get("/languages/supported")
async def get_supported_languages(
    *,
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get supported languages."""
    languages = {
        "supported_languages": [
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "es", "name": "Spanish", "native_name": "Español"},
            {"code": "fr", "name": "French", "native_name": "Français"},
            {"code": "de", "name": "German", "native_name": "Deutsch"}
        ],
        "default_language": "en",
        "auto_detection": True
    }
    
    return success_response(data=languages)

@router.post("/translate")
async def translate_query(
    *,
    query: str,
    target_language: str = "en",
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Translate query to target language."""
    # Simple translation mapping (in production, use proper translation service)
    translations = {
        "es": {
            "revenue": "ingresos",
            "expenses": "gastos",
            "profit": "beneficio",
            "customer": "cliente",
            "show me": "muéstrame",
            "last month": "el mes pasado"
        },
        "fr": {
            "revenue": "revenus",
            "expenses": "dépenses",
            "profit": "profit",
            "customer": "client",
            "show me": "montrez-moi",
            "last month": "le mois dernier"
        }
    }
    
    translated_query = query
    if target_language in translations:
        for english_term, translated_term in translations[target_language].items():
            translated_query = translated_query.replace(english_term, translated_term)
    
    return success_response(
        data={
            "original_query": query,
            "translated_query": translated_query,
            "target_language": target_language
        }
    )

# Learning and adaptation endpoints
@router.post("/feedback")
async def provide_feedback(
    *,
    db: AsyncSession = Depends(get_db),
    session_id: str,
    message_id: str,
    feedback_type: str,  # positive, negative, correction
    feedback_text: str = None,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Provide feedback for AI learning."""
    feedback_data = {
        "session_id": session_id,
        "message_id": message_id,
        "feedback_type": feedback_type,
        "feedback_text": feedback_text,
        "user_id": str(MOCK_USER_ID),
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    # Store feedback for learning
    await ai_assistant_crud.store_feedback(
        db,
        tenant_id=MOCK_TENANT_ID,
        feedback_data=feedback_data
    )
    
    return success_response(
        data=feedback_data,
        message="Feedback recorded for AI learning"
    )

@router.get("/learning/stats")
async def get_learning_stats(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get AI learning statistics."""
    stats = await ai_assistant_crud.get_learning_stats(db, tenant_id=MOCK_TENANT_ID)
    
    return success_response(data=stats)