from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
from app.core.db import get_db
from .services import (
    TaxJurisdictionService, TaxRateService, TaxTransactionService,
    TaxExemptionService, TaxReturnService
)
from .schemas import (
    TaxJurisdiction, TaxJurisdictionCreate,
    TaxRate, TaxRateCreate,
    TaxTransaction, TaxTransactionCreate,
    TaxExemption, TaxExemptionCreate,
    TaxReturn, TaxReturnCreate
)

router = APIRouter()

# Initialize services
jurisdiction_service = TaxJurisdictionService()
rate_service = TaxRateService()
transaction_service = TaxTransactionService()
exemption_service = TaxExemptionService()
return_service = TaxReturnService()

# Tax Jurisdiction endpoints
@router.post("/jurisdictions/", response_model=TaxJurisdiction, status_code=status.HTTP_201_CREATED)
async def create_jurisdiction(
    jurisdiction: TaxJurisdictionCreate,
    db: AsyncSession = Depends(get_db)
):
    existing = await jurisdiction_service.get_by_code(db, jurisdiction.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Jurisdiction code already exists"
        )
    return await jurisdiction_service.create(db, obj_in=jurisdiction)

@router.get("/jurisdictions/", response_model=List[TaxJurisdiction])
async def get_jurisdictions(
    level: str = None,
    db: AsyncSession = Depends(get_db)
):
    if level:
        return await jurisdiction_service.get_by_level(db, level)
    return await jurisdiction_service.get_multi(db)

@router.get("/jurisdictions/{jurisdiction_id}", response_model=TaxJurisdiction)
async def get_jurisdiction(
    jurisdiction_id: int,
    db: AsyncSession = Depends(get_db)
):
    jurisdiction = await jurisdiction_service.get(db, jurisdiction_id)
    if not jurisdiction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jurisdiction not found"
        )
    return jurisdiction

# Tax Rate endpoints
@router.post("/rates/", response_model=TaxRate, status_code=status.HTTP_201_CREATED)
async def create_tax_rate(
    rate: TaxRateCreate,
    db: AsyncSession = Depends(get_db)
):
    return await rate_service.create(db, obj_in=rate)

@router.get("/rates/", response_model=List[TaxRate])
async def get_tax_rates(
    tax_type: str = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    if active_only:
        return await rate_service.get_active_rates(db, tax_type)
    return await rate_service.get_multi(db)

@router.get("/rates/jurisdiction/{jurisdiction_id}", response_model=TaxRate)
async def get_rate_for_jurisdiction(
    jurisdiction_id: int,
    tax_type: str,
    effective_date: date = None,
    db: AsyncSession = Depends(get_db)
):
    rate = await rate_service.get_rate_for_jurisdiction(
        db, jurisdiction_id, tax_type, effective_date
    )
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax rate not found for jurisdiction"
        )
    return rate

# Tax Transaction endpoints
@router.post("/transactions/", response_model=TaxTransaction, status_code=status.HTTP_201_CREATED)
async def create_tax_transaction(
    transaction: TaxTransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    return await transaction_service.create_transaction(db, transaction)

@router.get("/transactions/", response_model=List[TaxTransaction])
async def get_tax_transactions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await transaction_service.get_multi(db, skip=skip, limit=limit)

@router.get("/transactions/{transaction_id}", response_model=TaxTransaction)
async def get_tax_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
):
    transaction = await transaction_service.get(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax transaction not found"
        )
    return transaction

@router.post("/transactions/calculate")
async def calculate_tax(
    taxable_amount: float,
    tax_rate_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        tax_amount = await transaction_service.calculate_tax(
            db, taxable_amount, tax_rate_id
        )
        return {
            "taxable_amount": taxable_amount,
            "tax_amount": float(tax_amount),
            "total_amount": taxable_amount + float(tax_amount)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Tax Exemption endpoints
@router.post("/exemptions/", response_model=TaxExemption, status_code=status.HTTP_201_CREATED)
async def create_tax_exemption(
    exemption: TaxExemptionCreate,
    db: AsyncSession = Depends(get_db)
):
    return await exemption_service.create(db, obj_in=exemption)

@router.get("/exemptions/", response_model=List[TaxExemption])
async def get_tax_exemptions(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    if active_only:
        return await exemption_service.get_active_exemptions(db)
    return await exemption_service.get_multi(db)

# Tax Return endpoints
@router.post("/returns/", response_model=TaxReturn, status_code=status.HTTP_201_CREATED)
async def create_tax_return(
    tax_return: TaxReturnCreate,
    db: AsyncSession = Depends(get_db)
):
    # Generate return number if not provided
    if not tax_return.return_number:
        period_year = tax_return.period_start.year
        tax_return.return_number = await return_service.generate_return_number(
            db, tax_return.tax_type, period_year
        )
    
    return await return_service.create(db, obj_in=tax_return)

@router.get("/returns/", response_model=List[TaxReturn])
async def get_tax_returns(
    start_date: date = None,
    end_date: date = None,
    db: AsyncSession = Depends(get_db)
):
    if start_date and end_date:
        return await return_service.get_returns_by_period(db, start_date, end_date)
    return await return_service.get_multi(db)

@router.get("/returns/{return_id}", response_model=TaxReturn)
async def get_tax_return(
    return_id: int,
    db: AsyncSession = Depends(get_db)
):
    tax_return = await return_service.get(db, return_id)
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found"
        )
    return tax_return