"""
API endpoints for tax management.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.core.permissions import require_permission, Permission
from app.crud.tax.tax_crud import tax_crud
from app.crud.tax.tax_reports import tax_reports_crud
from app.schemas.tax.tax_schemas import (
    TaxRateCreate, TaxRateUpdate, TaxRateResponse,
    TaxExemptionCreate, TaxExemptionUpdate, TaxExemptionResponse,
    TaxPolicyCreate, TaxPolicyUpdate, TaxPolicyResponse,
    TaxCalculationRequest, TaxCalculationResponse
)

router = APIRouter()

# Tax Rate endpoints
@router.post("/rates", response_model=TaxRateResponse, status_code=status.HTTP_201_CREATED)
async def create_tax_rate(
    *,
    db: AsyncSession = Depends(get_db),
    tax_rate_in: TaxRateCreate,
    _: bool = Depends(require_permission(Permission.TAX_WRITE)),
) -> Any:
    """Create a new tax rate."""
    tax_rate = await tax_crud.create_tax_rate(db, obj_in=tax_rate_in)
    return success_response(
        data=tax_rate,
        message="Tax rate created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/rates", response_model=List[TaxRateResponse])
async def get_tax_rates(
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tax_type: Optional[str] = Query(None),
    jurisdiction: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
) -> Any:
    """Get tax rates with filtering."""
    filters = {}
    if tax_type:
        filters["tax_type"] = tax_type
    if jurisdiction:
        filters["jurisdiction"] = jurisdiction
    if is_active is not None:
        filters["is_active"] = is_active
    
    tax_rates = await tax_crud.get_tax_rates(db, skip=skip, limit=limit, filters=filters)
    return success_response(data=tax_rates)

@router.get("/rates/{tax_rate_id}", response_model=TaxRateResponse)
async def get_tax_rate(
    *,
    db: AsyncSession = Depends(get_db),
    tax_rate_id: UUID,
) -> Any:
    """Get a specific tax rate."""
    tax_rate = await tax_crud.get_tax_rate(db, id=tax_rate_id)
    if not tax_rate:
        return error_response(
            message="Tax rate not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return success_response(data=tax_rate)

@router.put("/rates/{tax_rate_id}", response_model=TaxRateResponse)
async def update_tax_rate(
    *,
    db: AsyncSession = Depends(get_db),
    tax_rate_id: UUID,
    tax_rate_in: TaxRateUpdate,
) -> Any:
    """Update a tax rate."""
    tax_rate = await tax_crud.get_tax_rate(db, id=tax_rate_id)
    if not tax_rate:
        return error_response(
            message="Tax rate not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    tax_rate = await tax_crud.update_tax_rate(db, db_obj=tax_rate, obj_in=tax_rate_in)
    return success_response(
        data=tax_rate,
        message="Tax rate updated successfully",
    )

# Tax Exemption endpoints
@router.post("/exemptions", response_model=TaxExemptionResponse, status_code=status.HTTP_201_CREATED)
async def create_tax_exemption(
    *,
    db: AsyncSession = Depends(get_db),
    exemption_in: TaxExemptionCreate,
) -> Any:
    """Create a new tax exemption."""
    exemption = await tax_crud.create_tax_exemption(db, obj_in=exemption_in)
    return success_response(
        data=exemption,
        message="Tax exemption created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/exemptions", response_model=List[TaxExemptionResponse])
async def get_tax_exemptions(
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_type: Optional[str] = Query(None),
    tax_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
) -> Any:
    """Get tax exemptions with filtering."""
    filters = {}
    if entity_type:
        filters["entity_type"] = entity_type
    if tax_type:
        filters["tax_type"] = tax_type
    if is_active is not None:
        filters["is_active"] = is_active
    
    exemptions = await tax_crud.get_tax_exemptions(db, skip=skip, limit=limit, filters=filters)
    return success_response(data=exemptions)

# Tax Policy endpoints
@router.post("/policies", response_model=TaxPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_tax_policy(
    *,
    db: AsyncSession = Depends(get_db),
    policy_in: TaxPolicyCreate,
) -> Any:
    """Create a new tax policy."""
    policy = await tax_crud.create_tax_policy(db, obj_in=policy_in)
    return success_response(
        data=policy,
        message="Tax policy created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/policies", response_model=List[TaxPolicyResponse])
async def get_tax_policies(
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    policy_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
) -> Any:
    """Get tax policies with filtering."""
    filters = {}
    if policy_type:
        filters["policy_type"] = policy_type
    if is_active is not None:
        filters["is_active"] = is_active
    
    policies = await tax_crud.get_tax_policies(db, skip=skip, limit=limit, filters=filters)
    return success_response(data=policies)

# Tax Calculation endpoint
@router.post("/calculate", response_model=TaxCalculationResponse)
async def calculate_tax(
    *,
    db: AsyncSession = Depends(get_db),
    calculation_request: TaxCalculationRequest,
) -> Any:
    """Calculate tax for a given amount and conditions."""
    result = await tax_crud.calculate_tax(db, request=calculation_request)
    return success_response(data=result)

# Tax Reports endpoints
@router.get("/reports/summary")
async def get_tax_summary_report(
    *,
    db: AsyncSession = Depends(get_db),
    from_date: date = Query(...),
    to_date: date = Query(...),
    tax_type: Optional[str] = Query(None),
) -> Any:
    """Get tax summary report."""
    report = await tax_reports_crud.get_tax_summary_report(
        db, from_date=from_date, to_date=to_date, tax_type=tax_type
    )
    return success_response(data=report)

@router.get("/reports/exemptions")
async def get_exemption_report(
    *,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get tax exemption report."""
    report = await tax_reports_crud.get_exemption_report(db)
    return success_response(data=report)