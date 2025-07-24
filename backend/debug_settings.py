"""
Minimal script to debug settings initialization.
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Print Python path for debugging
print("Python path:")
for p in sys.path:
    print(f"  {p}")

# Try to import settings with basic error handling
try:
    print("\nAttempting to import settings...")
    from app.core.config import settings
    print("✅ Successfully imported settings")
except Exception as e:
    print(f"❌ Error importing settings: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# If we got here, settings was imported successfully
print("\nSettings attributes:")
for attr in dir(settings):
    if not attr.startswith('_'):
        try:
            value = getattr(settings, attr)
            print(f"{attr}: {value}")
        except Exception as e:
            print(f"{attr}: <error: {e}>")
