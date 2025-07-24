"""
Script to inspect and list all routes in the main FastAPI application.
"""
import sys
import os
from fastapi import FastAPI
from fastapi.routing import APIRoute

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

try:
    # Try to import the main FastAPI app
    from app.main import app
    
    print("Successfully imported the FastAPI app!")
    print(f"App title: {app.title}")
    print(f"App version: {app.version}")
    print("\nRegistered routes:")
    
    # List all routes
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"- {route.path} - {', '.join(route.methods)}")
        else:
            print(f"- {route.path} - {route.methods if hasattr(route, 'methods') else 'Unknown'}")
    
    print("\nTotal routes:", len(app.routes))
    
except ImportError as e:
    print(f"Error importing the FastAPI app: {e}")
    print("\nPython path:")
    for path in sys.path:
        print(f"- {path}")
    
    print("\nCurrent directory files:")
    for item in os.listdir('.'):
        print(f"- {item}")
    
    print("\nApp directory files:")
    app_dir = os.path.join(backend_dir, 'app')
    if os.path.exists(app_dir):
        for item in os.listdir(app_dir):
            print(f"- {item}")
    else:
        print(f"App directory not found at: {app_dir}")
