"""
AI Assistant Initialization

Sets up and configures the AI assistant with all available modules.
"""
from typing import Dict, Type

from ..services.ai.assistant import assistant
from ..services.ai.module_interface import AIModule

# Import AI modules with error handling
AVAILABLE_MODULES: Dict[str, Type[AIModule]] = {}

try:
    from ..modules.hrm.ai_integration import HRMAIModule
    AVAILABLE_MODULES['hrm'] = HRMAIModule
except ImportError as e:
    print(f"Warning: Could not import HRM AI module: {e}")

try:
    from ..modules.finance.ai_integration import FinanceAIModule
    AVAILABLE_MODULES['finance'] = FinanceAIModule
except ImportError as e:
    print(f"Warning: Could not import Finance AI module: {e}")

try:
    from ..modules.inventory.ai_integration import InventoryAIModule
    AVAILABLE_MODULES['inventory'] = InventoryAIModule
except ImportError as e:
    print(f"Warning: Could not import Inventory AI module: {e}")

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
