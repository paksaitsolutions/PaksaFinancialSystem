"""
Service logic for company settings: business rules, validation, and DB operations.
"""
from ..models.company_settings import CompanySettings
from ..schemas.company_settings import CompanySettingsCreate, CompanySettingsUpdate
from fastapi import HTTPException
from sqlalchemy.orm import Session


def get_company_settings(db: Session, company_id: int):
    """Get Company Settings."""
    settings = db.query(CompanySettings).filter(CompanySettings.company_id == company_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Company settings not found")
    return settings

def create_company_settings(db: Session, company_id: int, settings_in: CompanySettingsCreate):
    """Create Company Settings."""
    existing = db.query(CompanySettings).filter(CompanySettings.company_id == company_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Settings already exist for this company")
    settings = CompanySettings(company_id=company_id, **settings_in.dict())
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings

def update_company_settings(db: Session, company_id: int, settings_in: CompanySettingsUpdate):
    """Update Company Settings."""
    settings = db.query(CompanySettings).filter(CompanySettings.company_id == company_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Company settings not found")
    for field, value in settings_in.dict(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings
