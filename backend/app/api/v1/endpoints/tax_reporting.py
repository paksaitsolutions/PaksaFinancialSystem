from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.tax.tax_calculation_service import tax_calculation_service
from app.core.tax.tax_policy_service import tax_policy_service
from app.core.auth import get_current_user
from app.db.session import get_db
from app.schemas.tax import TaxPolicy, TaxRate, TaxExemption, TaxCalculationRequest, TaxCalculationResponse

router = APIRouter()

@router.get("/policy/current", response_model=TaxPolicy)
async def get_current_tax_policy(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the current active tax policy."""
    try:
        policy = await tax_policy_service.get_current_policy(db)
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active tax policy found"
            )
        return policy
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/policy", response_model=TaxPolicy)
async def update_tax_policy(
    policy_data: TaxPolicy,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update the current tax policy."""
    try:
        updated_policy = await tax_policy_service.update_policy(db, policy_data)
        return updated_policy
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/rates", response_model=TaxRate)
async def add_tax_rate(
    rate_data: TaxRate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a new tax rate."""
    try:
        new_rate = await tax_policy_service.add_tax_rate(db, rate_data)
        return new_rate
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/rates/{rate_id}", response_model=TaxRate)
async def update_tax_rate(
    rate_id: str,
    rate_data: TaxRate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing tax rate."""
    try:
        updated_rate = await tax_policy_service.update_tax_rate(db, rate_id, rate_data)
        return updated_rate
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/rates/{rate_id}")
async def delete_tax_rate(
    rate_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a tax rate."""
    try:
        await tax_policy_service.delete_tax_rate(db, rate_id)
        return {"message": "Tax rate deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/exemptions", response_model=TaxExemption)
async def add_tax_exemption(
    exemption_data: TaxExemption,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a new tax exemption."""
    try:
        new_exemption = await tax_policy_service.add_tax_exemption(db, exemption_data)
        return new_exemption
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/exemptions/{exemption_id}", response_model=TaxExemption)
async def update_tax_exemption(
    exemption_id: str,
    exemption_data: TaxExemption,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing tax exemption."""
    try:
        updated_exemption = await tax_policy_service.update_tax_exemption(db, exemption_id, exemption_data)
        return updated_exemption
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/exemptions/{exemption_id}")
async def delete_tax_exemption(
    exemption_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a tax exemption."""
    try:
        await tax_policy_service.delete_tax_exemption(db, exemption_id)
        return {"message": "Tax exemption deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/calculate", response_model=TaxCalculationResponse)
async def calculate_taxes(
    request: TaxCalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate taxes for a given transaction."""
    try:
        result = await tax_calculation_service.calculate_taxes(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
