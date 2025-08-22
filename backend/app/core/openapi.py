"""
OpenAPI documentation configuration.

This module provides utilities for configuring the OpenAPI documentation
for the FastAPI application.
"""
from typing import Dict, Any, List

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings

def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Create a custom OpenAPI schema for the application.
    
    Args:
        app: The FastAPI application
        
    Returns:
        The OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        description=settings.PROJECT_DESCRIPTION,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"] = {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT token",
            },
            "apiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key authentication",
            },
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [
        {"bearerAuth": []},
    ]
    
    # Add API versioning information
    openapi_schema["info"]["x-api-versioning"] = {
        "current": settings.API_VERSION,
        "available": ["v1"],
        "deprecated": [],
    }
    
    # Add custom tags metadata
    openapi_schema["tags"] = [
        {
            "name": "auth",
            "description": "Authentication and authorization operations",
        },
        {
            "name": "users",
            "description": "User management operations",
        },
        {
            "name": "general-ledger",
            "description": "General Ledger operations",
        },
        {
            "name": "accounts-payable",
            "description": "Accounts Payable operations",
        },
        {
            "name": "accounts-receivable",
            "description": "Accounts Receivable operations",
        },
        {
            "name": "payroll",
            "description": "Payroll operations",
        },
        {
            "name": "tax",
            "description": "Tax operations",
        },
    ]
    
    # Add custom servers
    openapi_schema["servers"] = [
        {
            "url": "/",
            "description": "Current server",
        },
        {
            "url": "https://api.paksa.finance",
            "description": "Production server",
        },
        {
            "url": "https://staging-api.paksa.finance",
            "description": "Staging server",
        },
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def setup_openapi(app: FastAPI) -> None:
    """Set up custom OpenAPI documentation for the application.
    
    Args:
        app: The FastAPI application
    """
    app.openapi = lambda: custom_openapi(app)