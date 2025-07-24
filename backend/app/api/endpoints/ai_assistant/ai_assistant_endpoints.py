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

router = APIRouter()

# Mock tenant and user IDs
MOCK_TENANT_ID = UUID("12345678-1234-5678-9012-123456789012")
MOCK_USER_ID = UUID("12345678-1234-5678-9012-123456789012")

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