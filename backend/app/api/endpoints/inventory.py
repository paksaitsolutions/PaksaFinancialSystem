from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
import io
import csv
import pandas as pd

router = APIRouter()

# Mock data for demonstration
MOCK_ITEMS = [
    {
        "id": 1, "sku": "WPM001", "name": "Widget Pro Max", "description": "Premium widget with advanced features",
        "category_id": 1, "category_name": "Widgets", "location_id": 1, "location_name": "Main Warehouse",
        "quantity": 150, "unit_price": 25.99, "total_value": 3898.50, "reorder_point": 50, "max_stock": 500,
        "unit_of_measure": "pcs", "barcode": "123456789012", "supplier_id": 1, "supplier_name": "Widget Corp",
        "last_updated": "2024-01-15T10:30:00Z", "status": "in_stock"
    },
    {
        "id": 2, "sku": "CX002", "name": "Component X", "description": "Essential component for assembly",
        "category_id": 2, "category_name": "Components", "location_id": 1, "location_name": "Main Warehouse",
        "quantity": 12, "unit_price": 15.50, "total_value": 186.00, "reorder_point": 25, "max_stock": 200,
        "unit_of_measure": "pcs", "barcode": "123456789013", "supplier_id": 2, "supplier_name": "Component Ltd",
        "last_updated": "2024-01-15T09:15:00Z", "status": "low_stock"
    },
    {
        "id": 3, "sku": "AK003", "name": "Assembly Kit", "description": "Complete assembly kit",
        "category_id": 3, "category_name": "Kits", "location_id": 2, "location_name": "Assembly Floor",
        "quantity": 0, "unit_price": 45.00, "total_value": 0.00, "reorder_point": 10, "max_stock": 100,
        "unit_of_measure": "kits", "barcode": "123456789014", "supplier_id": 1, "supplier_name": "Widget Corp",
        "last_updated": "2024-01-14T16:45:00Z", "status": "out_of_stock"
    }
]

MOCK_TRANSACTIONS = [
    {
        "id": 1, "item_id": 1, "item_name": "Widget Pro Max", "item_sku": "WPM001",
        "type": "stock_in", "quantity": 50, "unit_price": 25.99, "total_value": 1299.50,
        "reference_number": "PO-2024-001", "notes": "Regular restock", "created_by": "John Doe",
        "created_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": 2, "item_id": 2, "item_name": "Component X", "item_sku": "CX002",
        "type": "stock_out", "quantity": -25, "reference_number": "SO-2024-015",
        "notes": "Production use", "created_by": "Jane Smith", "created_at": "2024-01-15T08:15:00Z"
    }
]

MOCK_ALERTS = [
    {
        "id": 1, "item_id": 2, "item_name": "Component X", "item_sku": "CX002",
        "alert_type": "low_stock", "severity": "high", "message": "Stock below reorder point (12 units remaining)",
        "current_quantity": 12, "threshold_quantity": 25, "created_at": "2024-01-15T09:00:00Z",
        "acknowledged": False
    },
    {
        "id": 2, "item_id": 3, "item_name": "Assembly Kit", "item_sku": "AK003",
        "alert_type": "out_of_stock", "severity": "critical", "message": "Out of stock - reorder immediately",
        "current_quantity": 0, "threshold_quantity": 10, "created_at": "2024-01-14T16:45:00Z",
        "acknowledged": False
    }
]

@router.get("/dashboard/kpis")
async def get_dashboard_kpis(current_user: User = Depends(deps.get_current_active_user)):
    """Get inventory dashboard KPIs"""
    total_items = len(MOCK_ITEMS)
    low_stock = len([item for item in MOCK_ITEMS if item["status"] == "low_stock"])
    out_of_stock = len([item for item in MOCK_ITEMS if item["status"] == "out_of_stock"])
    total_value = sum(item["total_value"] for item in MOCK_ITEMS)
    
    return {
        "total_items": total_items,
        "total_items_change": 8.2,
        "low_stock_count": low_stock,
        "out_of_stock_count": out_of_stock,
        "total_value": total_value,
        "total_value_change": 12.4,
        "turnover_ratio": 4.2,
        "avg_days_to_sell": 87
    }

