from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.crud.settings import company_settings_crud, user_settings_crud, system_settings_crud
from app.schemas.settings import (
    CompanySettings, CompanySettingsCreate, CompanySettingsUpdate,
    UserSettings, UserSettingsCreate, UserSettingsUpdate,
    SystemSettings, SystemSettingsCreate, SystemSettingsUpdate
)

router = APIRouter()

# Company Settings Endpoints
@router.get("/company/{company_id}", response_model=CompanySettings)
def get_company_settings(company_id: int, db: Session = Depends(get_db)):
    """Get company settings"""
    settings = company_settings_crud.get_or_create_default(db=db, company_id=company_id)
    return settings

@router.put("/company/{company_id}", response_model=CompanySettings)
def update_company_settings(
    company_id: int,
    settings_update: CompanySettingsUpdate,
    db: Session = Depends(get_db)
):
    """Update company settings"""
    db_settings = company_settings_crud.get_by_company_id(db=db, company_id=company_id)
    if not db_settings:
        # Create default settings if they don't exist
        db_settings = company_settings_crud.get_or_create_default(db=db, company_id=company_id)
    
    return company_settings_crud.update(db=db, db_obj=db_settings, obj_in=settings_update)

@router.post("/company", response_model=CompanySettings)
def create_company_settings(
    settings: CompanySettingsCreate,
    db: Session = Depends(get_db)
):
    """Create new company settings"""
    return company_settings_crud.create(db=db, obj_in=settings)

# User Settings Endpoints
@router.get("/user/{user_id}", response_model=List[UserSettings])
def get_user_settings(user_id: str, db: Session = Depends(get_db)):
    """Get all settings for a user"""
    return user_settings_crud.get_user_settings(db=db, user_id=user_id)

@router.get("/user/{user_id}/{setting_key}", response_model=UserSettings)
def get_user_setting(user_id: str, setting_key: str, db: Session = Depends(get_db)):
    """Get specific user setting"""
    setting = user_settings_crud.get_user_setting(db=db, user_id=user_id, setting_key=setting_key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.put("/user/{user_id}/{setting_key}", response_model=UserSettings)
def update_user_setting(
    user_id: str,
    setting_key: str,
    setting_value: str,
    db: Session = Depends(get_db)
):
    """Create or update user setting"""
    return user_settings_crud.create_or_update(
        db=db, user_id=user_id, setting_key=setting_key, setting_value=setting_value
    )

@router.delete("/user/{user_id}/{setting_key}")
def delete_user_setting(user_id: str, setting_key: str, db: Session = Depends(get_db)):
    """Delete user setting"""
    success = user_settings_crud.delete_user_setting(db=db, user_id=user_id, setting_key=setting_key)
    if not success:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"message": "Setting deleted successfully"}

# System Settings Endpoints
@router.get("/system", response_model=List[SystemSettings])
def get_system_settings(db: Session = Depends(get_db)):
    """Get all system settings"""
    return system_settings_crud.get_all(db=db)

@router.get("/system/{setting_key}", response_model=SystemSettings)
def get_system_setting(setting_key: str, db: Session = Depends(get_db)):
    """Get specific system setting"""
    setting = system_settings_crud.get_by_key(db=db, setting_key=setting_key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.put("/system/{setting_key}", response_model=SystemSettings)
def update_system_setting(
    setting_key: str,
    setting_value: str,
    description: str = None,
    db: Session = Depends(get_db)
):
    """Create or update system setting"""
    return system_settings_crud.create_or_update(
        db=db, setting_key=setting_key, setting_value=setting_value, description=description
    )

@router.delete("/system/{setting_key}")
def delete_system_setting(setting_key: str, db: Session = Depends(get_db)):
    """Delete system setting"""
    success = system_settings_crud.delete_by_key(db=db, setting_key=setting_key)
    if not success:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"message": "Setting deleted successfully"}

# Validation endpoint
@router.post("/validate")
def validate_settings(settings: Dict[str, Any]):
    """Validate settings data"""
    errors = []
    
    # Company name validation
    if 'company_name' in settings and not settings['company_name']:
        errors.append("Company name is required")
    
    # Currency validation
    if 'base_currency' in settings and not settings['base_currency']:
        errors.append("Base currency is required")
    
    # Decimal places validation
    if 'decimal_places' in settings:
        decimal_places = settings['decimal_places']
        if not isinstance(decimal_places, int) or decimal_places < 0 or decimal_places > 6:
            errors.append("Decimal places must be between 0 and 6")
    
    # Session timeout validation
    if 'session_timeout' in settings:
        session_timeout = settings['session_timeout']
        if not isinstance(session_timeout, int) or session_timeout < 5 or session_timeout > 480:
            errors.append("Session timeout must be between 5 and 480 minutes")
    
    # Page size validation
    if 'default_page_size' in settings:
        page_size = settings['default_page_size']
        if not isinstance(page_size, int) or page_size < 1 or page_size > 1000:
            errors.append("Default page size must be between 1 and 1000")
    
    # API rate limit validation
    if 'api_rate_limit' in settings:
        rate_limit = settings['api_rate_limit']
        if not isinstance(rate_limit, int) or rate_limit < 10 or rate_limit > 10000:
            errors.append("API rate limit must be between 10 and 10000")
    
    # Webhook timeout validation
    if 'webhook_timeout' in settings:
        timeout = settings['webhook_timeout']
        if not isinstance(timeout, int) or timeout < 5 or timeout > 300:
            errors.append("Webhook timeout must be between 5 and 300 seconds")
    
    return {"valid": len(errors) == 0, "errors": errors}