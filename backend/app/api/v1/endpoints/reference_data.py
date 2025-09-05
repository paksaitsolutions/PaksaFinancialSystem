"""
Reference Data API Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.reference_data_service import ReferenceDataService

router = APIRouter()


@router.get("/countries")
async def get_countries(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all countries"""
    service = ReferenceDataService(db)
    countries = service.get_countries(active_only)
    return [
        {
            "id": str(country.id),
            "code": country.code,
            "name": country.name,
            "full_name": country.full_name,
            "iso3_code": country.iso3_code,
            "phone_code": country.phone_code,
            "is_active": country.is_active
        }
        for country in countries
    ]


@router.get("/currencies")
async def get_currencies(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all currencies"""
    service = ReferenceDataService(db)
    currencies = service.get_currencies(active_only)
    return [
        {
            "id": str(currency.id),
            "code": currency.code,
            "name": currency.name,
            "symbol": currency.symbol,
            "decimal_places": currency.decimal_places,
            "is_active": currency.is_active
        }
        for currency in currencies
    ]


@router.get("/languages")
async def get_languages(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all languages"""
    service = ReferenceDataService(db)
    languages = service.get_languages(active_only)
    return [
        {
            "id": str(language.id),
            "code": language.code,
            "name": language.name,
            "native_name": language.native_name,
            "is_rtl": language.is_rtl,
            "is_active": language.is_active
        }
        for language in languages
    ]


@router.get("/timezones")
async def get_timezones(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all timezones"""
    service = ReferenceDataService(db)
    timezones = service.get_timezones(active_only)
    return [
        {
            "id": str(timezone.id),
            "code": timezone.code,
            "name": timezone.name,
            "utc_offset": timezone.utc_offset,
            "is_active": timezone.is_active
        }
        for timezone in timezones
    ]


@router.get("/account-types")
async def get_account_types(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all account types"""
    service = ReferenceDataService(db)
    account_types = service.get_account_types(active_only)
    return [
        {
            "id": str(account_type.id),
            "code": account_type.code,
            "name": account_type.name,
            "category": account_type.category,
            "normal_balance": account_type.normal_balance,
            "is_active": account_type.is_active
        }
        for account_type in account_types
    ]


@router.get("/payment-methods")
async def get_payment_methods(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all payment methods"""
    service = ReferenceDataService(db)
    payment_methods = service.get_payment_methods(active_only)
    return [
        {
            "id": str(payment_method.id),
            "code": payment_method.code,
            "name": payment_method.name,
            "description": payment_method.description,
            "is_active": payment_method.is_active
        }
        for payment_method in payment_methods
    ]


@router.get("/tax-types")
async def get_tax_types(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all tax types"""
    service = ReferenceDataService(db)
    tax_types = service.get_tax_types(active_only)
    return [
        {
            "id": str(tax_type.id),
            "code": tax_type.code,
            "name": tax_type.name,
            "description": tax_type.description,
            "is_active": tax_type.is_active
        }
        for tax_type in tax_types
    ]


@router.get("/bank-account-types")
async def get_bank_account_types(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all bank account types"""
    service = ReferenceDataService(db)
    bank_account_types = service.get_bank_account_types(active_only)
    return [
        {
            "id": str(bank_account_type.id),
            "code": bank_account_type.code,
            "name": bank_account_type.name,
            "description": bank_account_type.description,
            "is_active": bank_account_type.is_active
        }
        for bank_account_type in bank_account_types
    ]