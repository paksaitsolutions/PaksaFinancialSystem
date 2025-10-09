from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid

from ....database import get_db
from ....models.inventory import FixedAsset
from ....models.user import User
from ....core.auth import get_current_user
from ....schemas.reports import (
    ReportResponse, ReportRunRequest, FinancialStatementResponse,
    TrialBalanceResponse, CashFlowResponse, IncomeStatementResponse,
    BalanceSheetResponse, AgingReportResponse
)

router = APIRouter()

@router.get("/financial-statements/balance-sheet")
async def get_balance_sheet(
    as_of_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not as_of_date:
        as_of_date = date.today()
    
    # Mock balance sheet data - replace with actual GL queries
    return BalanceSheetResponse(
        as_of_date=as_of_date,
        assets={
            "current_assets": {
                "cash": 125000,
                "accounts_receivable": 85000,
                "inventory": 65000,
                "total": 275000
            },
            "fixed_assets": {
                "equipment": 150000,
                "accumulated_depreciation": -45000,
                "total": 105000
            },
            "total_assets": 380000
        },
        liabilities={
            "current_liabilities": {
                "accounts_payable": 45000,
                "accrued_expenses": 15000,
                "total": 60000
            },
            "long_term_liabilities": {
                "loans_payable": 80000,
                "total": 80000
            },
            "total_liabilities": 140000
        },
        equity={
            "retained_earnings": 190000,
            "current_earnings": 50000,
            "total_equity": 240000
        }
    )

@router.get("/financial-statements/income-statement")
async def get_income_statement(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date(end_date.year, end_date.month, 1)
    
    return IncomeStatementResponse(
        period_start=start_date,
        period_end=end_date,
        revenue={
            "sales_revenue": 1250000,
            "service_revenue": 350000,
            "total_revenue": 1600000
        },
        cost_of_goods_sold={
            "materials": 400000,
            "labor": 300000,
            "total_cogs": 700000
        },
        gross_profit=900000,
        operating_expenses={
            "salaries": 250000,
            "rent": 60000,
            "utilities": 25000,
            "marketing": 45000,
            "total_operating_expenses": 380000
        },
        operating_income=520000,
        other_income=5000,
        other_expenses=15000,
        net_income=510000
    )

@router.get("/financial-statements/cash-flow")
async def get_cash_flow_statement(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date(end_date.year, end_date.month, 1)
    
    return CashFlowResponse(
        period_start=start_date,
        period_end=end_date,
        operating_activities={
            "net_income": 510000,
            "depreciation": 45000,
            "accounts_receivable_change": -25000,
            "inventory_change": -15000,
            "accounts_payable_change": 20000,
            "net_operating_cash": 535000
        },
        investing_activities={
            "equipment_purchases": -75000,
            "investment_sales": 30000,
            "net_investing_cash": -45000
        },
        financing_activities={
            "loan_proceeds": 100000,
            "loan_repayments": -50000,
            "dividends_paid": -80000,
            "net_financing_cash": -30000
        },
        net_cash_change=460000,
        beginning_cash=125000,
        ending_cash=585000
    )

@router.get("/general-ledger/trial-balance")
async def get_trial_balance(
    as_of_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not as_of_date:
        as_of_date = date.today()
    
    # Mock trial balance data
    accounts = [
        {"account_code": "1000", "account_name": "Cash", "debit": 125000, "credit": 0},
        {"account_code": "1200", "account_name": "Accounts Receivable", "debit": 85000, "credit": 0},
        {"account_code": "1300", "account_name": "Inventory", "debit": 65000, "credit": 0},
        {"account_code": "1500", "account_name": "Equipment", "debit": 150000, "credit": 0},
        {"account_code": "1510", "account_name": "Accumulated Depreciation", "debit": 0, "credit": 45000},
        {"account_code": "2000", "account_name": "Accounts Payable", "debit": 0, "credit": 45000},
        {"account_code": "2100", "account_name": "Accrued Expenses", "debit": 0, "credit": 15000},
        {"account_code": "2500", "account_name": "Loans Payable", "debit": 0, "credit": 80000},
        {"account_code": "3000", "account_name": "Retained Earnings", "debit": 0, "credit": 190000},
        {"account_code": "4000", "account_name": "Sales Revenue", "debit": 0, "credit": 1250000},
        {"account_code": "5000", "account_name": "Cost of Goods Sold", "debit": 700000, "credit": 0},
        {"account_code": "6000", "account_name": "Operating Expenses", "debit": 380000, "credit": 0}
    ]
    
    total_debits = sum(acc["debit"] for acc in accounts)
    total_credits = sum(acc["credit"] for acc in accounts)
    
    return TrialBalanceResponse(
        as_of_date=as_of_date,
        accounts=accounts,
        total_debits=total_debits,
        total_credits=total_credits,
        is_balanced=total_debits == total_credits
    )

@router.get("/aging/accounts-receivable")
async def get_ar_aging(
    as_of_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not as_of_date:
        as_of_date = date.today()
    
    # Mock AR aging data
    aging_buckets = [
        {"customer": "ABC Corp", "current": 15000, "days_30": 5000, "days_60": 0, "days_90": 0, "over_90": 0, "total": 20000},
        {"customer": "XYZ Ltd", "current": 8000, "days_30": 3000, "days_60": 2000, "days_90": 0, "over_90": 0, "total": 13000},
        {"customer": "DEF Inc", "current": 0, "days_30": 0, "days_60": 5000, "days_90": 2000, "over_90": 1000, "total": 8000}
    ]
    
    totals = {
        "current": sum(b["current"] for b in aging_buckets),
        "days_30": sum(b["days_30"] for b in aging_buckets),
        "days_60": sum(b["days_60"] for b in aging_buckets),
        "days_90": sum(b["days_90"] for b in aging_buckets),
        "over_90": sum(b["over_90"] for b in aging_buckets),
        "total": sum(b["total"] for b in aging_buckets)
    }
    
    return AgingReportResponse(
        report_type="accounts_receivable",
        as_of_date=as_of_date,
        aging_buckets=aging_buckets,
        totals=totals
    )

@router.get("/aging/accounts-payable")
async def get_ap_aging(
    as_of_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not as_of_date:
        as_of_date = date.today()
    
    # Mock AP aging data
    aging_buckets = [
        {"vendor": "Supplier A", "current": 12000, "days_30": 3000, "days_60": 0, "days_90": 0, "over_90": 0, "total": 15000},
        {"vendor": "Supplier B", "current": 8000, "days_30": 2000, "days_60": 1000, "days_90": 0, "over_90": 0, "total": 11000},
        {"vendor": "Supplier C", "current": 0, "days_30": 0, "days_60": 3000, "days_90": 1500, "over_90": 500, "total": 5000}
    ]
    
    totals = {
        "current": sum(b["current"] for b in aging_buckets),
        "days_30": sum(b["days_30"] for b in aging_buckets),
        "days_60": sum(b["days_60"] for b in aging_buckets),
        "days_90": sum(b["days_90"] for b in aging_buckets),
        "over_90": sum(b["over_90"] for b in aging_buckets),
        "total": sum(b["total"] for b in aging_buckets)
    }
    
    return AgingReportResponse(
        report_type="accounts_payable",
        as_of_date=as_of_date,
        aging_buckets=aging_buckets,
        totals=totals
    )

@router.get("/available-reports")
async def get_available_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available reports organized by module"""
    return {
        "financial_statements": [
            {"id": "balance-sheet", "name": "Balance Sheet", "description": "Statement of financial position"},
            {"id": "income-statement", "name": "Income Statement", "description": "Profit and loss statement"},
            {"id": "cash-flow", "name": "Cash Flow Statement", "description": "Cash inflows and outflows"}
        ],
        "general_ledger": [
            {"id": "trial-balance", "name": "Trial Balance", "description": "Account balances verification"},
            {"id": "general-ledger", "name": "General Ledger", "description": "Detailed account transactions"}
        ],
        "accounts_receivable": [
            {"id": "ar-aging", "name": "AR Aging Report", "description": "Outstanding receivables by age"},
            {"id": "customer-statements", "name": "Customer Statements", "description": "Customer account statements"}
        ],
        "accounts_payable": [
            {"id": "ap-aging", "name": "AP Aging Report", "description": "Outstanding payables by age"},
            {"id": "vendor-statements", "name": "Vendor Statements", "description": "Vendor account statements"}
        ],
        "inventory": [
            {"id": "inventory-valuation", "name": "Inventory Valuation", "description": "Current inventory values"},
            {"id": "inventory-movement", "name": "Inventory Movement", "description": "Stock movement report"}
        ],
        "fixed_assets": [
            {"id": "asset-register", "name": "Asset Register", "description": "Complete asset listing"},
            {"id": "depreciation-schedule", "name": "Depreciation Schedule", "description": "Asset depreciation details"}
        ],
        "tax": [
            {"id": "tax-summary", "name": "Tax Summary", "description": "Tax liability summary"},
            {"id": "tax-returns", "name": "Tax Returns", "description": "Tax return preparation"}
        ]
    }

@router.post("/run-report")
async def run_report(
    request: ReportRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run a specific report"""
    # Simulate report generation
    return {
        "report_id": request.report_id,
        "status": "completed",
        "generated_at": datetime.now(),
        "download_url": f"/api/v1/reports/download/{request.report_id}"
    }