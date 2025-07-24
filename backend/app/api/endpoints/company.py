"""
Company management API endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.company_schemas import (
    CompanyRegistrationRequest,
    CompanyResponse,
    CompanyUpdateRequest,
    CompanyUserRequest,
    CompanyUserResponse,
    CompanySettingsRequest,
    CompanySettingsResponse
)
from app.services.company.company_service import CompanyService

router = APIRouter()


def get_company_service(db: Session = Depends(get_db)) -> CompanyService:
    """Get an instance of the company service."""
    return CompanyService(db)


@router.post(
    "/register",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register company",
    description="Register a new company with basic information.",
    tags=["Company Registration"]
)
async def register_company(
    company_request: CompanyRegistrationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompanyResponse:
    """Register a new company."""
    service = get_company_service(db)
    
    try:
        company = service.register_company(company_request.dict(), current_user.id)
        return company
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Get company",
    description="Get company information by ID.",
    tags=["Company Management"]
)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompanyResponse:
    """Get company information."""
    service = get_company_service(db)
    
    company = service.get_company(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Update company",
    description="Update company information.",
    tags=["Company Management"]
)
async def update_company(
    company_id: UUID,
    company_request: CompanyUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompanyResponse:
    """Update company information."""
    service = get_company_service(db)
    
    try:
        company = service.update_company(
            company_id, 
            company_request.dict(exclude_unset=True), 
            current_user.id
        )
        return company
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=List[CompanyResponse],
    summary="List companies",
    description="List companies with optional status filter.",
    tags=["Company Management"]
)
async def list_companies(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[CompanyResponse]:
    """List companies."""
    service = get_company_service(db)
    
    companies = service.list_companies(status=status, limit=limit)
    return companies


@router.post(
    "/{company_id}/users",
    response_model=CompanyUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add user to company",
    description="Add a user to a company.",
    tags=["Company Users"]
)
async def add_user_to_company(
    company_id: UUID,
    user_request: CompanyUserRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompanyUserResponse:
    """Add a user to a company."""
    service = get_company_service(db)
    
    try:
        company_user = service.add_user_to_company(
            company_id=company_id,
            user_id=user_request.user_id,
            role=user_request.role,
            is_admin=user_request.is_admin,
            permissions=user_request.permissions
        )
        return company_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{company_id}/users",
    response_model=List[CompanyUserResponse],
    summary="Get company users",
    description="Get users associated with a company.",
    tags=["Company Users"]
)
async def get_company_users(
    company_id: UUID,
    active_only: bool = Query(True, description="Show only active users"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[CompanyUserResponse]:
    """Get users associated with a company."""
    service = get_company_service(db)
    
    users = service.get_company_users(company_id, active_only=active_only)
    return users


@router.get(
    "/user/{user_id}/companies",
    response_model=List[CompanyResponse],
    summary="Get user companies",
    description="Get companies associated with a user.",
    tags=["Company Users"]
)
async def get_user_companies(
    user_id: UUID,
    active_only: bool = Query(True, description="Show only active companies"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[CompanyResponse]:
    """Get companies associated with a user."""
    service = get_company_service(db)
    
    companies = service.get_user_companies(user_id, active_only=active_only)
    return companies


@router.put(
    "/{company_id}/settings",
    response_model=CompanySettingsResponse,
    summary="Update company settings",
    description="Update company settings and configurations.",
    tags=["Company Settings"]
)
async def update_company_settings(
    company_id: UUID,
    settings_request: CompanySettingsRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompanySettingsResponse:
    """Update company settings."""
    service = get_company_service(db)
    
    try:
        settings = service.update_company_settings(
            company_id,
            settings_request.dict(exclude_unset=True),
            current_user.id
        )
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{company_id}/settings",
    response_model=CompanySettingsResponse,
    summary="Get company settings",
    description="Get company settings and configurations.",
    tags=["Company Settings"]
)
async def get_company_settings(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompanySettingsResponse:
    """Get company settings."""
    service = get_company_service(db)
    
    settings = service.get_company_settings(company_id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company settings not found"
        )
    
    return settings