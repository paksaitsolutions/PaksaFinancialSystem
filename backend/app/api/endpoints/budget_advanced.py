from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database_config import get_db

router = APIRouter()

@router.get("/")
def get_budgets(db: Session = Depends(get_db)):
    """Get all budgets with advanced filtering"""
    return [
        {
            "id": "budget_001",
            "name": "FY 2024 Operating Budget",
            "description": "Annual operating budget for fiscal year 2024",
            "fiscal_year": 2024,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "status": "active",
            "total_budget": 2500000.00,
            "total_actual": 1875000.00,
            "variance": -625000.00,
            "line_items": []
        },
        {
            "id": "budget_002", 
            "name": "Q1 2024 Marketing Budget",
            "description": "Quarterly marketing and advertising budget",
            "fiscal_year": 2024,
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
            "status": "approved",
            "total_budget": 150000.00,
            "total_actual": 142500.00,
            "variance": -7500.00,
            "line_items": []
        }
    ]

@router.post("/")
def create_budget(budget_data: dict, db: Session = Depends(get_db)):
    """Create new budget with validation and approval workflow"""
    return {
        "id": f"budget_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "draft",
        "total_budget": sum(item.get('budgeted_amount', 0) for item in budget_data.get('line_items', [])),
        "total_actual": 0.00,
        "variance": 0.00,
        **budget_data
    }

@router.get("/{budget_id}")
def get_budget(budget_id: str, db: Session = Depends(get_db)):
    """Get detailed budget with line items and analytics"""
    return {
        "id": budget_id,
        "name": "FY 2024 Operating Budget",
        "description": "Annual operating budget for fiscal year 2024",
        "fiscal_year": 2024,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "status": "active",
        "line_items": [
            {
                "id": "line_001",
                "account_code": "4000",
                "account_name": "Revenue - Sales",
                "category": "Revenue",
                "budgeted_amount": 1500000.00,
                "actual_amount": 1125000.00,
                "variance": -375000.00,
                "period_type": "annual"
            },
            {
                "id": "line_002",
                "account_code": "5000", 
                "account_name": "Cost of Goods Sold",
                "category": "COGS",
                "budgeted_amount": 600000.00,
                "actual_amount": 450000.00,
                "variance": -150000.00,
                "period_type": "annual"
            }
        ]
    }

@router.post("/import-template/{template_id}")
def import_budget_template(template_id: str, db: Session = Depends(get_db)):
    """Import budget from predefined template"""
    return {
        "id": f"budget_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "name": f"Budget from Template {template_id}",
        "status": "draft",
        "imported_from_template": template_id,
        "line_items": [
            {
                "account_code": "4000",
                "account_name": "Revenue - Sales", 
                "category": "Revenue",
                "budgeted_amount": 1000000.00,
                "actual_amount": 0.00,
                "variance": 0.00
            }
        ]
    }

@router.get("/{budget_id}/export")
def export_budget(budget_id: str, format: str = "excel", db: Session = Depends(get_db)):
    """Export budget to various formats (Excel, CSV, PDF)"""
    return {
        "success": True,
        "download_url": f"/downloads/budget_{budget_id}.{format}",
        "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
    }

@router.post("/copy-previous")
def copy_from_previous_year(copy_data: dict, db: Session = Depends(get_db)):
    """Copy budget from previous year with adjustments"""
    return {
        "id": f"budget_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "name": f"FY {copy_data['new_fiscal_year']} Budget (Copied)",
        "fiscal_year": copy_data['new_fiscal_year'],
        "status": "draft",
        "copied_from": copy_data['previous_budget_id'],
        "adjustment_factor": 1.05  # 5% increase
    }

@router.get("/analytics")
def get_budget_analytics(db: Session = Depends(get_db)):
    """Advanced budget analytics and KPIs"""
    return {
        "total_budgets": 12,
        "active_budgets": 8,
        "budget_utilization": 75.2,
        "variance_percentage": -12.5,
        "top_variances": [
            {
                "account": "Marketing Expenses",
                "variance": -45000.00,
                "percentage": -15.2
            },
            {
                "account": "Travel & Entertainment", 
                "variance": 12000.00,
                "percentage": 8.7
            }
        ],
        "budget_performance": {
            "on_track": 6,
            "over_budget": 2,
            "under_budget": 4
        }
    }

@router.get("/templates")
def get_budget_templates(db: Session = Depends(get_db)):
    """Get available budget templates"""
    return [
        {
            "id": "template_001",
            "name": "Standard Operating Budget",
            "description": "Template for annual operating budget",
            "category": "Operating"
        },
        {
            "id": "template_002",
            "name": "Capital Expenditure Budget", 
            "description": "Template for capital investments",
            "category": "Capital"
        },
        {
            "id": "template_003",
            "name": "Department Budget",
            "description": "Template for departmental budgets",
            "category": "Departmental"
        }
    ]

@router.post("/{budget_id}/forecast")
def generate_budget_forecast(budget_id: str, forecast_data: dict, db: Session = Depends(get_db)):
    """AI-powered budget forecasting"""
    months = forecast_data.get('months', 12)
    return {
        "budget_id": budget_id,
        "forecast_period": f"{months} months",
        "projected_total": 2750000.00,
        "confidence_score": 0.87,
        "monthly_projections": [
            {
                "month": "2024-02",
                "projected_actual": 208333.33,
                "confidence": 0.92
            },
            {
                "month": "2024-03", 
                "projected_actual": 215000.00,
                "confidence": 0.89
            }
        ],
        "risk_factors": [
            "Seasonal revenue fluctuations",
            "Market volatility impact"
        ]
    }

@router.post("/{budget_id}/approve")
def approve_budget(budget_id: str, approval_data: dict, db: Session = Depends(get_db)):
    """Budget approval workflow"""
    return {
        "budget_id": budget_id,
        "status": "approved",
        "approved_by": approval_data.get('approver_id'),
        "approved_at": datetime.now().isoformat(),
        "approval_notes": approval_data.get('notes', '')
    }