"""
Dashboard Analytics API for real-time financial metrics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from typing import List, Dict, Any
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/kpis")
async def get_key_performance_indicators(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Get key performance indicators for dashboard"""
    return {
        "revenue": {
            "current": 1234567.89,
            "previous": 1098765.43,
            "change_percent": 12.4,
            "trend": "up"
        },
        "expenses": {
            "current": 987654.32,
            "previous": 876543.21,
            "change_percent": 12.7,
            "trend": "up"
        },
        "profit_margin": {
            "current": 20.5,
            "previous": 20.2,
            "change_percent": 1.5,
            "trend": "up"
        },
        "cash_flow": {
            "current": 456789.12,
            "previous": 398765.43,
            "change_percent": 14.5,
            "trend": "up"
        }
    }

@router.get("/financial-summary")
async def get_financial_summary(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Get financial summary for dashboard cards"""
    return {
        "total_revenue": 1234567.89,
        "accounts_receivable": 456789.12,
        "accounts_payable": 234567.89,
        "cash_balance": 789123.45,
        "net_income": 246913.57,
        "total_assets": 2500000.00,
        "total_liabilities": 800000.00,
        "equity": 1700000.00
    }

@router.get("/recent-transactions")
async def get_recent_transactions(limit: int = 10, db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Get recent transactions for dashboard"""
    return [
        {
            "id": 1,
            "date": "2024-01-15",
            "description": "Customer Payment - INV-001",
            "amount": 5000.00,
            "type": "receipt",
            "status": "completed",
            "account": "Accounts Receivable"
        },
        {
            "id": 2,
            "date": "2024-01-14",
            "description": "Office Supplies Purchase",
            "amount": -250.00,
            "type": "payment",
            "status": "pending",
            "account": "Office Expenses"
        },
        {
            "id": 3,
            "date": "2024-01-13",
            "description": "Service Revenue",
            "amount": 3500.00,
            "type": "revenue",
            "status": "completed",
            "account": "Service Revenue"
        }
    ]

@router.get("/alerts")
async def get_system_alerts(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Get system alerts and notifications"""
    return [
        {
            "id": 1,
            "type": "warning",
            "title": "Overdue Invoices",
            "message": "5 invoices are overdue totaling $12,500",
            "priority": "high",
            "created_date": "2024-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "type": "info",
            "title": "Budget Variance",
            "message": "Marketing budget is 15% over allocated amount",
            "priority": "medium",
            "created_date": "2024-01-15T09:15:00Z"
        },
        {
            "id": 3,
            "type": "success",
            "title": "Payment Received",
            "message": "Payment of $5,000 received from Customer ABC",
            "priority": "low",
            "created_date": "2024-01-15T08:45:00Z"
        }
    ]

@router.get("/charts/revenue-trend")
async def get_revenue_trend(period: str = "12m", db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Get revenue trend data for charts"""
    return {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "datasets": [
            {
                "label": "Revenue",
                "data": [85000, 92000, 88000, 95000, 102000, 98000, 105000, 110000, 108000, 115000, 120000, 125000],
                "borderColor": "#3b82f6",
                "backgroundColor": "rgba(59, 130, 246, 0.1)"
            }
        ]
    }

@router.get("/charts/expense-breakdown")
async def get_expense_breakdown(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Get expense breakdown for pie chart"""
    return {
        "labels": ["Salaries", "Office Rent", "Utilities", "Marketing", "Travel", "Supplies", "Other"],
        "datasets": [
            {
                "data": [45000, 12000, 3500, 8000, 2500, 1500, 4500],
                "backgroundColor": [
                    "#3b82f6", "#ef4444", "#10b981", "#f59e0b", 
                    "#8b5cf6", "#06b6d4", "#84cc16"
                ]
            }
        ]
    }

@router.get("/aging-reports")
async def get_aging_reports(db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Get accounts receivable and payable aging"""
    return {
        "accounts_receivable": {
            "current": 125000,
            "30_days": 45000,
            "60_days": 15000,
            "90_days": 8000,
            "over_90": 3000
        },
        "accounts_payable": {
            "current": 85000,
            "30_days": 25000,
            "60_days": 8000,
            "90_days": 2000,
            "over_90": 1000
        }
    }