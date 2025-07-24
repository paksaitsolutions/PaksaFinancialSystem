from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class CompanySettingsBase(BaseModel):
    company_id: int
    invoice_template: Optional[str] = None
    branding: Optional[Dict[str, Any]] = None
    default_currency: Optional[str] = None
    tax_rates: Optional[Dict[str, float]] = None
    language: Optional[str] = None
    payment_methods: Optional[list] = None
    document_numbering: Optional[Dict[str, str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None
    integrations: Optional[Dict[str, Any]] = None
    feature_toggles: Optional[Dict[str, bool]] = None
    data_retention_policy: Optional[str] = None

class CompanySettingsCreate(CompanySettingsBase):
    pass

class CompanySettingsUpdate(CompanySettingsBase):
    pass

class CompanySettingsInDB(CompanySettingsBase):
    id: int

    class Config:
        orm_mode = True
