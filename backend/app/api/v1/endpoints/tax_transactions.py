from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.core.tax.tax_transaction_service import tax_transaction_service
from app.schemas.tax import (
    TaxTransactionCreate,
    TaxTransactionUpdate,
    TaxTransactionInDB,
    TaxTransactionComponentCreate,
    TaxTransactionStatus,
    TaxTransactionType
)
from app.core.auth import get_current_user
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", response_model=TaxTransactionInDB, status_code=status.HTTP_201_CREATED)
async def create_tax_transaction(
    transaction_data: TaxTransactionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new tax transaction.
    
    This endpoint creates a new tax transaction with the provided data.
    Required permissions: tax:write
    """
    try:
        return await tax_transaction_service.create_transaction(
            db=db,
            transaction_data=transaction_data,
            current_user_id=current_user.id
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{transaction_id}", response_model=TaxTransactionInDB)
async def get_tax_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve a tax transaction by ID.
    
    This endpoint returns the details of a specific tax transaction.
    Required permissions: tax:read
    """
    try:
        return await tax_transaction_service.get_transaction(db, transaction_id)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/", response_model=List[TaxTransactionInDB])
async def list_tax_transactions(
    company_id: UUID,
    status: Optional[TaxTransactionStatus] = None,
    transaction_type: Optional[TaxTransactionType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List tax transactions with filtering and pagination.
    
    This endpoint returns a paginated list of tax transactions matching the specified filters.
    Required permissions: tax:read
    """
    try:
        return await tax_transaction_service.list_transactions(
            db=db,
            company_id=company_id,
            status=status,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{transaction_id}", response_model=TaxTransactionInDB)
async def update_tax_transaction(
    transaction_id: UUID,
    transaction_data: TaxTransactionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update an existing tax transaction.
    
    This endpoint updates the details of an existing tax transaction.
    Only draft transactions can be modified.
    Required permissions: tax:write
    """
    try:
        return await tax_transaction_service.update_transaction(
            db=db,
            transaction_id=transaction_id,
            update_data=transaction_data,
            current_user_id=current_user.id
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{transaction_id}/post", response_model=TaxTransactionInDB)
async def post_tax_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Post a draft tax transaction.
    
    This endpoint marks a draft transaction as posted, making it final.
    Required permissions: tax:post
    """
    try:
        return await tax_transaction_service.post_transaction(
            db=db,
            transaction_id=transaction_id,
            current_user_id=current_user.id
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{transaction_id}/void", response_model=TaxTransactionInDB)
async def void_tax_transaction(
    transaction_id: UUID,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Void a posted tax transaction.
    
    This endpoint voids a posted transaction and creates a reversal entry.
    Required permissions: tax:void
    """
    try:
        return await tax_transaction_service.void_transaction(
            db=db,
            transaction_id=transaction_id,
            reason=reason,
            current_user_id=current_user.id
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{transaction_id}/components", response_model=List[TaxTransactionComponentInDB])
async def get_transaction_components(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get components of a tax transaction.
    
    This endpoint returns the detailed tax components of a specific transaction.
    Required permissions: tax:read
    """
    try:
        transaction = await tax_transaction_service.get_transaction(db, transaction_id)
        return transaction.components
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
