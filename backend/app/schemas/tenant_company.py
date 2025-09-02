from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class TenantCompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    
    # Domain & Branding
    subdomain: str = Field(..., min_length=1, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    primary_color: Optional[str] = Field('#1976D2', regex=r'^#[0-9A-Fa-f]{6}$')
    secondary_color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    
    # Subscription & Limits
    plan: str = Field(..., max_length=50)
    max_users: int = Field(default=10, ge=1, le=10000)
    storage_limit_gb: int = Field(default=5, ge=1, le=1000)
    api_rate_limit: int = Field(default=1000, ge=100, le=100000)
    
    # Configuration
    timezone: str = Field(default='UTC', max_length=50)
    language: str = Field(default='en', max_length=10)
    currency: str = Field(default='USD', regex=r'^[A-Z]{3}$')
    date_format: str = Field(default='MM/DD/YYYY', max_length=20)
    
    # Features & Modules
    enabled_modules: Optional[List[str]] = None
    feature_flags: Optional[Dict[str, bool]] = None
    custom_settings: Optional[Dict[str, Any]] = None
    
    @validator('code')
    def validate_code(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Company code must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()
    
    @validator('subdomain')
    def validate_subdomain(cls, v):
        if not v.replace('-', '').isalnum():
            raise ValueError('Subdomain must contain only alphanumeric characters and hyphens')
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('Subdomain cannot start or end with a hyphen')
        return v.lower()
    
    @validator('plan')
    def validate_plan(cls, v):
        valid_plans = ['Basic', 'Professional', 'Enterprise', 'Custom']
        if v not in valid_plans:
            raise ValueError(f'Plan must be one of: {", ".join(valid_plans)}')
        return v
    
    @validator('size')
    def validate_size(cls, v):
        if v is not None:
            valid_sizes = ['Small', 'Medium', 'Large', 'Enterprise']
            if v not in valid_sizes:
                raise ValueError(f'Company size must be one of: {", ".join(valid_sizes)}')
        return v

class TenantCompanyCreate(TenantCompanyBase):
    # Admin user information for initial setup
    admin_name: str = Field(..., min_length=1, max_length=255)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8, max_length=128)
    admin_phone: Optional[str] = Field(None, max_length=20)
    
    # Optional trial configuration
    trial_days: Optional[int] = Field(None, ge=0, le=365)
    
    @validator('admin_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class TenantCompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    primary_color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    secondary_color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    max_users: Optional[int] = Field(None, ge=1, le=10000)
    storage_limit_gb: Optional[int] = Field(None, ge=1, le=1000)
    api_rate_limit: Optional[int] = Field(None, ge=100, le=100000)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    currency: Optional[str] = Field(None, regex=r'^[A-Z]{3}$')
    date_format: Optional[str] = Field(None, max_length=20)
    enabled_modules: Optional[List[str]] = None
    feature_flags: Optional[Dict[str, bool]] = None
    custom_settings: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['Active', 'Trial', 'Suspended', 'Inactive']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

class TenantCompanyInDB(TenantCompanyBase):
    id: int
    domain: str
    current_users: int
    status: str
    is_active: bool
    trial_ends_at: Optional[datetime]
    subscription_ends_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    
    class Config:
        orm_mode = True

class TenantCompanyResponse(TenantCompanyInDB):
    # Additional computed fields for API responses
    users_percentage: Optional[float] = None
    storage_used_gb: Optional[float] = None
    days_until_expiry: Optional[int] = None
    
    @validator('users_percentage', pre=True, always=True)
    def calculate_users_percentage(cls, v, values):
        if 'current_users' in values and 'max_users' in values and values['max_users'] > 0:
            return round((values['current_users'] / values['max_users']) * 100, 1)
        return 0.0

class CompanyAdminBase(BaseModel):
    company_id: int
    user_id: int
    role: str = Field(default='admin', max_length=50)
    permissions: Optional[Dict[str, Any]] = None
    is_primary: bool = Field(default=False)

class CompanyAdminCreate(CompanyAdminBase):
    pass

class CompanyAdminInDB(CompanyAdminBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class CompanyModuleBase(BaseModel):
    company_id: int
    module_name: str = Field(..., max_length=100)
    is_enabled: bool = Field(default=True)
    configuration: Optional[Dict[str, Any]] = None
    license_type: Optional[str] = Field(None, max_length=50)
    expires_at: Optional[datetime] = None

class CompanyModuleCreate(CompanyModuleBase):
    pass

class CompanyModuleUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    configuration: Optional[Dict[str, Any]] = None
    license_type: Optional[str] = Field(None, max_length=50)
    expires_at: Optional[datetime] = None

class CompanyModuleInDB(CompanyModuleBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class CompanySubscriptionBase(BaseModel):
    company_id: int
    plan_name: str = Field(..., max_length=50)
    billing_cycle: str = Field(default='monthly', max_length=20)
    amount: int = Field(..., ge=0)  # Amount in cents
    currency: str = Field(default='USD', regex=r'^[A-Z]{3}$')
    starts_at: datetime
    ends_at: Optional[datetime] = None
    auto_renew: bool = Field(default=True)
    payment_method: Optional[str] = Field(None, max_length=50)
    external_subscription_id: Optional[str] = Field(None, max_length=255)

class CompanySubscriptionCreate(CompanySubscriptionBase):
    pass

class CompanySubscriptionUpdate(BaseModel):
    plan_name: Optional[str] = Field(None, max_length=50)
    billing_cycle: Optional[str] = Field(None, max_length=20)
    amount: Optional[int] = Field(None, ge=0)
    ends_at: Optional[datetime] = None
    auto_renew: Optional[bool] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = None

class CompanySubscriptionInDB(CompanySubscriptionBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# Utility schemas for API responses
class CompanyStats(BaseModel):
    total_companies: int
    active_companies: int
    trial_companies: int
    suspended_companies: int
    total_users: int
    companies_by_plan: Dict[str, int]
    companies_by_status: Dict[str, int]

class CompanyActivationRequest(BaseModel):
    company_id: int

class CompanyActivationResponse(BaseModel):
    success: bool
    message: str
    company: TenantCompanyResponse
    access_token: Optional[str] = None