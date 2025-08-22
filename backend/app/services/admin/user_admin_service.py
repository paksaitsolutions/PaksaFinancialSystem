"""
User administration service.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Boolean, JSON
from app.models.base import BaseModel, GUID


class UserProvision(BaseModel):
    """User provisioning records."""
    __tablename__ = "user_provisions"
    
    user_id = Column(GUID(), nullable=False, index=True)
    company_id = Column(GUID(), nullable=False, index=True)
    provisioned_by = Column(GUID(), nullable=False)
    provision_type = Column(String(50), nullable=False, default="manual")
    status = Column(String(20), nullable=False, default="active")
    metadata = Column(JSON, nullable=True)


class SystemSetting(BaseModel):
    """System settings."""
    __tablename__ = "system_settings"
    
    key = Column(String(100), nullable=False, unique=True)
    value = Column(String(1000), nullable=True)
    data_type = Column(String(20), nullable=False, default="string")
    description = Column(String(500), nullable=True)
    is_public = Column(Boolean, nullable=False, default=False)


class UserAdminService:
    """Service for user administration."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def provision_user(
        self,
        user_id: UUID,
        company_id: UUID,
        provisioned_by: UUID,
        provision_type: str = "manual"
    ) -> UserProvision:
        """Provision a user for a company."""
        provision = UserProvision(
            user_id=user_id,
            company_id=company_id,
            provisioned_by=provisioned_by,
            provision_type=provision_type
        )
        
        self.db.add(provision)
        self.db.commit()
        self.db.refresh(provision)
        
        return provision
    
    def deactivate_user(self, user_id: UUID, company_id: UUID) -> bool:
        """Deactivate a user."""
        provision = self.db.query(UserProvision).filter(
            UserProvision.user_id == user_id,
            UserProvision.company_id == company_id
        ).first()
        
        if provision:
            provision.status = "inactive"
            self.db.commit()
            return True
        
        return False
    
    def set_system_setting(self, key: str, value: str) -> SystemSetting:
        """Set system setting."""
        setting = self.db.query(SystemSetting).filter(SystemSetting.key == key).first()
        
        if setting:
            setting.value = value
        else:
            setting = SystemSetting(key=key, value=value)
            self.db.add(setting)
        
        self.db.commit()
        self.db.refresh(setting)
        
        return setting
    
    def get_system_setting(self, key: str) -> Optional[SystemSetting]:
        """Get system setting."""
        return self.db.query(SystemSetting).filter(SystemSetting.key == key).first()