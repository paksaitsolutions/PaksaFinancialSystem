"""
AI Assistant Service - Initializes and manages all AI modules
"""
from typing import Dict, Type, Optional
from pathlib import Path
import logging

from app.services.ai.assistant import AIAssistant
from app.modules.payroll.ai_integration import PayrollAIModule
from app.modules.tax.ai_integration import TaxAIModule
from app.modules.fixed_assets.ai_integration import FixedAssetsAIModule

logger = logging.getLogger(__name__)

class AIAssistantManager:
    """Manages the initialization and access to the AI Assistant with all registered modules."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIAssistantManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.assistant = AIAssistant()
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Initialize all AI modules and register them with the assistant."""
        try:
            # Register all AI modules
            self.assistant.register_module('payroll', PayrollAIModule())
            self.assistant.register_module('tax', TaxAIModule())
            self.assistant.register_module('fixed_assets', FixedAssetsAIModule())
            
            logger.info("AI modules initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI modules: {str(e)}", exc_info=True)
            raise
    
    def get_assistant(self) -> AIAssistant:
        """Get the initialized AI assistant instance."""
        return self.assistant

# Create a singleton instance of the AI Assistant Manager
ai_assistant_manager = AIAssistantManager()

def get_ai_assistant() -> AIAssistant:
    """Dependency function to get the AI assistant instance."""
    return ai_assistant_manager.get_assistant()
