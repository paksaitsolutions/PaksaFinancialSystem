from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class CompanySettingsBase(BaseModel):
    company_name: str
    company_code: Optional[str] = None
    tax_id: Optional[str] = None
    registration_number: Optional[str] = None
    company_address: Optional[str] = None
    base_currency: str = "USD"
    fiscal_year_start: str = "January"
    decimal_places: int = 2
    rounding_method: str = "round"
    multi_currency_enabled: bool = False
    timezone: str = "UTC"
    language: str = "en"
    date_format: str = "MM/DD/YYYY"
    time_format: str = "12"
    number_format: str = "US"
    week_start: str = "Sunday"
    invoice_prefix: str = "INV-"
    invoice_start_number: int = 1000
    bill_prefix: str = "BILL-"
    payment_prefix: str = "PAY-"
    auto_numbering_enabled: bool = True
    session_timeout: int = 60
    default_page_size: int = 25
    default_theme: str = "light"
    backup_frequency: str = "daily"
    audit_trail_enabled: bool = True
    email_notifications_enabled: bool = True
    two_factor_auth_required: bool = False
    auto_save_enabled: bool = True
    api_rate_limit: int = 1000
    webhook_timeout: int = 30
    api_logging_enabled: bool = True
    webhook_retry_enabled: bool = True

    @validator('decimal_places')
    def validate_decimal_places(cls, v):
        if v < 0 or v > 6:
            raise ValueError('Decimal places must be between 0 and 6')
        return v

    @validator('session_timeout')
    def validate_session_timeout(cls, v):
        if v < 5 or v > 480:
            raise ValueError('Session timeout must be between 5 and 480 minutes')
        return v

class CompanySettingsCreate(CompanySettingsBase):
    pass

class CompanySettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    company_code: Optional[str] = None
    tax_id: Optional[str] = None
    registration_number: Optional[str] = None
    company_address: Optional[str] = None
    base_currency: Optional[str] = None
    fiscal_year_start: Optional[str] = None
    decimal_places: Optional[int] = None
    rounding_method: Optional[str] = None
    multi_currency_enabled: Optional[bool] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    number_format: Optional[str] = None
    week_start: Optional[str] = None
    invoice_prefix: Optional[str] = None
    invoice_start_number: Optional[int] = None
    bill_prefix: Optional[str] = None
    payment_prefix: Optional[str] = None
    auto_numbering_enabled: Optional[bool] = None
    session_timeout: Optional[int] = None
    default_page_size: Optional[int] = None
    default_theme: Optional[str] = None
    backup_frequency: Optional[str] = None
    audit_trail_enabled: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None
    two_factor_auth_required: Optional[bool] = None
    auto_save_enabled: Optional[bool] = None
    api_rate_limit: Optional[int] = None
    webhook_timeout: Optional[int] = None
    api_logging_enabled: Optional[bool] = None
    webhook_retry_enabled: Optional[bool] = None

class CompanySettings(CompanySettingsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserSettingsBase(BaseModel):
    user_id: str
    setting_key: str
    setting_value: Optional[str] = None

class UserSettingsCreate(UserSettingsBase):
    pass

class UserSettingsUpdate(BaseModel):
    setting_value: Optional[str] = None

class UserSettings(UserSettingsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SystemSettingsBase(BaseModel):
    setting_key: str
    setting_value: Optional[str] = None
    description: Optional[str] = None
    is_encrypted: bool = False

class SystemSettingsCreate(SystemSettingsBase):
    pass

class SystemSettingsUpdate(BaseModel):
    setting_value: Optional[str] = None
    description: Optional[str] = None
    is_encrypted: Optional[bool] = None

class SystemSettings(SystemSettingsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True