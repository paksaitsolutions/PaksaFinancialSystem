from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.crud.accounts_receivable.collection_crud import collection_crud, collection_activity_crud
from app.schemas.accounts_receivable.collection_schemas import (
    CollectionCreate, CollectionUpdate, CollectionResponse,
    CollectionActivityCreate, CollectionActivityResponse
)

router = APIRouter()


@router.get("/", response_model=List[CollectionResponse])
def get_collections(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    priority: str = None,
    db: Session = Depends(get_db)
):
    """Get all collections with optional filtering"""
    if status:
        return collection_crud.get_by_status(db, status)
    elif priority:
        return collection_crud.get_by_priority(db, priority)
    else:
        return collection_crud.get_all(db, skip=skip, limit=limit)


@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(
    collection_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific collection"""
    collection = collection_crud.get_by_id(db, collection_id)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    return collection


@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db)
):
    """Create a new collection"""
    return collection_crud.create(db, collection_data)


@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: str,
    collection_data: CollectionUpdate,
    db: Session = Depends(get_db)
):
    """Update a collection"""
    collection = collection_crud.update(db, collection_id, collection_data)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    return collection


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: str,
    db: Session = Depends(get_db)
):
    """Delete a collection"""
    if not collection_crud.delete(db, collection_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )


@router.get("/{collection_id}/activities", response_model=List[CollectionActivityResponse])
def get_collection_activities(
    collection_id: str,
    db: Session = Depends(get_db)
):
    """Get activities for a collection"""
    return collection_activity_crud.get_by_collection(db, collection_id)


@router.post("/{collection_id}/activities", response_model=CollectionActivityResponse, status_code=status.HTTP_201_CREATED)
def create_collection_activity(
    collection_id: str,
    activity_data: CollectionActivityCreate,
    db: Session = Depends(get_db)
):
    """Create a new collection activity"""
    # Ensure the collection_id matches
    activity_data.collection_id = collection_id
    return collection_activity_crud.create(db, activity_data)