"""
Test script to verify imports in main.py
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

print("Testing imports...")

try:
    # Test core imports
    from app.core.config import settings
    print("✓ Successfully imported settings from app.core.config")
    
    from app.core.logging import setup_logging
    print("✓ Successfully imported setup_logging from app.core.logging")
    
    from app.core.middleware.error_handler import setup_middleware
    print("✓ Successfully imported setup_middleware from app.core.middleware.error_handler")
    
    # Test API router import
    from app.api.v1.api import api_router
    print("✓ Successfully imported api_router from app.api.v1.api")
    
    print("\nAll imports successful!")
    
except Exception as e:
    print(f"\nError during imports: {str(e)}")
    print("\nPython path:")
    for p in sys.path:
        print(f"  - {p}")
