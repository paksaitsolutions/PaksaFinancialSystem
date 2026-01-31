"""
Module Interface for AI Assistant Integration
Defines the interface that all modules must implement to integrate with the AI assistant.
"""
from typing import Dict, List, Any, Optional

from abc import ABC, abstractmethod
from pydantic import BaseModel


class ModuleResponse(BaseModel):
    """Standard response format for module handlers"""
    response: str
    context_updates: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[Dict[str, str]]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    requires_confirmation: bool = False

class AIResponse(BaseModel):
    """AI response format"""
    answer: str
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    actions: Optional[List[Dict[str, Any]]] = None

class AIModule(ABC):
    """Abstract base class for AI module integration"""
    
    @property
    @abstractmethod
    def module_name(self) -> str:
        """Module Name."""
        """Return the name of the module"""
        pass
    
    @abstractmethod
    async def handle_query(self, query: str, context: Dict[str, Any]) -> ModuleResponse:
        """Handle Query."""
        """
        Handle a user query within this module's context
        
        Args:
            query: The user's query
            context: Current context including user, session, and module data
            
        Returns:
            ModuleResponse containing the assistant's response and any additional data
        """
        pass
    
    @abstractmethod
    async def get_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get Suggestions."""
        """
        Get contextual suggestions for the current state
        
        Args:
            context: Current context including user, session, and module data
            
        Returns:
            List of suggestion objects with text and type
        """
        pass
    
    async def get_module_info(self) -> Dict[str, Any]:
        """Get Module Info."""
        """
        Get information about this module's capabilities
        
        Returns:
            Dictionary containing module metadata and capabilities
        """
        return {
            "name": self.module_name,
            "description": "No description available",
            "capabilities": []
        }
