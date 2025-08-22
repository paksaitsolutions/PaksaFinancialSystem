<<<<<<< HEAD
"""
Reconciliation Router

This module provides the API endpoints for account reconciliation functionality.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from .. import schemas, services
from ..models import ReconciliationStatus, ReconciliationMatchType
from ..services import reconciliation_service
from ...auth.dependencies import get_current_user
from ...users.models import User

router = APIRouter(prefix="/reconciliations", tags=["reconciliations"])


@router.post("/", response_model=schemas.Reconciliation, status_code=status.HTTP_201_CREATED)
def create_reconciliation(
    reconciliation: schemas.ReconciliationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new reconciliation.
    """
    return reconciliation_service.create_reconciliation(db, reconciliation, current_user.id)


@router.get("/", response_model=List[schemas.Reconciliation])
def list_reconciliations(
    status: Optional[ReconciliationStatus] = None,
    account_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve reconciliations with optional filtering.
    """
    return reconciliation_service.get_reconciliations(
        db=db,
        status=status,
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
        user_id=current_user.id
    )


@router.get("/{reconciliation_id}", response_model=schemas.ReconciliationDetail)
def get_reconciliation(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific reconciliation by ID.
    """
    reconciliation = reconciliation_service.get_reconciliation(db, reconciliation_id, current_user.id)
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return reconciliation


@router.put("/{reconciliation_id}", response_model=schemas.Reconciliation)
def update_reconciliation(
    reconciliation_id: UUID,
    reconciliation_update: schemas.ReconciliationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a reconciliation.
    """
    reconciliation = reconciliation_service.update_reconciliation(
        db, reconciliation_id, reconciliation_update, current_user.id
    )
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return reconciliation


@router.delete("/{reconciliation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reconciliation(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a reconciliation.
    """
    if not reconciliation_service.delete_reconciliation(db, reconciliation_id, current_user.id):
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return None


@router.post("/{reconciliation_id}/items/", response_model=schemas.ReconciliationItem)
def add_reconciliation_item(
    reconciliation_id: UUID,
    item: schemas.ReconciliationItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add an item to a reconciliation.
    """
    return reconciliation_service.add_reconciliation_item(
        db, reconciliation_id, item, current_user.id
    )


@router.put("/items/{item_id}", response_model=schemas.ReconciliationItem)
def update_reconciliation_item(
    item_id: UUID,
    item_update: schemas.ReconciliationItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a reconciliation item.
    """
    item = reconciliation_service.update_reconciliation_item(
        db, item_id, item_update, current_user.id
    )
    if not item:
        raise HTTPException(status_code=404, detail="Reconciliation item not found")
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reconciliation_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a reconciliation item.
    """
    if not reconciliation_service.delete_reconciliation_item(db, item_id, current_user.id):
        raise HTTPException(status_code=404, detail="Reconciliation item not found")
    return None


@router.post("/{reconciliation_id}/complete/", response_model=schemas.Reconciliation)
def complete_reconciliation(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a reconciliation as completed.
    """
    reconciliation = reconciliation_service.complete_reconciliation(
        db, reconciliation_id, current_user.id
    )
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found or cannot be completed")
    return reconciliation


@router.get("/{reconciliation_id}/unreconciled/", response_model=List[schemas.UnreconciledTransaction])
def get_unreconciled_transactions(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get unreconciled transactions for a reconciliation.
    """
    reconciliation = reconciliation_service.get_reconciliation(
        db, reconciliation_id, current_user.id
    )
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    
    return reconciliation_service.get_unreconciled_transactions(
        db, reconciliation.account_id, reconciliation.start_date, reconciliation.end_date
    )


@router.get("/{reconciliation_id}/audit-logs/", response_model=List[schemas.ReconciliationAuditLog])
def get_audit_logs(
    reconciliation_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs for a reconciliation.
    """
    return reconciliation_service.get_audit_logs(
        db, reconciliation_id, current_user.id, skip, limit
    )
=======
"""
Reconciliation Router

This module provides the API endpoints for account reconciliation functionality.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from .. import schemas, services
from ..models import ReconciliationStatus, ReconciliationMatchType
from ..services import reconciliation_service
from ...auth.dependencies import get_current_user
from ...users.models import User

router = APIRouter(prefix="/reconciliations", tags=["reconciliations"])


@router.post("/", response_model=schemas.Reconciliation, status_code=status.HTTP_201_CREATED)
def create_reconciliation(
    reconciliation: schemas.ReconciliationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new reconciliation.
    """
    return reconciliation_service.create_reconciliation(db, reconciliation, current_user.id)


@router.get("/", response_model=List[schemas.Reconciliation])
def list_reconciliations(
    status: Optional[ReconciliationStatus] = None,
    account_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve reconciliations with optional filtering.
    """
    return reconciliation_service.get_reconciliations(
        db=db,
        status=status,
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
        user_id=current_user.id
    )


@router.get("/{reconciliation_id}", response_model=schemas.ReconciliationDetail)
def get_reconciliation(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific reconciliation by ID.
    """
    reconciliation = reconciliation_service.get_reconciliation(db, reconciliation_id, current_user.id)
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return reconciliation


@router.put("/{reconciliation_id}", response_model=schemas.Reconciliation)
def update_reconciliation(
    reconciliation_id: UUID,
    reconciliation_update: schemas.ReconciliationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a reconciliation.
    """
    reconciliation = reconciliation_service.update_reconciliation(
        db, reconciliation_id, reconciliation_update, current_user.id
    )
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return reconciliation


@router.delete("/{reconciliation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reconciliation(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a reconciliation.
    """
    if not reconciliation_service.delete_reconciliation(db, reconciliation_id, current_user.id):
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return None


@router.post("/{reconciliation_id}/items/", response_model=schemas.ReconciliationItem)
def add_reconciliation_item(
    reconciliation_id: UUID,
    item: schemas.ReconciliationItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add an item to a reconciliation.
    """
    return reconciliation_service.add_reconciliation_item(
        db, reconciliation_id, item, current_user.id
    )


@router.put("/items/{item_id}", response_model=schemas.ReconciliationItem)
def update_reconciliation_item(
    item_id: UUID,
    item_update: schemas.ReconciliationItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a reconciliation item.
    """
    item = reconciliation_service.update_reconciliation_item(
        db, item_id, item_update, current_user.id
    )
    if not item:
        raise HTTPException(status_code=404, detail="Reconciliation item not found")
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reconciliation_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a reconciliation item.
    """
    if not reconciliation_service.delete_reconciliation_item(db, item_id, current_user.id):
        raise HTTPException(status_code=404, detail="Reconciliation item not found")
    return None


@router.post("/{reconciliation_id}/complete/", response_model=schemas.Reconciliation)
def complete_reconciliation(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a reconciliation as completed.
    """
    reconciliation = reconciliation_service.complete_reconciliation(
        db, reconciliation_id, current_user.id
    )
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found or cannot be completed")
    return reconciliation


@router.get("/{reconciliation_id}/unreconciled/", response_model=List[schemas.UnreconciledTransaction])
def get_unreconciled_transactions(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get unreconciled transactions for a reconciliation.
    """
    reconciliation = reconciliation_service.get_reconciliation(
        db, reconciliation_id, current_user.id
    )
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    
    return reconciliation_service.get_unreconciled_transactions(
        db, reconciliation.account_id, reconciliation.start_date, reconciliation.end_date
    )


@router.get("/{reconciliation_id}/audit-logs/", response_model=List[schemas.ReconciliationAuditLog])
def get_audit_logs(
    reconciliation_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs for a reconciliation.
    """
    return reconciliation_service.get_audit_logs(
        db, reconciliation_id, current_user.id, skip, limit
    )
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
