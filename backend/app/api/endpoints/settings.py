from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.company_settings import CompanySettingsBase, CompanySettingsCreate, CompanySettingsUpdate, CompanySettingsInDB
from app.models.company_settings import CompanySettings
from app.models.company import Company
from app.services.company.company_service import get_db
from typing import List

router = APIRouter()

@router.get("/company/{company_id}/settings", response_model=CompanySettingsInDB)
def get_company_settings(company_id: int, db: Session = Depends(get_db)):
    settings = db.query(CompanySettings).filter(CompanySettings.company_id == company_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Company settings not found")
    return settings

@router.post("/company/{company_id}/settings", response_model=CompanySettingsInDB)
def create_company_settings(company_id: int, settings_in: CompanySettingsCreate, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    settings = CompanySettings(**settings_in.dict(), company_id=company_id)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings

@router.put("/company/{company_id}/settings", response_model=CompanySettingsInDB)
def update_company_settings(company_id: int, settings_in: CompanySettingsUpdate, db: Session = Depends(get_db)):
    settings = db.query(CompanySettings).filter(CompanySettings.company_id == company_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Company settings not found")
    for field, value in settings_in.dict(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings
