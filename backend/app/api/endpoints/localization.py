"""
Localization API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.services.localization.i18n_service import I18nService

router = APIRouter()


@router.get(
    "/languages",
    summary="Get supported languages",
    description="Get list of supported languages.",
    tags=["Localization"]
)
async def get_languages(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get supported languages."""
    service = I18nService(db)
    return service.get_supported_languages()


@router.get(
    "/translations/{language_code}",
    summary="Get translations",
    description="Get translations for a language.",
    tags=["Localization"]
)
async def get_translations(
    language_code: str,
    key: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get translations for a language."""
    service = I18nService(db)
    
    if key:
        return {"key": key, "value": service.get_translation(key, language_code)}
    
    # Return empty dict for now - would implement bulk translation retrieval
    return {}


@router.post(
    "/translations",
    summary="Set translation",
    description="Set translation for a key.",
    tags=["Localization"]
)
async def set_translation(
    key: str,
    language_code: str,
    value: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Set translation for a key."""
    service = I18nService(db)
    
    translation = service.set_translation(key, language_code, value)
    
    return translation


@router.post(
    "/currency/format",
    summary="Format currency",
    description="Format currency amount.",
    tags=["Localization"]
)
async def format_currency(
    amount: float,
    currency_code: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Format currency amount."""
    service = I18nService(db)
    
    formatted = service.format_currency(amount, currency_code)
    
    return {"amount": amount, "currency_code": currency_code, "formatted": formatted}