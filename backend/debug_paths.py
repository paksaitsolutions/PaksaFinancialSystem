"""
Debug script to check Python path and import resolution.
"""
import sys
import os
from pathlib import Path

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Print Python path
print("\nPython path:")
for p in sys.path:
    print(f"- {p}")

# Check if app package is importable
print("\nAttempting to import app package...")
try:
    import app
    print(f"✅ Successfully imported 'app' from: {app.__file__}")
    
    # Try importing core modules
    try:
        from app.core import db
        print(f"✅ Successfully imported 'app.core.db' from: {db.__file__}")
    except ImportError as e:
        print(f"❌ Error importing 'app.core.db': {e}")
        
except ImportError as e:
    print(f"❌ Error importing 'app': {e}")

# Print directory structure
print("\nDirectory structure:")
for root, dirs, files in os.walk("."):
    level = root.count(os.sep)
    indent = ' ' * 4 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 4 * (level + 1)
    for f in files:
        if f.endswith('.py') or f == '__init__.py':
            print(f"{subindent}{f}")
