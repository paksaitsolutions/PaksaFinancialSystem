from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.company_settings import CompanySettingsBase, CompanySettingsCreate, CompanySettingsUpdate, CompanySettingsInDB
from app.models.company_settings import CompanySettings
from app.models.company import Company
from app.services.company.company_service import get_db
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/company/{company_id}/settings", response_model=CompanySettingsInDB)
def get_company_settings(company_id: int, db: Session = Depends(get_db)):
    """Get company settings by company ID"""
    try:
        settings = db.query(CompanySettings).filter(CompanySettings.company_id == company_id).first()
        if not settings:
            # Create default settings if none exist
            default_settings = CompanySettings(
                company_id=company_id,
                company_name="Paksa Financial System",
                company_code="PAKSA001",
                base_currency="USD",
                fiscal_year_start="January",
                decimal_places=2,
                rounding_method="round",
                multi_currency_enabled=False,
                timezone="UTC",
                language="en",
                date_format="MM/DD/YYYY",
                time_format="12",
                number_format="US",
                week_start="Sunday",
                invoice_prefix="INV-",
                invoice_start_number=1000,
                bill_prefix="BILL-",
                payment_prefix="PAY-",
                auto_numbering_enabled=True,
                session_timeout=60,
                default_page_size=25,
                default_theme="light",
                backup_frequency="daily",
                audit_trail_enabled=True,
                email_notifications_enabled=True,
                two_factor_auth_required=False,
                auto_save_enabled=True,
                api_rate_limit=1000,
                webhook_timeout=30,
                api_logging_enabled=True,
                webhook_retry_enabled=True
            )
            db.add(default_settings)
            db.commit()
            db.refresh(default_settings)
            return default_settings
        return settings
    except Exception as e:
        logger.error(f"Error getting company settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/company/{company_id}/settings", response_model=CompanySettingsInDB)
def create_company_settings(company_id: int, settings_in: CompanySettingsCreate, db: Session = Depends(get_db)):
    """Create new company settings"""
    try:
        # Check if company exists
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Check if settings already exist
        existing_settings = db.query(CompanySettings).filter(CompanySettings.company_id == company_id).first()
        if existing_settings:
            raise HTTPException(status_code=400, detail="Company settings already exist")
        
        # Create new settings
        settings_data = settings_in.dict()
        settings_data['company_id'] = company_id
        settings = CompanySettings(**settings_data)
        
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
        logger.info(f"Created company settings for company {company_id}")
        return settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating company settings: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/company/{company_id}/settings", response_model=CompanySettingsInDB)
def update_company_settings(company_id: int, settings_in: CompanySettingsUpdate, db: Session = Depends(get_db)):
    """Update existing company settings"""
    try:
        settings = db.query(CompanySettings).filter(CompanySettings.company_id == company_id).first()
        if not settings:
            raise HTTPException(status_code=404, detail="Company settings not found")
        
        # Update only provided fields
        update_data = settings_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(settings, field):
                setattr(settings, field, value)
        
        db.commit()
        db.refresh(settings)
        
        logger.info(f"Updated company settings for company {company_id}")
        return settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating company settings: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/company/{company_id}/settings")
def delete_company_settings(company_id: int, db: Session = Depends(get_db)):
    """Delete company settings"""
    try:
        settings = db.query(CompanySettings).filter(CompanySettings.company_id == company_id).first()
        if not settings:
            raise HTTPException(status_code=404, detail="Company settings not found")
        
        db.delete(settings)
        db.commit()
        
        logger.info(f"Deleted company settings for company {company_id}")
        return {"message": "Company settings deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting company settings: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/settings/defaults", response_model=Dict[str, Any])
def get_default_settings():
    """Get default settings configuration"""
    return {
        "currencies": [
            {"label": "US Dollar (USD)", "value": "USD"},
            {"label": "Euro (EUR)", "value": "EUR"},
            {"label": "British Pound (GBP)", "value": "GBP"},
            {"label": "Canadian Dollar (CAD)", "value": "CAD"},
            {"label": "Australian Dollar (AUD)", "value": "AUD"},
            {"label": "Japanese Yen (JPY)", "value": "JPY"},
            {"label": "Swiss Franc (CHF)", "value": "CHF"},
            {"label": "Chinese Yuan (CNY)", "value": "CNY"},
            {"label": "Indian Rupee (INR)", "value": "INR"},
            {"label": "Pakistani Rupee (PKR)", "value": "PKR"}
        ],
        "timezones": [
            {"label": "UTC", "value": "UTC"},
            {"label": "Eastern Time (ET)", "value": "America/New_York"},
            {"label": "Central Time (CT)", "value": "America/Chicago"},
            {"label": "Mountain Time (MT)", "value": "America/Denver"},
            {"label": "Pacific Time (PT)", "value": "America/Los_Angeles"},
            {"label": "London (GMT)", "value": "Europe/London"},
            {"label": "Paris (CET)", "value": "Europe/Paris"},
            {"label": "Tokyo (JST)", "value": "Asia/Tokyo"},
            {"label": "Sydney (AEST)", "value": "Australia/Sydney"},
            {"label": "Karachi (PKT)", "value": "Asia/Karachi"},
            {"label": "Dubai (GST)", "value": "Asia/Dubai"}
        ],
        "languages": [
            {"label": "English", "value": "en"},
            {"label": "Spanish", "value": "es"},
            {"label": "French", "value": "fr"},
            {"label": "German", "value": "de"},
            {"label": "Italian", "value": "it"},
            {"label": "Portuguese", "value": "pt"},
            {"label": "Arabic", "value": "ar"},
            {"label": "Urdu", "value": "ur"},
            {"label": "Chinese (Simplified)", "value": "zh-CN"},
            {"label": "Japanese", "value": "ja"}
        ],
        "dateFormats": [
            {"label": "MM/DD/YYYY (US)", "value": "MM/DD/YYYY"},
            {"label": "DD/MM/YYYY (UK)", "value": "DD/MM/YYYY"},
            {"label": "YYYY-MM-DD (ISO)", "value": "YYYY-MM-DD"},
            {"label": "DD.MM.YYYY (German)", "value": "DD.MM.YYYY"},
            {"label": "DD-MM-YYYY", "value": "DD-MM-YYYY"}
        ],
        "themes": [
            {"label": "Light Theme", "value": "light"},
            {"label": "Dark Theme", "value": "dark"},
            {"label": "Auto (System)", "value": "auto"}
        ]
    }