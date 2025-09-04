"""
AI Assistant API Endpoints
Handles all AI assistant related API requests
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ....services.ai.assistant import AIAssistant
from ....services.ai.ai_assistant import get_ai_assistant
from ....services.ai.module_interface import ModuleResponse
from ....core.security import get_current_user
from ....models.user import User

router = APIRouter(tags=["AI Assistant"])
logger = logging.getLogger(__name__)

class AIQueryRequest(BaseModel):
    """Request model for AI assistant queries"""
    query: str = Field(..., description="The user's query to the AI assistant")
    module: Optional[str] = Field(
        None, 
        description="Optional module to route the query to (e.g., 'payroll', 'tax', 'fixed_assets')"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional context for the AI to consider when processing the query"
    )

class AISuggestionRequest(BaseModel):
    """Request model for getting AI suggestions"""
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Contextual information to help generate relevant suggestions"
    )

@router.post("/query", response_model=ModuleResponse)
async def process_query(
    request: AIQueryRequest,
    current_user: User = Depends(get_current_user),
    assistant: AIAssistant = Depends(get_ai_assistant)
) -> ModuleResponse:
    """
    Process a user query with the AI assistant and return a response.
    
    This endpoint routes the query to the appropriate AI module based on the content
    or the specified module parameter.
    """
    try:
        # Set up context with user information
        context = {
            "user_id": str(current_user.id),
            "user_email": current_user.email,
            "user_roles": current_user.roles,
            "timestamp": datetime.utcnow().isoformat(),
            "module": request.module,  # Pass the requested module to the context
            **(request.context or {})
        }
        
        logger.info(
            f"Processing AI query from user {current_user.email} "
            f"(module: {request.module or 'auto'})"
        )
        
        # Process the query
        response = await assistant.process_query(
            query=request.query,
            context=context,
            module=request.module  # Pass the module to assistant
        )
        
        return response
        
    except ValueError as e:
        # Handle known errors (e.g., module not found)
        logger.warning(f"Validation error in AI query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing AI query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )

@router.get("/suggestions", response_model=List[Dict[str, str]])
async def get_suggestions(
    module: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    assistant: AIAssistant = Depends(get_ai_assistant)
) -> List[Dict[str, str]]:
    """
    Get contextual suggestions from the AI assistant.
    
    Args:
        module: Optional module to get suggestions for (e.g., 'payroll', 'tax')
        context: Additional context to help generate relevant suggestions
    """
    try:
        # Set up context with user information
        full_context = {
            "user_id": str(current_user.id),
            "user_email": current_user.email,
            "user_roles": current_user.roles,
            "timestamp": datetime.utcnow().isoformat(),
            "module": module,  # Include the module in the context
            **(context or {})
        }
        
        logger.info(
            f"Getting AI suggestions for user {current_user.email} "
            f"(module: {module or 'all'})"
        )
        
        # Get suggestions, optionally filtered by module
        suggestions = await assistant.get_suggestions(
            context=full_context,
            module=module
        )
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting AI suggestions: {str(e)}", exc_info=True)
        # Return a generic error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting suggestions."
        )

@router.get("/modules")
async def list_available_modules(
    assistant: AIAssistant = Depends(get_ai_assistant)
) -> Dict[str, Any]:
    """
    List all available AI modules and their capabilities.
    
    Returns a dictionary where keys are module names and values are
    module information including description and capabilities.
    """
    try:
        modules_info = {}
        for module_name, module in assistant.modules.items():
            try:
                module_info = await module.get_module_info()
                modules_info[module_name] = module_info
            except Exception as module_error:
                logger.error(
                    f"Error getting info for module {module_name}: {str(module_error)}",
                    exc_info=True
                )
                modules_info[module_name] = {
                    "error": "Failed to load module information"
                }
        
        return {
            "modules": modules_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing AI modules: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving module information."
        )
