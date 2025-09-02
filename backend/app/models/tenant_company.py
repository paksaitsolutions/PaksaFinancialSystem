from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class TenantCompany(Base):
    __tablename__ = "tenant_companies"

    id = Column(Integer, primary_key=True, index=True)
    
    # Company Information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    industry = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)  # Small, Medium, Large, Enterprise
    address = Column(Text, nullable=True)
    
    # Domain & Branding
    domain = Column(String(255), nullable=False, unique=True, index=True)
    subdomain = Column(String(100), nullable=False, unique=True, index=True)
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), nullable=True, default='#1976D2')  # Hex color
    secondary_color = Column(String(7), nullable=True)
    
    # Subscription & Limits
    plan = Column(String(50), nullable=False, default='Basic')  # Basic, Professional, Enterprise, Custom
    max_users = Column(Integer, nullable=False, default=10)
    current_users = Column(Integer, nullable=False, default=0)
    storage_limit_gb = Column(Integer, nullable=False, default=5)
    api_rate_limit = Column(Integer, nullable=False, default=1000)
    
    # Status & Lifecycle
    status = Column(String(20), nullable=False, default='Active')  # Active, Trial, Suspended, Inactive
    is_active = Column(Boolean, nullable=False, default=True)
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
    
    # Configuration
    timezone = Column(String(50), nullable=False, default='UTC')
    language = Column(String(10), nullable=False, default='en')
    currency = Column(String(3), nullable=False, default='USD')
    date_format = Column(String(20), nullable=False, default='MM/DD/YYYY')
    
    # Features & Modules
    enabled_modules = Column(JSON, nullable=True)  # List of enabled modules
    feature_flags = Column(JSON, nullable=True)    # Feature toggles
    custom_settings = Column(JSON, nullable=True)  # Company-specific settings
    
    # Metadata
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    users = relationship("User", back_populates="company", foreign_keys="User.company_id")
    settings = relationship("CompanySettings", back_populates="company", uselist=False)
    
    def __repr__(self):
        return f"<TenantCompany(id={self.id}, name='{self.name}', code='{self.code}')>"

class CompanyAdmin(Base):
    __tablename__ = "company_admins"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("tenant_companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False, default='admin')  # admin, super_admin, owner
    permissions = Column(JSON, nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    company = relationship("TenantCompany")
    user = relationship("User")

class CompanyModule(Base):
    __tablename__ = "company_modules"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("tenant_companies.id"), nullable=False)
    module_name = Column(String(100), nullable=False)  # gl, ap, ar, payroll, etc.
    is_enabled = Column(Boolean, nullable=False, default=True)
    configuration = Column(JSON, nullable=True)
    license_type = Column(String(50), nullable=True)  # included, addon, premium
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    company = relationship("TenantCompany")

class CompanySubscription(Base):
    __tablename__ = "company_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("tenant_companies.id"), nullable=False)
    plan_name = Column(String(50), nullable=False)
    billing_cycle = Column(String(20), nullable=False, default='monthly')  # monthly, yearly
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String(3), nullable=False, default='USD')
    status = Column(String(20), nullable=False, default='active')  # active, cancelled, expired
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, nullable=False, default=True)
    payment_method = Column(String(50), nullable=True)
    external_subscription_id = Column(String(255), nullable=True)  # Stripe, PayPal, etc.
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    company = relationship("TenantCompany")