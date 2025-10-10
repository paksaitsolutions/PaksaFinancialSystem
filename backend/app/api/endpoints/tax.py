from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core import deps
from app.models.user import User
import io
import csv

router = APIRouter()

# Mock data
MOCK_JURISDICTIONS = [
    {"id": 1, "name": "Federal", "code": "US", "level": "federal", "is_active": True, "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"},
    {"id": 2, "name": "California", "code": "CA", "level": "state", "parent_id": 1, "is_active": True, "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"},
    {"id": 3, "name": "Los Angeles County", "code": "LAC", "level": "county", "parent_id": 2, "is_active": True, "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"}
]

MOCK_TAX_RATES = [
    {"id": 1, "jurisdiction_id": 1, "jurisdiction_name": "Federal", "tax_type": "income", "rate": 0.22, "effective_date": "2023-01-01", "is_active": True, "description": "Federal Income Tax"},
    {"id": 2, "jurisdiction_id": 2, "jurisdiction_name": "California", "tax_type": "sales", "rate": 0.0725, "effective_date": "2023-01-01", "is_active": True, "description": "CA State Sales Tax"},
    {"id": 3, "jurisdiction_id": 3, "jurisdiction_name": "Los Angeles County", "tax_type": "sales", "rate": 0.01, "effective_date": "2023-01-01", "is_active": True, "description": "LA County Sales Tax"}
]

MOCK_TRANSACTIONS = [
    {"id": 1, "entity_type": "customer", "entity_id": 1, "entity_name": "ABC Corp", "transaction_date": "2024-01-15", "taxable_amount": 1000.00, "tax_amount": 72.50, "total_amount": 1072.50, "tax_rate_id": 2, "tax_rate": 0.0725, "jurisdiction_id": 2, "jurisdiction_name": "California", "reference_number": "INV-001", "created_at": "2024-01-15T10:00:00Z"},
    {"id": 2, "entity_type": "customer", "entity_id": 2, "entity_name": "XYZ Inc", "transaction_date": "2024-01-14", "taxable_amount": 500.00, "tax_amount": 36.25, "total_amount": 536.25, "tax_rate_id": 2, "tax_rate": 0.0725, "jurisdiction_id": 2, "jurisdiction_name": "California", "reference_number": "INV-002", "created_at": "2024-01-14T14:30:00Z"}
]

MOCK_EXEMPTIONS = [
    {"id": 1, "entity_type": "customer", "entity_id": 3, "entity_name": "Nonprofit Org", "exemption_type": "nonprofit", "certificate_number": "NP-12345", "jurisdiction_id": 2, "jurisdiction_name": "California", "effective_date": "2023-01-01", "is_active": True, "notes": "501(c)(3) organization"}
]

MOCK_RETURNS = [
    {"id": 1, "jurisdiction_id": 2, "jurisdiction_name": "California", "period_start": "2024-01-01", "period_end": "2024-01-31", "filing_frequency": "monthly", "due_date": "2024-02-28", "status": "draft", "total_sales": 15000.00, "taxable_sales": 12000.00, "tax_collected": 870.00, "tax_due": 870.00}
]

@router.get("/dashboard/kpis")
async def get_tax_kpis(current_user: User = Depends(deps.get_current_active_user)):
    """Get tax dashboard KPIs"""
    total_liability = sum(t["tax_amount"] for t in MOCK_TRANSACTIONS)
    active_tax_codes = len([r for r in MOCK_TAX_RATES if r["is_active"]])
    pending_returns = len([r for r in MOCK_RETURNS if r["status"] in ["draft", "pending"]])
    
    return {
        "total_liability": total_liability,
        "liability_change": 8.2,
        "active_tax_codes": active_tax_codes,
        "pending_returns": pending_returns,
        "days_until_due": 15,
        "compliance_score": 98
    }

