from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.crud.hrm.policy_crud import policy_crud
from app.schemas.hrm.policy_schemas import PolicyCreate, PolicyUpdate, PolicyResponse

router = APIRouter()


@router.get("/", response_model=List[PolicyResponse])
def get_policies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all HR policies"""
    return policy_crud.get_all(db, skip=skip, limit=limit)


@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(
    policy_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific HR policy"""
    policy = policy_crud.get_by_id(db, policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    return policy


@router.post("/", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy(
    policy_data: PolicyCreate,
    db: Session = Depends(get_db)
):
    """Create a new HR policy"""
    return policy_crud.create(db, policy_data)


@router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: str,
    policy_data: PolicyUpdate,
    db: Session = Depends(get_db)
):
    """Update an HR policy"""
    policy = policy_crud.update(db, policy_id, policy_data)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(
    policy_id: str,
    db: Session = Depends(get_db)
):
    """Delete an HR policy"""
    if not policy_crud.delete(db, policy_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )