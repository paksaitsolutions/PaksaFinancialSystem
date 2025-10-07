from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any

class CompanySettingsBase(BaseModel):
    # Company Information
    company_name: str = Field(..., min_length=1, max_length=255)
    company_code: Optional[str] = Field(None, max_length=50)
    tax_id: Optional[str] = Field(None, max_length=100)
    registration_number: Optional[str] = Field(None, max_length=100)
    company_address: Optional[str] = None
    
    # Financial Settings
    base_currency: str = Field(default='USD', pattern=r'^[A-Z]{3}$')
    fiscal_year_start: str = Field(default='January')
    decimal_places: int = Field(default=2, ge=0, le=6)
    rounding_method: str = Field(default='round')
    multi_currency_enabled: bool = Field(default=False)
    
    # Regional Settings
    timezone: str = Field(default='UTC')
    language: str = Field(default='en', max_length=10)
    date_format: str = Field(default='MM/DD/YYYY')
    time_format: str = Field(default='12', pattern=r'^(12|24)$')
    number_format: str = Field(default='US')
    week_start: str = Field(default='Sunday')
    
    # Document Settings
    invoice_prefix: Optional[str] = Field(default='INV-', max_length=20)
    invoice_start_number: int = Field(default=1000, ge=1)
    bill_prefix: Optional[str] = Field(default='BILL-', max_length=20)
    payment_prefix: Optional[str] = Field(default='PAY-', max_length=20)
    auto_numbering_enabled: bool = Field(default=True)
    
    # System Preferences
    session_timeout: int = Field(default=60, ge=5, le=480)
    default_page_size: int = Field(default=25, ge=10, le=100)
    default_theme: str = Field(default='light')
    backup_frequency: str = Field(default='daily')
    audit_trail_enabled: bool = Field(default=True)
    email_notifications_enabled: bool = Field(default=True)
    two_factor_auth_required: bool = Field(default=False)
    auto_save_enabled: bool = Field(default=True)
    
    # Integration Settings
    api_rate_limit: int = Field(default=1000, ge=10, le=10000)
    webhook_timeout: int = Field(default=30, ge=5, le=300)
    api_logging_enabled: bool = Field(default=True)
    webhook_retry_enabled: bool = Field(default=True)
    
    # Legacy fields (for backward compatibility)
    invoice_template: Optional[str] = None
    branding: Optional[Dict[str, Any]] = None
    default_currency: Optional[str] = None  # Deprecated
    tax_rates: Optional[Dict[str, float]] = None
    payment_methods: Optional[list] = None
    document_numbering: Optional[Dict[str, str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None
    integrations: Optional[Dict[str, Any]] = None
    feature_toggles: Optional[Dict[str, bool]] = None
    data_retention_policy: Optional[str] = None
    
    @validator('fiscal_year_start')
    def validate_fiscal_year_start(cls, v):
        valid_months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        if v not in valid_months:
            raise ValueError('Invalid fiscal year start month')
        return v
    
    @validator('rounding_method')
    def validate_rounding_method(cls, v):
        valid_methods = ['round', 'ceil', 'floor', 'bankers']
        if v not in valid_methods:
            raise ValueError('Invalid rounding method')
        return v
    
    @validator('default_theme')
    def validate_theme(cls, v):
        valid_themes = ['light', 'dark', 'auto']
        if v not in valid_themes:
            raise ValueError('Invalid theme')
        return v
    
    @validator('backup_frequency')
    def validate_backup_frequency(cls, v):
        valid_frequencies = ['hourly', 'daily', 'weekly', 'monthly']
        if v not in valid_frequencies:
            raise ValueError('Invalid backup frequency')
        return v

class CompanySettingsCreate(CompanySettingsBase):
    company_id: int

class CompanySettingsUpdate(BaseModel):
    # All fields optional for updates
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_code: Optional[str] = Field(None, max_length=50)
    tax_id: Optional[str] = Field(None, max_length=100)
    registration_number: Optional[str] = Field(None, max_length=100)
    company_address: Optional[str] = None
    base_currency: Optional[str] = Field(None, pattern=r'^[A-Z]{3}$')
    fiscal_year_start: Optional[str] = None
    decimal_places: Optional[int] = Field(None, ge=0, le=6)
    rounding_method: Optional[str] = None
    multi_currency_enabled: Optional[bool] = None
    timezone: Optional[str] = None
    language: Optional[str] = Field(None, max_length=10)
    date_format: Optional[str] = None
    time_format: Optional[str] = Field(None, pattern=r'^(12|24)$')
    number_format: Optional[str] = None
    week_start: Optional[str] = None
    invoice_prefix: Optional[str] = Field(None, max_length=20)
    invoice_start_number: Optional[int] = Field(None, ge=1)
    bill_prefix: Optional[str] = Field(None, max_length=20)
    payment_prefix: Optional[str] = Field(None, max_length=20)
    auto_numbering_enabled: Optional[bool] = None
    session_timeout: Optional[int] = Field(None, ge=5, le=480)
    default_page_size: Optional[int] = Field(None, ge=10, le=100)
    default_theme: Optional[str] = None
    backup_frequency: Optional[str] = None
    audit_trail_enabled: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None
    two_factor_auth_required: Optional[bool] = None
    auto_save_enabled: Optional[bool] = None
    api_rate_limit: Optional[int] = Field(None, ge=10, le=10000)
    webhook_timeout: Optional[int] = Field(None, ge=5, le=300)
    api_logging_enabled: Optional[bool] = None
    webhook_retry_enabled: Optional[bool] = None
    
    # Legacy fields
    invoice_template: Optional[str] = None
    branding: Optional[Dict[str, Any]] = None
    default_currency: Optional[str] = None
    tax_rates: Optional[Dict[str, float]] = None
    payment_methods: Optional[list] = None
    document_numbering: Optional[Dict[str, str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None
    integrations: Optional[Dict[str, Any]] = None
    feature_toggles: Optional[Dict[str, bool]] = None
    data_retention_policy: Optional[str] = None

class CompanySettingsInDB(CompanySettingsBase):
    id: int
    company_id: int

    class Config:
        orm_mode = True
