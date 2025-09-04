"""
Test script to list all registered FastAPI routes
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi import FastAPI
from app.main import app

def list_routes():
    """List all registered routes in the FastAPI application"""
    print("\nRegistered routes:")
    print("-" * 80)
    for route in app.routes:
        if hasattr(route, "path"):
            methods = getattr(route, "methods", [])
            print(f"{route.path} - {', '.join(methods) if methods else 'N/A'}")

if __name__ == "__main__":
    print("Listing all registered routes...")
    list_routes()
