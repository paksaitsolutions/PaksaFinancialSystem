"""
Paksa Financial System - Main API Router
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Main API router that includes all sub-routers for the application.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging

from core.database import get_db
from core.security import get_current_active_user
from core.config import settings

# Create main API router with versioning
api_router = APIRouter(
    prefix=settings.API_PREFIX,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    }
)

# Import and include all API routes here
from .endpoints import (
    accounts_payable,
    chart_of_accounts,
    journal_entries,
    trial_balance,
    financial_statements,
    accounts_receivable,
    fixed_assets,
    budget,
    cash_management
)

# Import compliance module
from app.modules.compliance.api import paksa_compliance_router

# Include API routes with proper organization

# ===== Core Financials =====
api_router.include_router(
    chart_of_accounts.router, 
    prefix="/chart-of-accounts", 
    tags=["01. Core - Chart of Accounts"]
)

api_router.include_router(
    journal_entries.router,
    prefix="/journal-entries",
    tags=["01. Core - Journal Entries"]
)

api_router.include_router(
    trial_balance.router,
    prefix="/trial-balance",
    tags=["01. Core - Trial Balance"]
)

api_router.include_router(
    financial_statements.router,
    prefix="/financial-statements",
    tags=["01. Core - Financial Statements"]
)

# ===== Accounts Modules =====
api_router.include_router(
    accounts_payable.router,
    prefix="/accounts-payable",
    tags=["02. Accounts - Payable"]
)

api_router.include_router(
    accounts_receivable.router,
    prefix="/accounts-receivable",
    tags=["02. Accounts - Receivable"]
)

# ===== Asset Management =====
api_router.include_router(
    fixed_assets.router,
    prefix="/fixed-assets",
    tags=["03. Assets - Fixed Assets"]
)

api_router.include_router(
    cash_management.router,
    prefix="/cash-management",
    tags=["03. Assets - Cash Management"]
)

# ===== Budgeting =====
api_router.include_router(
    budget.router,
    prefix="/budget",
    tags=["04. Budgeting"]
)

# ===== Compliance & Security =====
api_router.include_router(
    paksa_compliance_router,
    prefix="/compliance",
    tags=["99. Compliance & Security"]
)

@api_router.get("/", include_in_schema=False)
async def api_root() -> Dict[str, Any]:
    """Root API endpoint."""
    return {
        "application": "Paksa Financial System",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs",
        "api_version": "v1",
        "status": "operational"
    }

@api_router.get("/health", include_in_schema=False)
async def health_check() -> Dict[str, str]:
    """Health check endpoint for load balancers and monitoring."""
    # Add more sophisticated health checks here (database, cache, etc.)
    return {"status": "healthy"}
