from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
import io
import csv

router = APIRouter()

# Mock data
MOCK_ASSETS = [
    {
        "id": 1, "asset_number": "FA001", "asset_name": "Office Computer", "description": "Dell OptiPlex 7090",
        "asset_category": "IT Equipment", "location": "Main Office", "purchase_date": "2023-01-15",
        "purchase_cost": 1500.00, "salvage_value": 150.00, "useful_life_years": 5,
        "depreciation_method": "straight_line", "accumulated_depreciation": 450.00, "current_value": 1050.00,
        "status": "active", "vendor_name": "Dell Inc", "warranty_expiry": "2026-01-15",
        "created_at": "2023-01-15T10:00:00Z", "updated_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": 2, "asset_number": "FA002", "asset_name": "Office Desk", "description": "Executive wooden desk",
        "asset_category": "Furniture", "location": "Main Office", "purchase_date": "2022-06-10",
        "purchase_cost": 800.00, "salvage_value": 80.00, "useful_life_years": 10,
        "depreciation_method": "straight_line", "accumulated_depreciation": 144.00, "current_value": 656.00,
        "status": "active", "vendor_name": "Office Furniture Co", "warranty_expiry": "2024-06-10",
        "created_at": "2022-06-10T10:00:00Z", "updated_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": 3, "asset_number": "FA003", "asset_name": "Company Vehicle", "description": "Toyota Camry 2023",
        "asset_category": "Vehicle", "location": "Parking Lot", "purchase_date": "2023-03-20",
        "purchase_cost": 28000.00, "salvage_value": 8000.00, "useful_life_years": 8,
        "depreciation_method": "straight_line", "accumulated_depreciation": 2083.33, "current_value": 25916.67,
        "status": "maintenance", "vendor_name": "Toyota Dealer", "warranty_expiry": "2026-03-20",
        "next_maintenance": "2024-02-15", "created_at": "2023-03-20T10:00:00Z", "updated_at": "2024-01-15T10:00:00Z"
    }
]

MOCK_MAINTENANCE = [
    {
        "id": 1, "asset_id": 3, "asset_name": "Company Vehicle", "maintenance_type": "preventive",
        "description": "Regular oil change and inspection", "scheduled_date": "2024-02-15",
        "status": "scheduled", "estimated_cost": 150.00, "vendor_name": "Auto Service Center",
        "created_by": "John Doe", "created_at": "2024-01-10T10:00:00Z"
    },
    {
        "id": 2, "asset_id": 1, "asset_name": "Office Computer", "maintenance_type": "corrective",
        "description": "Replace faulty RAM module", "scheduled_date": "2024-01-20",
        "completed_date": "2024-01-20", "status": "completed", "estimated_cost": 100.00,
        "actual_cost": 95.00, "vendor_name": "IT Support Co", "created_by": "Jane Smith",
        "created_at": "2024-01-18T10:00:00Z"
    }
]

MOCK_CATEGORIES = [
    {"id": 1, "name": "IT Equipment", "description": "Computers, servers, networking equipment", 
     "default_useful_life": 5, "default_depreciation_method": "straight_line", "default_salvage_rate": 0.1, "asset_count": 1},
    {"id": 2, "name": "Furniture", "description": "Office furniture and fixtures",
     "default_useful_life": 10, "default_depreciation_method": "straight_line", "default_salvage_rate": 0.1, "asset_count": 1},
    {"id": 3, "name": "Vehicle", "description": "Company vehicles",
     "default_useful_life": 8, "default_depreciation_method": "straight_line", "default_salvage_rate": 0.3, "asset_count": 1},
    {"id": 4, "name": "Machinery", "description": "Manufacturing and production equipment",
     "default_useful_life": 15, "default_depreciation_method": "straight_line", "default_salvage_rate": 0.05, "asset_count": 0}
]

