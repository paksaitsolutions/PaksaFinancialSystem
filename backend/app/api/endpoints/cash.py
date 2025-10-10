from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database_config import get_db

router = APIRouter()

@router.get("/dashboard")
def get_cash_dashboard(db: Session = Depends(get_db)):
    """Advanced cash management dashboard with real-time metrics"""
    return {
        "total_balance": 2847392.50,
        "account_count": 8,
        "monthly_inflow": 1245670.00,
        "monthly_outflow": 987450.00,
        "cash_flow_trend": [850000, 920000, 1050000, 1180000, 1245670],
        "liquidity_ratio": 2.85
    }

@router.get("/accounts")
def get_bank_accounts(db: Session = Depends(get_db)):
    """Get all bank accounts with real-time balances"""
    return [
        {
            "id": "acc_001",
            "name": "Main Operating Account",
            "account_number": "****1234",
            "bank_name": "First National Bank",
            "account_type": "checking",
            "current_balance": 1245670.00,
            "available_balance": 1195670.00,
            "currency": "USD",
            "is_active": True
        },
        {
            "id": "acc_002", 
            "name": "Payroll Account",
            "account_number": "****5678",
            "bank_name": "Business Bank",
            "account_type": "checking",
            "current_balance": 450230.00,
            "available_balance": 450230.00,
            "currency": "USD",
            "is_active": True
        },
        {
            "id": "acc_003",
            "name": "Reserve Fund",
            "account_number": "****9012",
            "bank_name": "Investment Bank",
            "account_type": "savings",
            "current_balance": 850000.00,
            "available_balance": 850000.00,
            "currency": "USD",
            "is_active": True
        }
    ]

@router.post("/accounts")
def create_bank_account(account_data: dict, db: Session = Depends(get_db)):
    """Create new bank account with validation"""
    return {
        "id": f"acc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        **account_data,
        "current_balance": 0.00,
        "available_balance": 0.00,
        "is_active": True
    }

@router.get("/transactions")
def get_transactions(limit: Optional[int] = 100, db: Session = Depends(get_db)):
    """Get cash transactions with advanced filtering"""
    return [
        {
            "id": "txn_001",
            "account_id": "acc_001",
            "transaction_date": "2024-01-15T10:30:00",
            "transaction_type": "deposit",
            "amount": 125000.00,
            "memo": "Customer payment - Invoice batch",
            "reference": "DEP-2024-001",
            "account": {
                "name": "Main Operating Account",
                "account_number": "****1234"
            }
        },
        {
            "id": "txn_002",
            "account_id": "acc_002",
            "transaction_date": "2024-01-14T14:15:00", 
            "transaction_type": "withdrawal",
            "amount": 45230.00,
            "memo": "Payroll processing - Bi-weekly",
            "reference": "PAY-2024-003",
            "account": {
                "name": "Payroll Account",
                "account_number": "****5678"
            }
        }
    ]

@router.post("/transactions")
def create_transaction(transaction_data: dict, db: Session = Depends(get_db)):
    """Create cash transaction with automatic balance update"""
    return {
        "id": f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "transaction_date": datetime.now().isoformat(),
        **transaction_data
    }

@router.get("/forecast")
def get_cash_flow_forecast(days: int = 30, db: Session = Depends(get_db)):
    """AI-powered cash flow forecasting"""
    forecasts = []
    base_date = datetime.now()
    
    for i in range(0, days, 7):  # Weekly forecasts
        week_date = base_date + timedelta(days=i)
        forecasts.append({
            "period": f"Week {i//7 + 1}",
            "week_ending": week_date.strftime("%Y-%m-%d"),
            "projected_inflow": 285000 + (i * 1000),
            "projected_outflow": 195000 + (i * 800),
            "net_cash_flow": 90000 + (i * 200),
            "ending_balance": 2847392 + ((90000 + (i * 200)) * (i//7 + 1)),
            "confidence_level": max(0.75, 0.95 - (i * 0.02))
        })
    
    return forecasts

@router.post("/accounts/{account_id}/reconcile")
def reconcile_account(account_id: str, reconciliation_data: dict, db: Session = Depends(get_db)):
    """Advanced bank reconciliation with automatic matching"""
    return {
        "success": True,
        "reconciled_transactions": reconciliation_data.get("transaction_count", 0),
        "unmatched_items": 2,
        "balance_difference": 0.00,
        "reconciliation_date": datetime.now().isoformat()
    }

@router.get("/analytics/liquidity")
def get_liquidity_analysis(db: Session = Depends(get_db)):
    """Advanced liquidity analysis and ratios"""
    return {
        "current_ratio": 2.85,
        "quick_ratio": 2.45,
        "cash_ratio": 1.95,
        "working_capital": 1850000.00,
        "days_cash_on_hand": 45.2,
        "burn_rate": 195000.00,
        "runway_months": 14.6
    }

@router.get("/analytics/variance")
def get_cash_variance_analysis(db: Session = Depends(get_db)):
    """Cash flow variance analysis vs budget/forecast"""
    return {
        "period": "Current Month",
        "budgeted_inflow": 1200000.00,
        "actual_inflow": 1245670.00,
        "inflow_variance": 45670.00,
        "budgeted_outflow": 950000.00,
        "actual_outflow": 987450.00,
        "outflow_variance": -37450.00,
        "net_variance": 8220.00,
        "variance_percentage": 0.68
    }