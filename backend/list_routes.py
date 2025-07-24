"""
Script to list all available routes in the FastAPI application.
"""
import sys
from fastapi import FastAPI
from fastapi.routing import APIRoute

# Add the backend directory to the Python path
import os
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import the FastAPI app
from app.main import app

def list_routes():
    """List all available routes in the FastAPI application."""
    routes = []
    
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods),
                "endpoint": route.endpoint.__name__ if hasattr(route.endpoint, '__name__') else str(route.endpoint)
            })
    
    # Print the routes in a nice format
    print("\n" + "="*80)
    print("AVAILABLE ROUTES:")
    print("="*80)
    for i, route in enumerate(routes, 1):
        print(f"{i}. {route['path']} - {', '.join(route['methods'])}")
        print(f"   Endpoint: {route['endpoint']}")
        print("-"*80)
    
    print(f"\nTotal routes: {len(routes)}")

if __name__ == "__main__":
    list_routes()