@router.get("/stats")
async def get_asset_stats(current_user: User = Depends(deps.get_current_active_user)):
    """Get fixed assets statistics"""
    total_cost = sum(asset["purchase_cost"] for asset in MOCK_ASSETS)
    total_depreciation = sum(asset["accumulated_depreciation"] for asset in MOCK_ASSETS)
    total_current_value = sum(asset["current_value"] for asset in MOCK_ASSETS)
    maintenance_due = len([m for m in MOCK_MAINTENANCE if m["status"] == "scheduled"])
    
    return {
        "total_assets": len(MOCK_ASSETS),
        "total_cost": total_cost,
        "total_accumulated_depreciation": total_depreciation,
        "total_current_value": total_current_value,
        "monthly_depreciation": total_depreciation / 12,  # Simplified calculation
        "maintenance_due": maintenance_due
    }

@router.get("/assets")
async def get_assets(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get fixed assets with filtering and pagination"""
    assets = MOCK_ASSETS.copy()
    
    if search:
        assets = [a for a in assets if search.lower() in a["asset_name"].lower() or search.lower() in a["asset_number"].lower()]
    
    if category:
        assets = [a for a in assets if a["asset_category"] == category]
    
    if status:
        assets = [a for a in assets if a["status"] == status]
    
    total = len(assets)
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "assets": assets[start:end],
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/assets/{asset_id}")
async def get_asset(
    asset_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get specific fixed asset"""
    asset = next((a for a in MOCK_ASSETS if a["id"] == asset_id), None)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.post("/assets")
async def create_asset(
    asset_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create new fixed asset"""
    new_asset = {
        "id": max(a["id"] for a in MOCK_ASSETS) + 1,
        **asset_data,
        "accumulated_depreciation": 0.0,
        "current_value": asset_data["purchase_cost"],
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    MOCK_ASSETS.append(new_asset)
    return new_asset

@router.put("/assets/{asset_id}")
async def update_asset(
    asset_id: int,
    asset_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Update fixed asset"""
    asset_index = next((i for i, a in enumerate(MOCK_ASSETS) if a["id"] == asset_id), None)
    if asset_index is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    MOCK_ASSETS[asset_index].update(asset_data)
    MOCK_ASSETS[asset_index]["updated_at"] = datetime.now().isoformat()
    return MOCK_ASSETS[asset_index]

@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Delete fixed asset"""
    asset_index = next((i for i, a in enumerate(MOCK_ASSETS) if a["id"] == asset_id), None)
    if asset_index is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    MOCK_ASSETS.pop(asset_index)
    return {"message": "Asset deleted successfully"}

@router.get("/categories")
async def get_categories(current_user: User = Depends(deps.get_current_active_user)):
    """Get asset categories"""
    return MOCK_CATEGORIES

@router.post("/categories")
async def create_category(
    category_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create new asset category"""
    new_category = {
        "id": max(c["id"] for c in MOCK_CATEGORIES) + 1,
        **category_data,
        "asset_count": 0
    }
    MOCK_CATEGORIES.append(new_category)
    return new_category

@router.get("/maintenance")
async def get_maintenance_records(
    asset_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get maintenance records"""
    records = MOCK_MAINTENANCE.copy()
    if asset_id:
        records = [r for r in records if r["asset_id"] == asset_id]
    return records

@router.post("/maintenance")
async def create_maintenance_record(
    maintenance_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create maintenance record"""
    asset = next((a for a in MOCK_ASSETS if a["id"] == maintenance_data["asset_id"]), None)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    new_maintenance = {
        "id": max(m["id"] for m in MOCK_MAINTENANCE) + 1,
        **maintenance_data,
        "asset_name": asset["asset_name"],
        "created_by": current_user.full_name,
        "created_at": datetime.now().isoformat()
    }
    MOCK_MAINTENANCE.append(new_maintenance)
    return new_maintenance

@router.get("/maintenance/upcoming")
async def get_upcoming_maintenance(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get upcoming maintenance"""
    cutoff_date = datetime.now() + timedelta(days=days)
    upcoming = [
        m for m in MOCK_MAINTENANCE 
        if m["status"] == "scheduled" and datetime.fromisoformat(m["scheduled_date"].replace('Z', '+00:00')) <= cutoff_date
    ]
    return upcoming

@router.get("/assets/{asset_id}/depreciation")
async def get_depreciation_schedule(
    asset_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get depreciation schedule for asset"""
    asset = next((a for a in MOCK_ASSETS if a["id"] == asset_id), None)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Mock depreciation schedule
    schedule = []
    monthly_depreciation = (asset["purchase_cost"] - asset["salvage_value"]) / (asset["useful_life_years"] * 12)
    
    for i in range(12):  # Show 12 months
        date = datetime.now().replace(day=1) + timedelta(days=32*i)
        accumulated = monthly_depreciation * (i + 1)
        schedule.append({
            "id": i + 1,
            "asset_id": asset_id,
            "period_date": date.strftime("%Y-%m-%d"),
            "depreciation_amount": monthly_depreciation,
            "accumulated_depreciation": accumulated,
            "book_value": asset["purchase_cost"] - accumulated,
            "created_at": datetime.now().isoformat()
        })
    
    return schedule

@router.post("/assets/{asset_id}/dispose")
async def dispose_asset(
    asset_id: int,
    disposal_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Dispose of an asset"""
    asset_index = next((i for i, a in enumerate(MOCK_ASSETS) if a["id"] == asset_id), None)
    if asset_index is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset = MOCK_ASSETS[asset_index]
    gain_loss = disposal_data["disposal_amount"] - asset["current_value"]
    
    # Update asset status
    MOCK_ASSETS[asset_index]["status"] = "disposed"
    MOCK_ASSETS[asset_index]["updated_at"] = datetime.now().isoformat()
    
    disposal = {
        "id": 1,
        "asset_id": asset_id,
        **disposal_data,
        "gain_loss": gain_loss,
        "created_by": current_user.full_name,
        "created_at": datetime.now().isoformat()
    }
    
    return disposal

@router.get("/reports/valuation")
async def get_valuation_report(current_user: User = Depends(deps.get_current_active_user)):
    """Get asset valuation report"""
    by_category = {}
    by_status = {}
    
    for asset in MOCK_ASSETS:
        # By category
        cat = asset["asset_category"]
        if cat not in by_category:
            by_category[cat] = {"category": cat, "count": 0, "cost": 0, "current_value": 0}
        by_category[cat]["count"] += 1
        by_category[cat]["cost"] += asset["purchase_cost"]
        by_category[cat]["current_value"] += asset["current_value"]
        
        # By status
        status = asset["status"]
        if status not in by_status:
            by_status[status] = {"status": status, "count": 0, "value": 0}
        by_status[status]["count"] += 1
        by_status[status]["value"] += asset["current_value"]
    
    total_cost = sum(a["purchase_cost"] for a in MOCK_ASSETS)
    total_current_value = sum(a["current_value"] for a in MOCK_ASSETS)
    total_depreciation = sum(a["accumulated_depreciation"] for a in MOCK_ASSETS)
    
    return {
        "by_category": list(by_category.values()),
        "by_status": list(by_status.values()),
        "total_cost": total_cost,
        "total_current_value": total_current_value,
        "total_depreciation": total_depreciation
    }

@router.post("/import")
async def import_assets(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Import assets from CSV/Excel file"""
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    return {"success": 5, "errors": ["Row 3: Invalid date format"]}

@router.get("/export")
async def export_assets(
    format: str = Query("csv", regex="^(csv|excel)$"),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Export assets to CSV or Excel"""
    if format == "csv":
        output = io.StringIO()
        if MOCK_ASSETS:
            writer = csv.DictWriter(output, fieldnames=MOCK_ASSETS[0].keys())
            writer.writeheader()
            writer.writerows(MOCK_ASSETS)
        
        response = StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=fixed_assets.csv"}
        )
        return response
    
    return {"message": "Excel export would be implemented here"}