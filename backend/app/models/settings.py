from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Numeric
from sqlalchemy.sql import func
from app.core.database import Base

class CompanySettings(Base):
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    company_code = Column(String(50))
    tax_id = Column(String(50))
    registration_number = Column(String(100))
    company_address = Column(Text)
    
    # Financial Settings
    base_currency = Column(String(3), default="USD")
    fiscal_year_start = Column(String(20), default="January")
    decimal_places = Column(Integer, default=2)
    rounding_method = Column(String(20), default="round")
    multi_currency_enabled = Column(Boolean, default=False)
    
    # Regional Settings
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    date_format = Column(String(20), default="MM/DD/YYYY")
    time_format = Column(String(2), default="12")
    number_format = Column(String(10), default="US")
    week_start = Column(String(10), default="Sunday")
    
    # Document Settings
    invoice_prefix = Column(String(10), default="INV-")
    invoice_start_number = Column(Integer, default=1000)
    bill_prefix = Column(String(10), default="BILL-")
    payment_prefix = Column(String(10), default="PAY-")
    auto_numbering_enabled = Column(Boolean, default=True)
    
    # System Preferences
    session_timeout = Column(Integer, default=60)
    default_page_size = Column(Integer, default=25)
    default_theme = Column(String(20), default="light")
    backup_frequency = Column(String(20), default="daily")
    audit_trail_enabled = Column(Boolean, default=True)
    email_notifications_enabled = Column(Boolean, default=True)
    two_factor_auth_required = Column(Boolean, default=False)
    auto_save_enabled = Column(Boolean, default=True)
    
    # Integration Settings
    api_rate_limit = Column(Integer, default=1000)
    webhook_timeout = Column(Integer, default=30)
    api_logging_enabled = Column(Boolean, default=True)
    webhook_retry_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    setting_key = Column(String(100), nullable=False)
    setting_value = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), nullable=False, unique=True)
    setting_value = Column(Text)
    description = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())