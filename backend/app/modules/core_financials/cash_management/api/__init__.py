"""
Paksa Financial System - Cash Management API Module
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

This module contains the API endpoints for the Cash Management functionality.
"""

from fastapi import APIRouter
from . import bank_accounts, transactions, reconciliations

router = APIRouter()

# Include all endpoint routers
router.include_router(bank_accounts.router, prefix="/accounts", tags=["Bank Accounts"])
router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
router.include_router(reconciliations.router, prefix="/reconciliations", tags=["Reconciliations"])
