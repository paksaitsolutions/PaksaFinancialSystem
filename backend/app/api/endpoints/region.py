"""
Region and Country API endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.region_schemas import (
    RegionCreate, RegionUpdate, RegionResponse,
    CountryCreate, CountryUpdate, CountryResponse
)
from app.crud.region_crud import RegionCRUD, CountryCRUD

router = APIRouter()


# Region endpoints
@router.get(
    "/regions",
    response_model=List[RegionResponse],
    summary="List all regions",
    description="Get a list of all regions in the system.",
    tags=["Regions"]
)
async def list_regions(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[RegionResponse]:
    """Get a list of all regions."""
    crud = RegionCRUD(db)
    return crud.get_all_regions(include_inactive)


@router.get(
    "/regions/{region_id}",
    response_model=RegionResponse,
    summary="Get region by ID",
    description="Get detailed information about a specific region.",
    tags=["Regions"]
)
async def get_region(
    region_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> RegionResponse:
    """Get a region by its ID."""
    crud = RegionCRUD(db)
    region = crud.get_region_by_id(region_id)
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with ID {region_id} not found"
        )
    
    return region


@router.post(
    "/regions",
    response_model=RegionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new region",
    description="Create a new region in the system.",
    tags=["Regions"]
)
async def create_region(
    region: RegionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> RegionResponse:
    """Create a new region."""
    crud = RegionCRUD(db)
    
    # Check if region code already exists
    existing = crud.get_region_by_code(region.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Region with code {region.code} already exists"
        )
    
    return crud.create_region(region.dict())


@router.put(
    "/regions/{region_id}",
    response_model=RegionResponse,
    summary="Update a region",
    description="Update an existing region.",
    tags=["Regions"]
)
async def update_region(
    region_id: UUID,
    region: RegionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> RegionResponse:
    """Update an existing region."""
    crud = RegionCRUD(db)
    
    updated_region = crud.update_region(region_id, region.dict(exclude_unset=True))
    if not updated_region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with ID {region_id} not found"
        )
    
    return updated_region


@router.delete(
    "/regions/{region_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a region",
    description="Delete a region from the system.",
    tags=["Regions"]
)
async def delete_region(
    region_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> None:
    """Delete a region."""
    crud = RegionCRUD(db)
    
    if not crud.delete_region(region_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with ID {region_id} not found"
        )


# Country endpoints
@router.get(
    "/countries",
    response_model=List[CountryResponse],
    summary="List all countries",
    description="Get a list of all countries in the system.",
    tags=["Countries"]
)
async def list_countries(
    include_inactive: bool = False,
    region_id: UUID = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[CountryResponse]:
    """Get a list of all countries."""
    crud = CountryCRUD(db)
    
    if region_id:
        return crud.get_countries_by_region(region_id, include_inactive)
    
    return crud.get_all_countries(include_inactive)


@router.get(
    "/countries/{country_id}",
    response_model=CountryResponse,
    summary="Get country by ID",
    description="Get detailed information about a specific country.",
    tags=["Countries"]
)
async def get_country(
    country_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CountryResponse:
    """Get a country by its ID."""
    crud = CountryCRUD(db)
    country = crud.get_country_by_id(country_id)
    
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with ID {country_id} not found"
        )
    
    return country


@router.post(
    "/countries",
    response_model=CountryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new country",
    description="Create a new country in the system.",
    tags=["Countries"]
)
async def create_country(
    country: CountryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CountryResponse:
    """Create a new country."""
    crud = CountryCRUD(db)
    
    # Check if country code already exists
    existing = crud.get_country_by_code(country.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Country with code {country.code} already exists"
        )
    
    return crud.create_country(country.dict())


@router.put(
    "/countries/{country_id}",
    response_model=CountryResponse,
    summary="Update a country",
    description="Update an existing country.",
    tags=["Countries"]
)
async def update_country(
    country_id: UUID,
    country: CountryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CountryResponse:
    """Update an existing country."""
    crud = CountryCRUD(db)
    
    updated_country = crud.update_country(country_id, country.dict(exclude_unset=True))
    if not updated_country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with ID {country_id} not found"
        )
    
    return updated_country


@router.delete(
    "/countries/{country_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a country",
    description="Delete a country from the system.",
    tags=["Countries"]
)
async def delete_country(
    country_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> None:
    """Delete a country."""
    crud = CountryCRUD(db)
    
    if not crud.delete_country(country_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with ID {country_id} not found"
        )