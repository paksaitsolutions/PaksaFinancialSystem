import sys
import os
from pathlib import Path

print("=== Python Path ===")
for p in sys.path:
    print(f"- {p}")

print("\n=== Current Working Directory ===")
print(f"- {os.getcwd()}")

print("\n=== Testing Imports ===")
try:
    import app
    print("✅ Successfully imported 'app'")
    print(f"app.__file__: {app.__file__}")
    
    # Try importing database module
    try:
        from app.modules.core import database
        print("✅ Successfully imported 'app.modules.core.database'")
        print(f"database.__file__: {database.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import 'app.modules.core.database': {e}")
        
        # Try alternative import path
        try:
            from app.core import database as core_db
            print("✅ Successfully imported 'app.core.database'")
            print(f"core_db.__file__: {core_db.__file__}")
        except ImportError as e2:
            print(f"❌ Also failed to import 'app.core.database': {e2}")
    
except ImportError as e:
    print(f"❌ Failed to import 'app': {e}")

print("\n=== Directory Structure ===")
for root, dirs, files in os.walk(Path(__file__).parent / "app"):
    level = root.replace(str(Path(__file__).parent), '').count(os.sep)
    indent = ' ' * 4 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 4 * (level + 1)
    for f in files:
        if f.endswith('.py'):
            print(f"{subindent}{f}")
