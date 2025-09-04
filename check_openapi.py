"""
Script to check the OpenAPI schema of the FastAPI application
"""
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Add the backend directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.main import app
    
    # Get the OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Print all paths
    print("\nAvailable API Paths:")
    print("=" * 80)
    for path in sorted(openapi_schema.get('paths', {}).keys()):
        print(path)
    
    # Check for payroll analytics paths
    print("\nPayroll Analytics Paths:")
    print("=" * 80)
    payroll_paths = [p for p in openapi_schema.get('paths', {}).keys() if '/payroll/analytics/' in p]
    if payroll_paths:
        for path in sorted(payroll_paths):
            print(path)
    else:
        print("No payroll analytics paths found in OpenAPI schema!")
        
        # Print all paths to help with debugging
        print("\nAll available paths:")
        print("=" * 80)
        for path in sorted(openapi_schema.get('paths', {}).keys()):
            print(path)
    
except ImportError as e:
    print(f"Error importing app: {e}")
    print("Make sure you're running this from the project root directory.")
    print(f"Current working directory: {os.getcwd()}")
    print("Python path:", sys.path)