@router.get("/summary")
async def get_tax_summary(
    start_date: str = Query(...),
    end_date: str = Query(...),
    jurisdiction_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get tax summary for period"""
    transactions = MOCK_TRANSACTIONS.copy()
    
    if jurisdiction_id:
        transactions = [t for t in transactions if t["jurisdiction_id"] == jurisdiction_id]
    
    total_transactions = len(transactions)
    total_taxable_amount = sum(t["taxable_amount"] for t in transactions)
    total_tax_amount = sum(t["tax_amount"] for t in transactions)
    total_amount = sum(t["total_amount"] for t in transactions)
    
    # Group by jurisdiction
    by_jurisdiction = {}
    for t in transactions:
        jur = t["jurisdiction_name"]
        if jur not in by_jurisdiction:
            by_jurisdiction[jur] = {"jurisdiction_name": jur, "transaction_count": 0, "taxable_amount": 0, "tax_amount": 0}
        by_jurisdiction[jur]["transaction_count"] += 1
        by_jurisdiction[jur]["taxable_amount"] += t["taxable_amount"]
        by_jurisdiction[jur]["tax_amount"] += t["tax_amount"]
    
    # Group by tax type (simplified)
    by_tax_type = {
        "sales": {"tax_type": "sales", "transaction_count": total_transactions, "taxable_amount": total_taxable_amount, "tax_amount": total_tax_amount}
    }
    
    return {
        "period_start": start_date,
        "period_end": end_date,
        "summary": {
            "total_transactions": total_transactions,
            "total_taxable_amount": total_taxable_amount,
            "total_tax_amount": total_tax_amount,
            "total_amount": total_amount
        },
        "by_jurisdiction": list(by_jurisdiction.values()),
        "by_tax_type": list(by_tax_type.values())
    }

@router.get("/jurisdictions")
async def get_jurisdictions(
    level: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get tax jurisdictions"""
    jurisdictions = MOCK_JURISDICTIONS.copy()
    if level:
        jurisdictions = [j for j in jurisdictions if j["level"] == level]
    return jurisdictions

@router.post("/jurisdictions")
async def create_jurisdiction(
    jurisdiction_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create tax jurisdiction"""
    new_jurisdiction = {
        "id": max(j["id"] for j in MOCK_JURISDICTIONS) + 1,
        **jurisdiction_data,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    MOCK_JURISDICTIONS.append(new_jurisdiction)
    return new_jurisdiction

@router.get("/rates")
async def get_tax_rates(
    tax_type: Optional[str] = None,
    active_only: bool = True,
    jurisdiction_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get tax rates"""
    rates = MOCK_TAX_RATES.copy()
    
    if tax_type:
        rates = [r for r in rates if r["tax_type"] == tax_type]
    
    if active_only:
        rates = [r for r in rates if r["is_active"]]
    
    if jurisdiction_id:
        rates = [r for r in rates if r["jurisdiction_id"] == jurisdiction_id]
    
    return rates

@router.post("/rates")
async def create_tax_rate(
    rate_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create tax rate"""
    jurisdiction = next((j for j in MOCK_JURISDICTIONS if j["id"] == rate_data["jurisdiction_id"]), None)
    if not jurisdiction:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    
    new_rate = {
        "id": max(r["id"] for r in MOCK_TAX_RATES) + 1,
        **rate_data,
        "jurisdiction_name": jurisdiction["name"],
        "is_active": True
    }
    MOCK_TAX_RATES.append(new_rate)
    return new_rate

@router.get("/transactions")
async def get_tax_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    entity_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get tax transactions"""
    transactions = MOCK_TRANSACTIONS.copy()
    
    if entity_type:
        transactions = [t for t in transactions if t["entity_type"] == entity_type]
    
    # Date filtering would be implemented here
    
    total = len(transactions)
    start = (page - 1) * limit
    end = start + limit
    
    return transactions[start:end]

@router.post("/transactions")
async def create_tax_transaction(
    transaction_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create tax transaction"""
    new_transaction = {
        "id": max(t["id"] for t in MOCK_TRANSACTIONS) + 1,
        **transaction_data,
        "entity_name": f"Entity {transaction_data['entity_id']}",
        "jurisdiction_name": "California",  # Would lookup from jurisdiction_id
        "created_at": datetime.now().isoformat()
    }
    MOCK_TRANSACTIONS.append(new_transaction)
    return new_transaction

@router.post("/calculate")
async def calculate_tax(
    calculation_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Calculate tax amount"""
    taxable_amount = calculation_data["taxable_amount"]
    tax_rate_id = calculation_data["tax_rate_id"]
    
    rate = next((r for r in MOCK_TAX_RATES if r["id"] == tax_rate_id), None)
    if not rate:
        raise HTTPException(status_code=404, detail="Tax rate not found")
    
    tax_amount = taxable_amount * rate["rate"]
    total_amount = taxable_amount + tax_amount
    
    return {
        "taxable_amount": taxable_amount,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "tax_rate": rate["rate"]
    }

@router.get("/exemptions")
async def get_tax_exemptions(
    entity_type: Optional[str] = None,
    active_only: bool = True,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get tax exemptions"""
    exemptions = MOCK_EXEMPTIONS.copy()
    
    if entity_type:
        exemptions = [e for e in exemptions if e["entity_type"] == entity_type]
    
    if active_only:
        exemptions = [e for e in exemptions if e["is_active"]]
    
    return exemptions

@router.post("/exemptions")
async def create_tax_exemption(
    exemption_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create tax exemption"""
    new_exemption = {
        "id": max(e["id"] for e in MOCK_EXEMPTIONS) + 1,
        **exemption_data,
        "entity_name": f"Entity {exemption_data['entity_id']}",
        "jurisdiction_name": "California",  # Would lookup from jurisdiction_id
        "is_active": True
    }
    MOCK_EXEMPTIONS.append(new_exemption)
    return new_exemption

@router.get("/returns")
async def get_tax_returns(
    jurisdiction_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get tax returns"""
    returns = MOCK_RETURNS.copy()
    
    if jurisdiction_id:
        returns = [r for r in returns if r["jurisdiction_id"] == jurisdiction_id]
    
    if status:
        returns = [r for r in returns if r["status"] == status]
    
    return returns

@router.post("/returns")
async def create_tax_return(
    return_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create tax return"""
    jurisdiction = next((j for j in MOCK_JURISDICTIONS if j["id"] == return_data["jurisdiction_id"]), None)
    if not jurisdiction:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    
    new_return = {
        "id": max(r["id"] for r in MOCK_RETURNS) + 1,
        **return_data,
        "jurisdiction_name": jurisdiction["name"]
    }
    MOCK_RETURNS.append(new_return)
    return new_return

@router.get("/deadlines/upcoming")
async def get_upcoming_deadlines(current_user: User = Depends(deps.get_current_active_user)):
    """Get upcoming tax deadlines"""
    return [
        {
            "id": 1,
            "description": "Sales Tax Return - Q4 2024",
            "jurisdiction": "California",
            "due_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "days_remaining": 15,
            "status": "pending"
        },
        {
            "id": 2,
            "description": "VAT Return - January 2025",
            "jurisdiction": "Federal",
            "due_date": (datetime.now() + timedelta(days=28)).isoformat(),
            "days_remaining": 28,
            "status": "draft"
        }
    ]

@router.get("/reports/liability")
async def get_tax_liability_report(
    start_date: str = Query(...),
    end_date: str = Query(...),
    jurisdiction_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get tax liability report"""
    transactions = MOCK_TRANSACTIONS.copy()
    
    if jurisdiction_id:
        transactions = [t for t in transactions if t["jurisdiction_id"] == jurisdiction_id]
    
    total_liability = sum(t["tax_amount"] for t in transactions)
    
    return {
        "total_liability": total_liability,
        "by_period": [{"period": "2024-01", "amount": total_liability}],
        "by_jurisdiction": [{"jurisdiction": "California", "amount": total_liability}],
        "by_tax_type": [{"tax_type": "sales", "amount": total_liability}]
    }

@router.get("/reports/compliance")
async def get_tax_compliance_report(current_user: User = Depends(deps.get_current_active_user)):
    """Get tax compliance report"""
    return {
        "compliance_score": 98,
        "filed_on_time": 12,
        "filed_late": 1,
        "pending_filings": 2,
        "overdue_filings": 0,
        "recent_filings": MOCK_RETURNS[:3]
    }

@router.post("/import")
async def import_tax_data(
    file: UploadFile = File(...),
    type: str = Query(..., regex="^(transactions|rates|exemptions)$"),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Import tax data from CSV/Excel file"""
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    return {"success": 8, "errors": ["Row 3: Invalid tax rate format"]}

@router.get("/export/{data_type}")
async def export_tax_data(
    data_type: str,
    format: str = Query("csv", regex="^(csv|excel)$"),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Export tax data to CSV or Excel"""
    if data_type not in ["transactions", "rates", "exemptions"]:
        raise HTTPException(status_code=400, detail="Invalid data type")
    
    if format == "csv":
        data_map = {
            "transactions": MOCK_TRANSACTIONS,
            "rates": MOCK_TAX_RATES,
            "exemptions": MOCK_EXEMPTIONS
        }
        
        data = data_map[data_type]
        output = io.StringIO()
        
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        response = StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=tax_{data_type}.csv"}
        )
        return response
    
    return {"message": "Excel export would be implemented here"}