"""
Unified Settings/Configuration System
Centralized configuration management for all modules
"""
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel, AuditMixin
from datetime import datetime
import json

class UnifiedSettings(BaseModel, AuditMixin):
    """Unified settings for all modules"""
    __tablename__ = "unified_settings"
    
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    module_name = Column(String(50), nullable=False, index=True)  # gl, ap, ar, tax, payroll, etc.
    setting_key = Column(String(100), nullable=False, index=True)
    setting_value = Column(JSON, nullable=False)
    setting_type = Column(String(20), default="string")  # string, number, boolean, json, array
    description = Column(Text)
    is_system_setting = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    
    # Relationships
    company = relationship("Company", viewonly=True)
    
    __table_args__ = (
        {"extend_existing": True},
    )

class SettingsTemplate(BaseModel, AuditMixin):
    """Settings templates for different modules"""
    __tablename__ = "settings_templates"
    
    template_name = Column(String(100), nullable=False, unique=True)
    module_name = Column(String(50), nullable=False)
    template_data = Column(JSON, nullable=False)
    is_default = Column(Boolean, default=False)
    description = Column(Text)
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedSettingsService:
    """Service for managing unified settings"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def get_setting(self, company_id: str, module: str, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        setting = await self.db.query(UnifiedSettings).filter(
            UnifiedSettings.company_id == company_id,
            UnifiedSettings.module_name == module,
            UnifiedSettings.setting_key == key
        ).first()
        
        return setting.setting_value if setting else default
    
    async def set_setting(self, company_id: str, module: str, key: str, value: Any, 
                         setting_type: str = "string", description: str = None) -> UnifiedSettings:
        """Set a setting value"""
        setting = await self.db.query(UnifiedSettings).filter(
            UnifiedSettings.company_id == company_id,
            UnifiedSettings.module_name == module,
            UnifiedSettings.setting_key == key
        ).first()
        
        if setting:
            setting.setting_value = value
            setting.setting_type = setting_type
            setting.updated_at = datetime.utcnow()
        else:
            setting = UnifiedSettings(
                company_id=company_id,
                module_name=module,
                setting_key=key,
                setting_value=value,
                setting_type=setting_type,
                description=description
            )
            self.db.add(setting)
        
        await self.db.commit()
        return setting
    
    async def get_module_settings(self, company_id: str, module: str) -> Dict[str, Any]:
        """Get all settings for a module"""
        settings = await self.db.query(UnifiedSettings).filter(
            UnifiedSettings.company_id == company_id,
            UnifiedSettings.module_name == module
        ).all()
        
        return {s.setting_key: s.setting_value for s in settings}
    
    async def apply_template(self, company_id: str, template_name: str) -> bool:
        """Apply a settings template"""
        template = await self.db.query(SettingsTemplate).filter(
            SettingsTemplate.template_name == template_name
        ).first()
        
        if not template:
            return False
        
        for key, value in template.template_data.items():
            await self.set_setting(
                company_id=company_id,
                module=template.module_name,
                key=key,
                value=value
            )
        
        return True

# Default settings for each module
DEFAULT_SETTINGS = {
    "gl": {
        "fiscal_year_start": "01-01",
        "default_currency": "USD",
        "auto_post_journals": True,
        "require_balanced_entries": True,
        "allow_future_dates": False
    },
    "ap": {
        "auto_generate_voucher_numbers": True,
        "require_purchase_orders": False,
        "default_payment_terms": "Net 30",
        "auto_calculate_tax": True,
        "require_approval_workflow": False
    },
    "ar": {
        "auto_generate_invoice_numbers": True,
        "default_payment_terms": "Net 30",
        "auto_calculate_tax": True,
        "send_payment_reminders": True,
        "aging_periods": [30, 60, 90, 120]
    },
    "tax": {
        "auto_calculate_tax": True,
        "default_tax_rate": 0.0825,
        "require_tax_exemption_certificates": False,
        "auto_file_returns": False
    },
    "payroll": {
        "pay_frequency": "bi-weekly",
        "auto_calculate_taxes": True,
        "require_timesheet_approval": True,
        "auto_generate_paystubs": True
    },
    "inventory": {
        "valuation_method": "FIFO",
        "auto_reorder": False,
        "track_serial_numbers": False,
        "require_receiving": True
    },
    "hrm": {
        "require_manager_approval": True,
        "track_attendance": True,
        "auto_accrue_pto": True,
        "performance_review_frequency": "annual"
    }
}