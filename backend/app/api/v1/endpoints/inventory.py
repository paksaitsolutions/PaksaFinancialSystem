from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from ....database import get_db
from ....models.inventory import (
    InventoryItem, InventoryCategory, InventoryLocation, 
    InventoryTransaction, InventoryAdjustment
)
from ....schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    InventoryCategoryCreate, InventoryCategoryResponse,
    InventoryLocationCreate, InventoryLocationResponse,
    InventoryTransactionCreate, InventoryTransactionResponse,
    InventoryAdjustmentCreate, InventoryAdjustmentResponse
)
from ....core.auth import get_current_user
from ....models.user import User

router = APIRouter()

# Items endpoints
@router.get("/items", response_model=List[InventoryItemResponse])
async def get_inventory_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    category_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(InventoryItem).filter(InventoryItem.company_id == current_user.company_id)
    
    if search:
        query = query.filter(
            (InventoryItem.item_name.ilike(f"%{search}%")) |
            (InventoryItem.item_code.ilike(f"%{search}%"))
        )
    
    if category_id:
        query = query.filter(InventoryItem.category_id == category_id)
    
    if status:
        is_active = status.lower() == "active"
        query = query.filter(InventoryItem.is_active == is_active)
    
    items = query.offset(skip).limit(limit).all()
    return items

@router.post("/items", response_model=InventoryItemResponse)
async def create_inventory_item(
    item: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = InventoryItem(
        id=str(uuid.uuid4()),
        company_id=current_user.company_id,
        **item.dict()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/items/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.company_id == current_user.company_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item

@router.put("/items/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: str,
    item_update: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.company_id == current_user.company_id
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for field, value in item_update.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    
    db_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}")
async def delete_inventory_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.company_id == current_user.company_id
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}

# Categories endpoints
@router.get("/categories", response_model=List[InventoryCategoryResponse])
async def get_inventory_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = db.query(InventoryCategory).filter(
        InventoryCategory.company_id == current_user.company_id,
        InventoryCategory.is_active == True
    ).all()
    return categories

@router.post("/categories", response_model=InventoryCategoryResponse)
async def create_inventory_category(
    category: InventoryCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_category = InventoryCategory(
        id=str(uuid.uuid4()),
        company_id=current_user.company_id,
        **category.dict()
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Locations endpoints
@router.get("/locations", response_model=List[InventoryLocationResponse])
async def get_inventory_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    locations = db.query(InventoryLocation).filter(
        InventoryLocation.company_id == current_user.company_id,
        InventoryLocation.is_active == True
    ).all()
    return locations

@router.post("/locations", response_model=InventoryLocationResponse)
async def create_inventory_location(
    location: InventoryLocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_location = InventoryLocation(
        id=str(uuid.uuid4()),
        company_id=current_user.company_id,
        **location.dict()
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

# Transactions endpoints
@router.get("/transactions", response_model=List[InventoryTransactionResponse])
async def get_inventory_transactions(
    item_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(InventoryTransaction).filter(
        InventoryTransaction.company_id == current_user.company_id
    )
    
    if item_id:
        query = query.filter(InventoryTransaction.item_id == item_id)
    
    transactions = query.order_by(InventoryTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions

@router.post("/transactions", response_model=InventoryTransactionResponse)
async def create_inventory_transaction(
    transaction: InventoryTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_transaction = InventoryTransaction(
        id=str(uuid.uuid4()),
        company_id=current_user.company_id,
        created_by=current_user.id,
        **transaction.dict()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# Adjustments endpoints
@router.get("/adjustments", response_model=List[InventoryAdjustmentResponse])
async def get_inventory_adjustments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    adjustments = db.query(InventoryAdjustment).filter(
        InventoryAdjustment.company_id == current_user.company_id
    ).order_by(InventoryAdjustment.adjustment_date.desc()).offset(skip).limit(limit).all()
    return adjustments

@router.post("/adjustments", response_model=InventoryAdjustmentResponse)
async def create_inventory_adjustment(
    adjustment: InventoryAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_adjustment = InventoryAdjustment(
        id=str(uuid.uuid4()),
        company_id=current_user.company_id,
        created_by=current_user.id,
        **adjustment.dict()
    )
    db.add(db_adjustment)
    db.commit()
    db.refresh(db_adjustment)
    return db_adjustment

# Barcode lookup endpoint
@router.get("/barcode/lookup")
async def lookup_item_by_barcode(
    code: str = Query(..., description="Barcode or SKU to lookup"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(InventoryItem).filter(
        InventoryItem.company_id == current_user.company_id,
        (InventoryItem.item_code == code) | (InventoryItem.barcode == code)
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item