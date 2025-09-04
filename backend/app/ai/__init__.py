"""
AI Assistant Initialization

Sets up and configures the AI assistant with all available modules.
"""
from typing import Dict, Type

from ..services.ai.assistant import assistant
from ..services.ai.module_interface import AIModule
from ..modules.hrm.ai_integration import HRMAIModule
from ..modules.finance.ai_integration import FinanceAIModule
from ..modules.inventory.ai_integration import InventoryAIModule

# Dictionary of available AI modules
AVAILABLE_MODULES: Dict[str, Type[AIModule]] = {
    'hrm': HRMAIModule,
    'finance': FinanceAIModule,
    'inventory': InventoryAIModule,
}

def initialize_ai_assistant() -> None:
    """
    Initialize the AI assistant with all available modules.
    This function should be called during application startup.
    """
    # Clear any existing modules
    assistant.modules.clear()
    
    # Register each module
    for module_name, module_class in AVAILABLE_MODULES.items():
        try:
            module_instance = module_class()
            assistant.register_module(module_name, module_instance)
            print("[OK] Registered AI module: {}".format(module_name))
        except Exception as e:
            print("[ERROR] Failed to register AI module {}: {}".format(module_name, str(e)))
    
    print("\nAI Assistant initialized with {} modules".format(len(assistant.modules)))
    print("Available modules: {}".format(", ".join(assistant.modules.keys())))

# Initialize the AI assistant when this module is imported
initialize_ai_assistant()
