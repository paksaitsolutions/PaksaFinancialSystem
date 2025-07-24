"""
Schemas for company operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class CompanyRegistrationRequest(BaseModel):
    """Schema for company registration request."""
    company_name: str = Field(..., description="Company name")
    email: EmailStr = Field(..., description="Company email")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")
    industry: Optional[str] = Field(None, description="Industry")
    business_type: Optional[str] = Field(None, description="Business type")
    tax_id: Optional[str] = Field(None, description="Tax ID")
    registration_number: Optional[str] = Field(None, description="Registration number")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    default_currency: str = Field("USD", description="Default currency")
    default_language: str = Field("en-US", description="Default language")
    timezone: str = Field("UTC", description="Timezone")
    fiscal_year_start: str = Field("01-01", description="Fiscal year start (MM-DD)")


class CompanyResponse(BaseModel):
    """Schema for company response."""
    id: UUID = Field(..., description="Company ID")
    company_name: str = Field(..., description="Company name")
    company_code: str = Field(..., description="Company code")
    email: str = Field(..., description="Company email")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")
    industry: Optional[str] = Field(None, description="Industry")
    business_type: Optional[str] = Field(None, description="Business type")
    tax_id: Optional[str] = Field(None, description="Tax ID")
    registration_number: Optional[str] = Field(None, description="Registration number")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    primary_color: Optional[str] = Field(None, description="Primary color")
    secondary_color: Optional[str] = Field(None, description="Secondary color")
    default_currency: str = Field(..., description="Default currency")
    default_language: str = Field(..., description="Default language")
    timezone: str = Field(..., description="Timezone")
    date_format: str = Field(..., description="Date format")
    fiscal_year_start: str = Field(..., description="Fiscal year start")
    tax_settings: Optional[Dict[str, Any]] = Field(None, description="Tax settings")
    enabled_modules: Optional[Dict[str, bool]] = Field(None, description="Enabled modules")
    numbering_formats: Optional[Dict[str, str]] = Field(None, description="Numbering formats")
    subscription_tier: str = Field(..., description="Subscription tier")
    status: str = Field(..., description="Company status")
    trial_ends_at: Optional[datetime] = Field(None, description="Trial end date")
    database_schema: Optional[str] = Field(None, description="Database schema")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class CompanyUpdateRequest(BaseModel):
    """Schema for company update request."""
    company_name: Optional[str] = Field(None, description="Company name")
    email: Optional[EmailStr] = Field(None, description="Company email")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")
    industry: Optional[str] = Field(None, description="Industry")
    business_type: Optional[str] = Field(None, description="Business type")
    tax_id: Optional[str] = Field(None, description="Tax ID")
    registration_number: Optional[str] = Field(None, description="Registration number")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    primary_color: Optional[str] = Field(None, description="Primary color")
    secondary_color: Optional[str] = Field(None, description="Secondary color")
    default_currency: Optional[str] = Field(None, description="Default currency")
    default_language: Optional[str] = Field(None, description="Default language")
    timezone: Optional[str] = Field(None, description="Timezone")
    date_format: Optional[str] = Field(None, description="Date format")
    fiscal_year_start: Optional[str] = Field(None, description="Fiscal year start")
    tax_settings: Optional[Dict[str, Any]] = Field(None, description="Tax settings")
    enabled_modules: Optional[Dict[str, bool]] = Field(None, description="Enabled modules")
    numbering_formats: Optional[Dict[str, str]] = Field(None, description="Numbering formats")


class CompanyUserRequest(BaseModel):
    """Schema for adding user to company."""
    user_id: UUID = Field(..., description="User ID")
    role: str = Field("user", description="User role")
    is_admin: bool = Field(False, description="Is admin user")
    permissions: Optional[Dict[str, Any]] = Field(None, description="User permissions")


class CompanyUserResponse(BaseModel):
    """Schema for company user response."""
    id: UUID = Field(..., description="Company user ID")
    company_id: UUID = Field(..., description="Company ID")
    user_id: UUID = Field(..., description="User ID")
    role: str = Field(..., description="User role")
    is_admin: bool = Field(..., description="Is admin user")
    is_active: bool = Field(..., description="Is active")
    permissions: Optional[Dict[str, Any]] = Field(None, description="User permissions")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True


class CompanySettingsRequest(BaseModel):
    """Schema for company settings update."""
    chart_of_accounts_template: Optional[str] = Field(None, description="Chart of accounts template")
    approval_workflows: Optional[Dict[str, Any]] = Field(None, description="Approval workflows")
    integrations: Optional[Dict[str, Any]] = Field(None, description="Integration settings")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields")
    notification_settings: Optional[Dict[str, Any]] = Field(None, description="Notification settings")
    security_settings: Optional[Dict[str, Any]] = Field(None, description="Security settings")


class CompanySettingsResponse(BaseModel):
    """Schema for company settings response."""
    id: UUID = Field(..., description="Settings ID")
    company_id: UUID = Field(..., description="Company ID")
    chart_of_accounts_template: Optional[str] = Field(None, description="Chart of accounts template")
    approval_workflows: Optional[Dict[str, Any]] = Field(None, description="Approval workflows")
    integrations: Optional[Dict[str, Any]] = Field(None, description="Integration settings")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields")
    notification_settings: Optional[Dict[str, Any]] = Field(None, description="Notification settings")
    security_settings: Optional[Dict[str, Any]] = Field(None, description="Security settings")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True