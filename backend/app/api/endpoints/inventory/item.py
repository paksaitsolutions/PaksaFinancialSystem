"""
API endpoints for inventory item management.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.db.router import db_router
from app.core.api_response import success_response, error_response
from app.core.permissions import require_permission, Permission
from app.crud.inventory.item import inventory_item_crud
from app.schemas.inventory.item import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
)
# Temporarily disabled: from app.services.inventory.transfer_service import TransferService
# Temporarily disabled: from app.services.inventory.cycle_count_service import CycleCountService
# Temporarily disabled: from app.services.inventory.barcode_service import BarcodeService

router = APIRouter()

# Initialize services - temporarily disabled to avoid conflicts
# transfer_service = TransferService()
# cycle_service = CycleCountService()
# barcode_service = BarcodeService()

@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_in: InventoryItemCreate,
    _: bool = Depends(require_permission(Permission.INVENTORY_WRITE)),
) -> Any:
    """
    Create a new inventory item.
    """
    # Check if item with same SKU already exists
    existing_item = await inventory_item_crud.get_by_sku(db, sku=item_in.sku)
    if existing_item:
        return error_response(
            message=f"Inventory item with SKU {item_in.sku} already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    item = await inventory_item_crud.create(db, obj_in=item_in)
    return success_response(
        data=item,
        message="Inventory item created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/")
async def get_inventory_items(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.INVENTORY_READ)),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
    name: Optional[str] = Query(None, description="Filter by name"),
    sku: Optional[str] = Query(None, description="Filter by SKU"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
) -> Any:
    """
    Get list of inventory items with pagination and filtering.
    """
    # Build filters
    filters = {}
    if name:
        filters["name"] = name
    if sku:
        filters["sku"] = sku
    if status:
        filters["status"] = status
    if category_id:
        filters["category_id"] = category_id
    
    result = await inventory_item_crud.get_paginated(
        db,
        page=page,
        page_size=page_size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    return success_response(
        data=result["items"],
        meta={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": result["pagination"]["total"],
                "pages": result["pagination"]["total_pages"],
            }
        },
    )

@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    item_id: UUID,
    _: bool = Depends(require_permission(Permission.INVENTORY_READ)),
) -> Any:
    """
    Get a specific inventory item by ID.
    """
    item = await inventory_item_crud.get(db, id=item_id)
    if not item:
        return error_response(
            message="Inventory item not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return success_response(data=item)

@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: UUID,
    item_in: InventoryItemUpdate,
    _: bool = Depends(require_permission(Permission.INVENTORY_WRITE)),
) -> Any:
    """
    Update an inventory item.
    """
    item = await inventory_item_crud.get(db, id=item_id)
    if not item:
        return error_response(
            message="Inventory item not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if SKU is being changed and if it already exists
    if item_in.sku and item_in.sku != item.sku:
        existing_item = await inventory_item_crud.get_by_sku(db, sku=item_in.sku)
        if existing_item:
            return error_response(
                message=f"Inventory item with SKU {item_in.sku} already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    
    item = await inventory_item_crud.update(db, db_obj=item, obj_in=item_in)
    return success_response(
        data=item,
        message="Inventory item updated successfully",
    )

@router.delete("/{item_id}")
async def delete_inventory_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: UUID,
    _: bool = Depends(require_permission(Permission.INVENTORY_DELETE)),
) -> Any:
    """
    Delete an inventory item.
    """
    item = await inventory_item_crud.get(db, id=item_id)
    if not item:
        return error_response(
            message="Inventory item not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    await inventory_item_crud.delete(db, id=item_id)
    return success_response(
        message="Inventory item deleted successfully",
    )

# Multi-location transfer endpoints
@router.post("/transfers")
async def create_transfer(
    *,
    db: AsyncSession = Depends(get_db),
    transfer_data: dict,
    _: bool = Depends(require_permission(Permission.INVENTORY_WRITE)),
) -> Any:
    """Create location transfer."""
    transfer_service = TransferService()
    transfer = await transfer_service.create_transfer(
        db, tenant_id=UUID("12345678-1234-5678-9012-123456789012"), transfer_data=transfer_data
    )
    return success_response(
        data=transfer,
        message="Transfer created successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.post("/transfers/{transfer_id}/approve")
async def approve_transfer(
    *,
    db: AsyncSession = Depends(get_db),
    transfer_id: UUID,
    _: bool = Depends(require_permission(Permission.INVENTORY_WRITE)),
) -> Any:
    """Approve transfer."""
    transfer_service = TransferService()
    transfer = await transfer_service.approve_transfer(
        db, transfer_id=transfer_id, approved_by=UUID("12345678-1234-5678-9012-123456789012")
    )
    return success_response(
        data=transfer,
        message="Transfer approved successfully"
    )

@router.post("/transfers/{transfer_id}/ship")
async def ship_transfer(
    *,
    db: AsyncSession = Depends(get_db),
    transfer_id: UUID,
    shipping_data: dict,
    _: bool = Depends(require_permission(Permission.INVENTORY_WRITE)),
) -> Any:
    """Ship transfer."""
    transfer_service = TransferService()
    transfer = await transfer_service.ship_transfer(
        db, transfer_id=transfer_id, shipping_data=shipping_data
    )
    return success_response(
        data=transfer,
        message="Transfer shipped successfully"
    )

@router.get("/transfers/{transfer_id}/status")
async def get_transfer_status(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    transfer_id: UUID,
    _: bool = Depends(require_permission(Permission.INVENTORY_READ)),
) -> Any:
    """Get transfer status."""
    transfer_service = TransferService()
    status_data = await transfer_service.get_transfer_status(db, transfer_id=transfer_id)
    return success_response(data=status_data)

# Cycle counting endpoints
@router.post("/cycle-counts")
async def create_cycle_count(
    *,
    db: AsyncSession = Depends(get_db),
    count_data: dict,
    _: bool = Depends(require_permission(Permission.INVENTORY_WRITE)),
) -> Any:
    """Create cycle count."""
    cycle_service = CycleCountService()
    cycle_count = await cycle_service.create_cycle_count(
        db, tenant_id=UUID("12345678-1234-5678-9012-123456789012"), count_data=count_data
    )
    return success_response(
        data=cycle_count,
        message="Cycle count created successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.post("/cycle-counts/{count_id}/record")
async def record_count(
    *,
    db: AsyncSession = Depends(get_db),
    count_id: UUID,
    item_id: UUID = Query(...),
    counted_quantity: float = Query(...),
    _: bool = Depends(require_permission(Permission.INVENTORY_WRITE)),
) -> Any:
    """Record counted quantity."""
    cycle_service = CycleCountService()
    count_item = await cycle_service.record_count(
        db, cycle_count_id=count_id, item_id=item_id, counted_quantity=counted_quantity
    )
    return success_response(
        data=count_item,
        message="Count recorded successfully"
    )

@router.post("/cycle-counts/{count_id}/complete")
async def complete_cycle_count(
    *,
    db: AsyncSession = Depends(get_db),
    count_id: UUID,
    _: bool = Depends(require_permission(Permission.INVENTORY_WRITE)),
) -> Any:
    """Complete cycle count."""
    cycle_service = CycleCountService()
    cycle_count = await cycle_service.complete_cycle_count(
        db, cycle_count_id=count_id, completed_by=UUID("12345678-1234-5678-9012-123456789012")
    )
    return success_response(
        data=cycle_count,
        message="Cycle count completed successfully"
    )

@router.get("/cycle-counts/{count_id}/report")
async def get_cycle_count_report(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    count_id: UUID,
    _: bool = Depends(require_permission(Permission.INVENTORY_READ)),
) -> Any:
    """Get cycle count report."""
    cycle_service = CycleCountService()
    report = await cycle_service.get_cycle_count_report(db, cycle_count_id=count_id)
    return success_response(data=report)

# Barcode scanning endpoints
@router.post("/barcodes/scan")
async def scan_barcode(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    barcode: str = Query(...),
    _: bool = Depends(require_permission(Permission.INVENTORY_READ)),
) -> Any:
    """Scan barcode and get item info."""
    barcode_service = BarcodeService()
    result = await barcode_service.scan_barcode(
        db, tenant_id=UUID("12345678-1234-5678-9012-123456789012"), barcode=barcode
    )
    return success_response(data=result)

@router.post("/barcodes/mapping")
async def create_barcode_mapping(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: UUID = Query(...),
    barcode: str = Query(...),
    barcode_type: str = Query("UPC"),
    is_primary: bool = Query(False),
    _: bool = Depends(require_permission(Permission.INVENTORY_WRITE)),
) -> Any:
    """Create barcode mapping."""
    barcode_service = BarcodeService()
    mapping = await barcode_service.create_barcode_mapping(
        db, 
        tenant_id=UUID("12345678-1234-5678-9012-123456789012"),
        item_id=item_id,
        barcode=barcode,
        barcode_type=barcode_type,
        is_primary=is_primary
    )
    return success_response(
        data=mapping,
        message="Barcode mapping created successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.post("/barcodes/update-quantity")
async def update_quantity_by_barcode(
    *,
    db: AsyncSession = Depends(get_db),
    barcode: str = Query(...),
    quantity_change: float = Query(...),
    transaction_type: str = Query("adjustment"),
    notes: Optional[str] = Query(None),
    _: bool = Depends(require_permission(Permission.INVENTORY_WRITE)),
) -> Any:
    """Update item quantity by barcode."""
    barcode_service = BarcodeService()
    result = await barcode_service.update_item_quantity_by_barcode(
        db,
        tenant_id=UUID("12345678-1234-5678-9012-123456789012"),
        barcode=barcode,
        quantity_change=quantity_change,
        transaction_type=transaction_type,
        notes=notes
    )
    return success_response(
        data=result,
        message="Quantity updated successfully"
    )