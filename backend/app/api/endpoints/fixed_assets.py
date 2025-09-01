"""
Fixed Assets API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

# Mock data for fixed assets
MOCK_ASSETS = [
    {
        "id": 1,
        "name": "Office Computer",
        "asset_number": "FA-001",
        "category": "IT Equipment",
        "purchase_cost": 1500.00,
        "accumulated_depreciation": 300.00,
        "book_value": 1200.00,
        "purchase_date": "2023-01-15",
        "useful_life_years": 5,
        "salvage_value": 100.00,
        "depreciation_method": "straight_line",
        "status": "active",
        "location": "Main Office",
        "department": "IT"
    },
    {
        "id": 2,
        "name": "Office Printer",
        "asset_number": "FA-002", 
        "category": "Office Equipment",
        "purchase_cost": 500.00,
        "accumulated_depreciation": 100.00,
        "book_value": 400.00,
        "purchase_date": "2023-03-20",
        "useful_life_years": 3,
        "salvage_value": 50.00,
        "depreciation_method": "straight_line",
        "status": "active",
        "location": "Main Office",
        "department": "Administration"
    }
]

MOCK_MAINTENANCE = [
    {
        "id": 1,
        "asset_id": 1,
        "maintenance_type": "Preventive",
        "description": "Regular system maintenance",
        "scheduled_date": "2024-02-15",
        "status": "scheduled",
        "estimated_cost": 150.00,
        "actual_cost": None,
        "vendor_name": "Tech Support Co",
        "notes": "Annual maintenance check"
    }
]

@router.get("/assets")
async def get_assets():
    """Get all fixed assets"""
    return MOCK_ASSETS

@router.get("/assets/{asset_id}")
async def get_asset(asset_id: int):
    """Get a specific asset by ID"""
    asset = next((a for a in MOCK_ASSETS if a["id"] == asset_id), None)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.get("/maintenance")
async def get_maintenance_records():
    """Get all maintenance records"""
    return MOCK_MAINTENANCE

@router.get("/maintenance/{maintenance_id}")
async def get_maintenance_record(maintenance_id: int):
    """Get a specific maintenance record by ID"""
    record = next((m for m in MOCK_MAINTENANCE if m["id"] == maintenance_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return record

@router.post("/maintenance")
async def create_maintenance_record(maintenance_data: Dict[str, Any]):
    """Create a new maintenance record"""
    new_id = max([m["id"] for m in MOCK_MAINTENANCE], default=0) + 1
    new_record = {
        "id": new_id,
        **maintenance_data
    }
    MOCK_MAINTENANCE.append(new_record)
    return new_record

@router.put("/maintenance/{maintenance_id}")
async def update_maintenance_record(maintenance_id: int, maintenance_data: Dict[str, Any]):
    """Update a maintenance record"""
    record = next((m for m in MOCK_MAINTENANCE if m["id"] == maintenance_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    record.update(maintenance_data)
    return record

@router.get("/reports")
async def get_asset_reports():
    """Get asset reports data"""
    total_assets = len(MOCK_ASSETS)
    total_cost = sum(asset["purchase_cost"] for asset in MOCK_ASSETS)
    total_accumulated_depreciation = sum(asset["accumulated_depreciation"] for asset in MOCK_ASSETS)
    total_book_value = sum(asset["book_value"] for asset in MOCK_ASSETS)
    
    # Group by category
    assets_by_category = {}
    for asset in MOCK_ASSETS:
        category = asset["category"]
        if category not in assets_by_category:
            assets_by_category[category] = {"category": category, "count": 0, "total_cost": 0}
        assets_by_category[category]["count"] += 1
        assets_by_category[category]["total_cost"] += asset["purchase_cost"]
    
    # Group by status
    assets_by_status = {}
    for asset in MOCK_ASSETS:
        status = asset["status"]
        if status not in assets_by_status:
            assets_by_status[status] = {"status": status, "count": 0}
        assets_by_status[status]["count"] += 1
    
    return {
        "total_assets": total_assets,
        "total_cost": total_cost,
        "total_accumulated_depreciation": total_accumulated_depreciation,
        "total_book_value": total_book_value,
        "assets_by_category": list(assets_by_category.values()),
        "assets_by_status": list(assets_by_status.values())
    }