"""
Fixed Assets Module

This module provides comprehensive fixed asset management capabilities including:
- Asset lifecycle tracking (acquisition, depreciation, maintenance, disposal)
- Depreciation calculation and scheduling
- Maintenance management
- Asset categories and classifications
- Reporting and analytics
"""
from . import models, schemas, services, exceptions
from .api import router as fixed_assets_router

# Export the router to be included in the main FastAPI application
__all__ = [
    'models',
    'schemas',
    'services', 
    'exceptions',
    'fixed_assets_router',
]
