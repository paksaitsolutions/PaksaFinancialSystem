from fastapi import APIRouter, Query
from typing import List, Optional

router = APIRouter()

@router.get("/account-types")
async def get_account_types(active_only: bool = Query(True)):
    """Get chart of account types"""
    account_types = [
        {"id": 1, "name": "Assets", "code": "ASSET", "active": True},
        {"id": 2, "name": "Liabilities", "code": "LIABILITY", "active": True},
        {"id": 3, "name": "Equity", "code": "EQUITY", "active": True},
        {"id": 4, "name": "Revenue", "code": "REVENUE", "active": True},
        {"id": 5, "name": "Expenses", "code": "EXPENSE", "active": True},
        {"id": 6, "name": "Cost of Goods Sold", "code": "COGS", "active": True}
    ]
    
    if active_only:
        account_types = [at for at in account_types if at["active"]]
    
    return account_types

@router.get("/currencies")
async def get_currencies():
    """Get available currencies"""
    return [
        {"code": "USD", "name": "US Dollar", "symbol": "$"},
        {"code": "EUR", "name": "Euro", "symbol": "€"},
        {"code": "GBP", "name": "British Pound", "symbol": "£"},
        {"code": "PKR", "name": "Pakistani Rupee", "symbol": "₨"}
    ]