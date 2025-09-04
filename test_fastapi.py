import os
import sys
from fastapi import FastAPI

# Add the backend directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.main import app
    
    print("\nRegistered routes:")
    print("=" * 80)
    
    # Collect all routes
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            methods = ', '.join(route.methods) if hasattr(route, "methods") else "N/A"
            routes.append((route.path, methods))
    
    # Sort and print routes
    for path, methods in sorted(routes, key=lambda x: x[0]):
        print(f"{path} - {methods}")
    
    # Check for payroll analytics routes
    print("\nPayroll Analytics Routes:")
    print("=" * 80)
    payroll_routes = [r for r in routes if "/api/payroll/analytics/" in r[0]]
    if payroll_routes:
        for path, methods in sorted(payroll_routes, key=lambda x: x[0]):
            print(f"{path} - {methods}")
    else:
        print("No payroll analytics routes found!")
    
except ImportError as e:
    print(f"Error importing app: {e}")
    print("Make sure you're running this from the project root directory.")
    print(f"Current working directory: {os.getcwd()}")
    print("Python path:", sys.path)
