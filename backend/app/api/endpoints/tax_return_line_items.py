from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.deps import get_current_active_user, get_db

router = APIRouter()


@router.get("/", response_model=schemas.TaxReturnLineItemListResponse)
def list_tax_return_line_items(
    db: Session = Depends(get_db),
    tax_return_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve tax return line items.
    """
    if not tax_return_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tax_return_id is required",
        )
        
    # Check if the user has access to this tax return
    tax_return = crud.tax_return.get(db=db, id=tax_return_id)
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )
        
    if tax_return.company_id != current_user.company_id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get line items
    line_items = crud.tax_return_line_item.get_by_tax_return(
        db=db, 
        tax_return_id=tax_return_id,
        skip=skip, 
        limit=limit
    )
    
    # Get total count for pagination
    total = crud.tax_return_line_item.count_by_tax_return(
        db=db, 
        tax_return_id=tax_return_id
    )
    
    return {
        "data": line_items,
        "total": total,
        "page": (skip // limit) + 1,
        "limit": limit,
    }


@router.post(
    "/", 
    response_model=schemas.TaxReturnLineItemResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_tax_return_line_item(
    *,
    db: Session = Depends(get_db),
    line_item_in: schemas.TaxReturnLineItemCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new tax return line item.
    """
    # Check if the user has access to this tax return
    tax_return = crud.tax_return.get(db=db, id=line_item_in.tax_return_id)
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )
        
    if tax_return.company_id != current_user.company_id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to add line items to this tax return",
        )
    
    # Create the line item
    line_item = crud.tax_return_line_item.create_with_tax_return(
        db=db, 
        obj_in=line_item_in,
        tax_return_id=line_item_in.tax_return_id
    )
    
    return {"success": True, "data": line_item}


@router.get("/{line_item_id}", response_model=schemas.TaxReturnLineItemResponse)
def get_tax_return_line_item(
    *,
    db: Session = Depends(get_db),
    line_item_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific tax return line item by ID.
    """
    line_item = crud.tax_return_line_item.get(db=db, id=line_item_id)
    if not line_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return line item not found",
        )
        
    # Get the associated tax return to check permissions
    tax_return = crud.tax_return.get(db=db, id=line_item.tax_return_id)
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated tax return not found",
        )
        
    if tax_return.company_id != current_user.company_id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this line item",
        )
    
    return {"success": True, "data": line_item}


@router.put("/{line_item_id}", response_model=schemas.TaxReturnLineItemResponse)
def update_tax_return_line_item(
    *,
    db: Session = Depends(get_db),
    line_item_id: UUID,
    line_item_in: schemas.TaxReturnLineItemUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a tax return line item.
    """
    line_item = crud.tax_return_line_item.get(db=db, id=line_item_id)
    if not line_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return line item not found",
        )
        
    # Get the associated tax return to check permissions
    tax_return = crud.tax_return.get(db=db, id=line_item.tax_return_id)
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated tax return not found",
        )
        
    if tax_return.company_id != current_user.company_id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this line item",
        )
        
    # Prevent changing the tax return ID
    if line_item_in.tax_return_id and line_item_in.tax_return_id != line_item.tax_return_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change the tax return ID of a line item",
        )
    
    # Update the line item
    line_item = crud.tax_return_line_item.update(
        db=db, 
        db_obj=line_item, 
        obj_in=line_item_in
    )
    
    return {"success": True, "data": line_item}


@router.delete("/{line_item_id}", response_model=schemas.GenericResponse)
def delete_tax_return_line_item(
    *,
    db: Session = Depends(get_db),
    line_item_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a tax return line item.
    """
    line_item = crud.tax_return_line_item.get(db=db, id=line_item_id)
    if not line_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return line item not found",
        )
        
    # Get the associated tax return to check permissions
    tax_return = crud.tax_return.get(db=db, id=line_item.tax_return_id)
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated tax return not found",
        )
        
    if tax_return.company_id != current_user.company_id and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this line item",
        )
    
    # Delete the line item
    crud.tax_return_line_item.remove(db=db, id=line_item_id)
    
    return {"success": True, "message": "Tax return line item deleted successfully"}