@router.get("/dashboard/movements")
async def get_stock_movements(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get stock movements for dashboard chart"""
    movements = []
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        movements.append({
            "date": date.strftime("%Y-%m-%d"),
            "stock_in": 50 + (i % 20),
            "stock_out": 30 + (i % 15),
            "adjustments": (i % 5) - 2,
            "net_change": 20 + (i % 10)
        })
    
    return movements

@router.get("/transactions/recent")
async def get_recent_transactions(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get recent inventory transactions"""
    return MOCK_TRANSACTIONS[:limit]

@router.get("/alerts")
async def get_stock_alerts(
    acknowledged: bool = Query(False),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get stock alerts"""
    return [alert for alert in MOCK_ALERTS if alert["acknowledged"] == acknowledged]

@router.get("/items")
async def get_items(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get inventory items with filtering and pagination"""
    items = MOCK_ITEMS.copy()
    
    if search:
        items = [item for item in items if search.lower() in item["name"].lower() or search.lower() in item["sku"].lower()]
    
    if category_id:
        items = [item for item in items if item["category_id"] == category_id]
    
    if location_id:
        items = [item for item in items if item["location_id"] == location_id]
    
    if status:
        items = [item for item in items if item["status"] == status]
    
    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.get("/items/{item_id}")
async def get_item(
    item_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get specific inventory item"""
    item = next((item for item in MOCK_ITEMS if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/items")
async def create_item(
    item_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create new inventory item"""
    new_item = {
        "id": max(item["id"] for item in MOCK_ITEMS) + 1,
        **item_data,
        "total_value": item_data["quantity"] * item_data["unit_price"],
        "last_updated": datetime.now().isoformat(),
        "status": "in_stock" if item_data["quantity"] > item_data.get("reorder_point", 0) else "low_stock"
    }
    MOCK_ITEMS.append(new_item)
    return new_item

@router.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Update inventory item"""
    item_index = next((i for i, item in enumerate(MOCK_ITEMS) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    MOCK_ITEMS[item_index].update(item_data)
    MOCK_ITEMS[item_index]["last_updated"] = datetime.now().isoformat()
    if "quantity" in item_data and "unit_price" in item_data:
        MOCK_ITEMS[item_index]["total_value"] = item_data["quantity"] * item_data["unit_price"]
    
    return MOCK_ITEMS[item_index]

@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Delete inventory item"""
    item_index = next((i for i, item in enumerate(MOCK_ITEMS) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    MOCK_ITEMS.pop(item_index)
    return {"message": "Item deleted successfully"}

@router.post("/adjustments")
async def adjust_stock(
    adjustments_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Perform stock adjustments"""
    adjustments = adjustments_data.get("adjustments", [])
    transactions = []
    
    for adj in adjustments:
        item = next((item for item in MOCK_ITEMS if item["id"] == adj["item_id"]), None)
        if not item:
            continue
        
        if adj["type"] == "increase":
            item["quantity"] += adj["quantity"]
        elif adj["type"] == "decrease":
            item["quantity"] = max(0, item["quantity"] - adj["quantity"])
        elif adj["type"] == "set":
            item["quantity"] = adj["quantity"]
        
        item["total_value"] = item["quantity"] * item["unit_price"]
        item["last_updated"] = datetime.now().isoformat()
        
        transaction = {
            "id": len(MOCK_TRANSACTIONS) + len(transactions) + 1,
            "item_id": item["id"],
            "item_name": item["name"],
            "item_sku": item["sku"],
            "type": "adjustment",
            "quantity": adj["quantity"] if adj["type"] == "increase" else -adj["quantity"],
            "notes": adj.get("notes", ""),
            "created_by": current_user.full_name,
            "created_at": datetime.now().isoformat()
        }
        transactions.append(transaction)
    
    return transactions

@router.get("/categories")
async def get_categories(current_user: User = Depends(deps.get_current_active_user)):
    """Get inventory categories"""
    return [
        {"id": 1, "name": "Widgets", "description": "Widget products", "item_count": 1, "total_value": 3898.50},
        {"id": 2, "name": "Components", "description": "Component parts", "item_count": 1, "total_value": 186.00},
        {"id": 3, "name": "Kits", "description": "Assembly kits", "item_count": 1, "total_value": 0.00}
    ]

@router.get("/locations")
async def get_locations(current_user: User = Depends(deps.get_current_active_user)):
    """Get inventory locations"""
    return [
        {"id": 1, "name": "Main Warehouse", "code": "WH001", "type": "warehouse", "item_count": 2, "total_value": 4084.50},
        {"id": 2, "name": "Assembly Floor", "code": "AF001", "type": "warehouse", "item_count": 1, "total_value": 0.00}
    ]

@router.get("/transactions")
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    item_id: Optional[int] = None,
    type: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get inventory transactions"""
    transactions = MOCK_TRANSACTIONS.copy()
    
    if item_id:
        transactions = [t for t in transactions if t["item_id"] == item_id]
    
    if type:
        transactions = [t for t in transactions if t["type"] == type]
    
    total = len(transactions)
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "transactions": transactions[start:end],
        "total": total,
        "page": page,
        "limit": limit
    }

@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Acknowledge a stock alert"""
    alert = next((alert for alert in MOCK_ALERTS if alert["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert["acknowledged"] = True
    return {"message": "Alert acknowledged"}

@router.get("/reports/valuation")
async def get_inventory_valuation(current_user: User = Depends(deps.get_current_active_user)):
    """Get inventory valuation report"""
    total_value = sum(item["total_value"] for item in MOCK_ITEMS)
    
    by_category = [
        {"category": "Widgets", "value": 3898.50, "percentage": 95.4},
        {"category": "Components", "value": 186.00, "percentage": 4.6},
        {"category": "Kits", "value": 0.00, "percentage": 0.0}
    ]
    
    by_location = [
        {"location": "Main Warehouse", "value": 4084.50, "percentage": 100.0},
        {"location": "Assembly Floor", "value": 0.00, "percentage": 0.0}
    ]
    
    return {
        "by_category": by_category,
        "by_location": by_location,
        "total_value": total_value
    }

@router.get("/reports/stock-levels")
async def get_stock_levels_report(current_user: User = Depends(deps.get_current_active_user)):
    """Get stock levels report"""
    in_stock = len([item for item in MOCK_ITEMS if item["status"] == "in_stock"])
    low_stock = len([item for item in MOCK_ITEMS if item["status"] == "low_stock"])
    out_of_stock = len([item for item in MOCK_ITEMS if item["status"] == "out_of_stock"])
    
    return {
        "in_stock": in_stock,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "overstock": 0,
        "items": MOCK_ITEMS
    }

@router.get("/items/barcode/{barcode}")
async def search_by_barcode(
    barcode: str,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Search item by barcode"""
    item = next((item for item in MOCK_ITEMS if item.get("barcode") == barcode), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/import")
async def import_items(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Import items from CSV/Excel file"""
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    # Mock import process
    return {
        "success": 10,
        "errors": ["Row 5: Invalid SKU format", "Row 8: Missing required field 'name'"]
    }

@router.get("/export")
async def export_items(
    format: str = Query("csv", regex="^(csv|excel)$"),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Export items to CSV or Excel"""
    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=MOCK_ITEMS[0].keys())
        writer.writeheader()
        writer.writerows(MOCK_ITEMS)
        
        response = StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=inventory_items.csv"}
        )
        return response
    
    # For Excel format, return mock response
    return {"message": "Excel export would be implemented here"}