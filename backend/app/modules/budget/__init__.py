"""
Budget Module

This module handles all budget-related functionality including:
- Budget creation and management
- Budget tracking and reporting
- Budget vs. actual analysis
- Budget approvals and workflows
"""
from fastapi import APIRouter
from . import api

router = APIRouter(prefix="/budget", tags=["budget"])
router.include_router(api.router)

__all__ = ["router"]
