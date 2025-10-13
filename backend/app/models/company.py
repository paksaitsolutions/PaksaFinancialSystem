"""
Company profile models for multi-tenant support.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class CompanyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"


class SubscriptionTier(str, Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Company(BaseModel):
    """
    Company profile for multi-tenant support.
    """
    __tablename__ = "companies"
    
    # Basic company information
    company_name = Column(String(200), nullable=False)
    company_code = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Industry and business details
    industry = Column(String(100), nullable=True)
    business_type = Column(String(50), nullable=True)
    tax_id = Column(String(50), nullable=True)
    registration_number = Column(String(100), nullable=True)
    
    # Address information
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Branding
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), nullable=True)  # Hex color
    secondary_color = Column(String(7), nullable=True)
    
    # Localization settings
    default_currency = Column(String(3), nullable=False, default="USD")
    default_language = Column(String(5), nullable=False, default="en-US")
    timezone = Column(String(50), nullable=False, default="UTC")
    date_format = Column(String(20), nullable=False, default="MM/DD/YYYY")
    
    # Fiscal settings
    fiscal_year_start = Column(String(5), nullable=False, default="01-01")  # MM-DD
    tax_settings = Column(JSON, nullable=True)
    
    # System configuration
    enabled_modules = Column(JSON, nullable=True)
    numbering_formats = Column(JSON, nullable=True)
    
    # Subscription and status
    subscription_tier = Column(String(20), nullable=False, default=SubscriptionTier.BASIC)
    status = Column(String(20), nullable=False, default=CompanyStatus.TRIAL)
    trial_ends_at = Column(DateTime, nullable=True)
    
    # Database isolation
    database_schema = Column(String(100), nullable=True)
    
    def __repr__(self) -> str:
        return f"<Company(code='{self.company_code}', name='{self.company_name}')>"


class CompanyUser(BaseModel):
    """
    Association between companies and users.
    """
    __tablename__ = "company_users"
    
    company_id = Column(GUID(), nullable=False, index=True)
    user_id = Column(GUID(), nullable=False, index=True)
    
    # Role within company
    role = Column(String(50), nullable=False, default="user")
    is_admin = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Permissions
    permissions = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<CompanyUser(company_id={self.company_id}, user_id={self.user_id}, role='{self.role}')>"


class CompanySettings(BaseModel):
    """
    Company-specific settings and configurations.
    """
    __tablename__ = "company_settings"
    
    company_id = Column(GUID(), nullable=False, index=True)
    
    # Chart of accounts template
    chart_of_accounts_template = Column(String(50), nullable=True)
    
    # Approval workflows
    approval_workflows = Column(JSON, nullable=True)
    
    # Integration settings
    integrations = Column(JSON, nullable=True)
    
    # Custom fields
    custom_fields = Column(JSON, nullable=True)
    
    # Notification settings
    notification_settings = Column(JSON, nullable=True)
    
    # Security settings
    security_settings = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<CompanySettings(company_id={self.company_id})>"