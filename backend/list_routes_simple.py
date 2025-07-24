"""
Simple script to list all registered routes in the FastAPI application.
"""
import uvicorn
from fastapi import FastAPI

# Create a simple FastAPI app to list routes
app = FastAPI()

@app.get("/")
async def list_routes():
    """List all registered routes in the application."""
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, 'methods') else []
        })
    return {"routes": routes}

if __name__ == "__main__":
    uvicorn.run("list_routes_simple:app", host="0.0.0.0", port=8000, reload=True)
