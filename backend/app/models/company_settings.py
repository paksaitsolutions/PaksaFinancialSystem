from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class CompanySettings(Base):
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False, unique=True)
    
    # Company Information
    company_name = Column(String(255), nullable=False)
    company_code = Column(String(50), nullable=True)
    tax_id = Column(String(100), nullable=True)
    registration_number = Column(String(100), nullable=True)
    company_address = Column(Text, nullable=True)
    
    # Financial Settings
    base_currency = Column(String(3), nullable=False, default='USD')
    fiscal_year_start = Column(String(20), nullable=False, default='January')
    decimal_places = Column(Integer, nullable=False, default=2)
    rounding_method = Column(String(20), nullable=False, default='round')
    multi_currency_enabled = Column(Boolean, nullable=False, default=False)
    
    # Regional Settings
    timezone = Column(String(50), nullable=False, default='UTC')
    language = Column(String(10), nullable=False, default='en')
    date_format = Column(String(20), nullable=False, default='MM/DD/YYYY')
    time_format = Column(String(2), nullable=False, default='12')
    number_format = Column(String(10), nullable=False, default='US')
    week_start = Column(String(10), nullable=False, default='Sunday')
    
    # Document Settings
    invoice_prefix = Column(String(20), nullable=True, default='INV-')
    invoice_start_number = Column(Integer, nullable=False, default=1000)
    bill_prefix = Column(String(20), nullable=True, default='BILL-')
    payment_prefix = Column(String(20), nullable=True, default='PAY-')
    auto_numbering_enabled = Column(Boolean, nullable=False, default=True)
    
    # System Preferences
    session_timeout = Column(Integer, nullable=False, default=60)
    default_page_size = Column(Integer, nullable=False, default=25)
    default_theme = Column(String(20), nullable=False, default='light')
    backup_frequency = Column(String(20), nullable=False, default='daily')
    audit_trail_enabled = Column(Boolean, nullable=False, default=True)
    email_notifications_enabled = Column(Boolean, nullable=False, default=True)
    two_factor_auth_required = Column(Boolean, nullable=False, default=False)
    auto_save_enabled = Column(Boolean, nullable=False, default=True)
    
    # Integration Settings
    api_rate_limit = Column(Integer, nullable=False, default=1000)
    webhook_timeout = Column(Integer, nullable=False, default=30)
    api_logging_enabled = Column(Boolean, nullable=False, default=True)
    webhook_retry_enabled = Column(Boolean, nullable=False, default=True)
    
    # Legacy fields (for backward compatibility)
    invoice_template = Column(String, nullable=True)
    branding = Column(JSON, nullable=True)
    default_currency = Column(String, nullable=True)  # Deprecated, use base_currency
    tax_rates = Column(JSON, nullable=True)
    payment_methods = Column(JSON, nullable=True)
    document_numbering = Column(JSON, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    notifications = Column(JSON, nullable=True)
    integrations = Column(JSON, nullable=True)
    feature_toggles = Column(JSON, nullable=True)
    data_retention_policy = Column(String, nullable=True)

    company = relationship("Company", back_populates="settings")
