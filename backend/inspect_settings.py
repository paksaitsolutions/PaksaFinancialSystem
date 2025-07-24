"""
Minimal script to inspect the settings module directly.
"""
import os
import sys
import importlib.util

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def load_module(module_path):
    """Dynamically load a module from a file path."""
    module_name = os.path.basename(module_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def main():
    print("🔍 Inspecting settings module...")
    
    # Path to the config file
    config_path = os.path.join(project_root, 'app', 'core', 'config.py')
    
    if not os.path.exists(config_path):
        print(f"❌ Config file not found at: {config_path}")
        return
    
    print(f"📂 Config file found at: {config_path}")
    
    try:
        # Try to load the module
        print("\n🔄 Loading settings module...")
        config = load_module(config_path)
        
        # Check if settings exists
        if not hasattr(config, 'settings'):
            print("❌ No 'settings' object found in config module")
            return
        
        settings = config.settings
        print(f"✅ Settings object type: {type(settings)}")
        
        # Print all attributes
        print("\n📋 All attributes:")
        for attr in dir(settings):
            if not attr.startswith('_'):
                try:
                    value = getattr(settings, attr)
                    print(f"  {attr}: {value}")
                except Exception as e:
                    print(f"  {attr}: <error: {e}>")
        
    except Exception as e:
        print(f"\n❌ Error loading settings:")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
