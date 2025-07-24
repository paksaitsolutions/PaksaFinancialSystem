"""
Currency API endpoints.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.currency_schemas import (
    CurrencyCreate, CurrencyUpdate, CurrencyResponse,
    ExchangeRateCreate, ExchangeRateUpdate, ExchangeRateResponse,
    ConversionRequest, ConversionResponse
)
from app.services.currency.currency_service import CurrencyService

router = APIRouter()


def get_currency_service(db: Session = Depends(get_db)) -> CurrencyService:
    """Get an instance of the currency service."""
    return CurrencyService(db)


@router.get(
    "/",
    response_model=List[CurrencyResponse],
    summary="List all currencies",
    description="Get a list of all currencies in the system.",
    tags=["Currencies"]
)
async def list_currencies(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[CurrencyResponse]:
    """
    Get a list of all currencies.
    """
    service = get_currency_service(db)
    return service.get_all_currencies(include_inactive)


@router.get(
    "/{currency_id}",
    response_model=CurrencyResponse,
    summary="Get currency by ID",
    description="Get detailed information about a specific currency.",
    tags=["Currencies"]
)
async def get_currency(
    currency_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CurrencyResponse:
    """
    Get a currency by its ID.
    """
    service = get_currency_service(db)
    currency = service.get_currency_by_id(currency_id)
    
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency with ID {currency_id} not found"
        )
    
    return currency


@router.get(
    "/code/{code}",
    response_model=CurrencyResponse,
    summary="Get currency by code",
    description="Get detailed information about a currency by its code.",
    tags=["Currencies"]
)
async def get_currency_by_code(
    code: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CurrencyResponse:
    """
    Get a currency by its code.
    """
    service = get_currency_service(db)
    currency = service.get_currency_by_code(code)
    
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency with code {code} not found"
        )
    
    return currency


@router.get(
    "/base",
    response_model=CurrencyResponse,
    summary="Get base currency",
    description="Get the system's base currency.",
    tags=["Currencies"]
)
async def get_base_currency(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CurrencyResponse:
    """
    Get the system's base currency.
    """
    service = get_currency_service(db)
    currency = service.get_base_currency()
    
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No base currency set"
        )
    
    return currency


@router.post(
    "/",
    response_model=CurrencyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new currency",
    description="Create a new currency in the system.",
    tags=["Currencies"]
)
async def create_currency(
    currency: CurrencyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CurrencyResponse:
    """
    Create a new currency.
    """
    service = get_currency_service(db)
    
    try:
        return service.create_currency(currency.dict(), current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{currency_id}",
    response_model=CurrencyResponse,
    summary="Update a currency",
    description="Update an existing currency.",
    tags=["Currencies"]
)
async def update_currency(
    currency_id: UUID,
    currency: CurrencyUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CurrencyResponse:
    """
    Update an existing currency.
    """
    service = get_currency_service(db)
    
    try:
        return service.update_currency(currency_id, currency.dict(exclude_unset=True), current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{currency_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a currency",
    description="Delete a currency from the system.",
    tags=["Currencies"]
)
async def delete_currency(
    currency_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> None:
    """
    Delete a currency.
    """
    service = get_currency_service(db)
    
    try:
        result = service.delete_currency(currency_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency with ID {currency_id} not found"
            )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/exchange-rates",
    response_model=ExchangeRateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new exchange rate",
    description="Create a new exchange rate between two currencies.",
    tags=["Exchange Rates"]
)
async def create_exchange_rate(
    rate: ExchangeRateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ExchangeRateResponse:
    """
    Create a new exchange rate.
    """
    service = get_currency_service(db)
    
    try:
        return service.create_exchange_rate(rate.dict(), current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/exchange-rates/{source_code}/{target_code}",
    summary="Get exchange rate",
    description="Get the exchange rate between two currencies.",
    tags=["Exchange Rates"]
)
async def get_exchange_rate(
    source_code: str,
    target_code: str,
    rate_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get the exchange rate between two currencies.
    """
    service = get_currency_service(db)
    
    rate = service.get_exchange_rate(source_code, target_code, rate_date)
    
    if rate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exchange rate from {source_code} to {target_code} not found"
        )
    
    return {
        "source_currency": source_code.upper(),
        "target_currency": target_code.upper(),
        "rate": str(rate),
        "date": rate_date or date.today()
    }


@router.post(
    "/convert",
    response_model=ConversionResponse,
    summary="Convert amount between currencies",
    description="Convert an amount from one currency to another.",
    tags=["Exchange Rates"]
)
async def convert_currency(
    conversion: ConversionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ConversionResponse:
    """
    Convert an amount from one currency to another.
    """
    service = get_currency_service(db)
    
    rate = service.get_exchange_rate(
        conversion.from_currency,
        conversion.to_currency,
        conversion.conversion_date
    )
    
    if rate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exchange rate from {conversion.from_currency} to {conversion.to_currency} not found"
        )
    
    converted_amount = conversion.amount * rate
    
    return ConversionResponse(
        original_amount=conversion.amount,
        original_currency=conversion.from_currency,
        converted_amount=converted_amount,
        target_currency=conversion.to_currency,
        exchange_rate=rate,
        conversion_date=conversion.conversion_date or date.today(),
        rate_source="System"
    )