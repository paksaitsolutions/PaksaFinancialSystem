"""
AI Assistant Service - Initializes and manages all AI modules
"""
from pathlib import Path
from typing import Dict, Type, Optional

import logging

from app.modules.fixed_assets.ai_integration import FixedAssetsAIModule
from app.modules.payroll.ai_integration import PayrollAIModule
from app.modules.tax.ai_integration import TaxAIModule
from app.services.ai.assistant import AIAssistant



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
        try:
            # Register modules directly without async
            self.assistant.modules = {
                'payroll': PayrollAIModule(),
                'tax': TaxAIModule(),
                'fixed_assets': FixedAssetsAIModule()
            }
            logger.info("AI modules initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI modules: {str(e)}", exc_info=True)
            # Don't raise to prevent startup failure
            pass
    
    def get_assistant(self) -> AIAssistant:
        return self.assistant

# Create a singleton instance of the AI Assistant Manager
ai_assistant_manager = AIAssistantManager()

def get_ai_assistant() -> AIAssistant:
    return ai_assistant_manager.get_assistant()
