from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.settings import CompanySettings, UserSettings, SystemSettings
from app.schemas.settings import CompanySettingsCreate, CompanySettingsUpdate, UserSettingsCreate, UserSettingsUpdate, SystemSettingsCreate, SystemSettingsUpdate

class CompanySettingsCRUD:
    def get(self, db: Session, id: int) -> Optional[CompanySettings]:
        return db.query(CompanySettings).filter(CompanySettings.id == id).first()

    def get_by_company_id(self, db: Session, company_id: int) -> Optional[CompanySettings]:
        return db.query(CompanySettings).filter(CompanySettings.id == company_id).first()

    def create(self, db: Session, obj_in: CompanySettingsCreate) -> CompanySettings:
        db_obj = CompanySettings(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: CompanySettings, obj_in: CompanySettingsUpdate) -> CompanySettings:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_or_create_default(self, db: Session, company_id: int = 1) -> CompanySettings:
        settings = self.get_by_company_id(db, company_id)
        if not settings:
            default_settings = CompanySettingsCreate(
                company_name="Paksa Financial System",
                company_code="PAKSA001",
                base_currency="USD",
                fiscal_year_start="January"
            )
            settings = self.create(db, default_settings)
        return settings

class UserSettingsCRUD:
    def get_user_settings(self, db: Session, user_id: str) -> List[UserSettings]:
        return db.query(UserSettings).filter(UserSettings.user_id == user_id).all()

    def get_user_setting(self, db: Session, user_id: str, setting_key: str) -> Optional[UserSettings]:
        return db.query(UserSettings).filter(
            UserSettings.user_id == user_id,
            UserSettings.setting_key == setting_key
        ).first()

    def create_or_update(self, db: Session, user_id: str, setting_key: str, setting_value: str) -> UserSettings:
        existing = self.get_user_setting(db, user_id, setting_key)
        if existing:
            existing.setting_value = setting_value
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            obj_in = UserSettingsCreate(
                user_id=user_id,
                setting_key=setting_key,
                setting_value=setting_value
            )
            db_obj = UserSettings(**obj_in.dict())
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

    def delete_user_setting(self, db: Session, user_id: str, setting_key: str) -> bool:
        setting = self.get_user_setting(db, user_id, setting_key)
        if setting:
            db.delete(setting)
            db.commit()
            return True
        return False

class SystemSettingsCRUD:
    def get_all(self, db: Session) -> List[SystemSettings]:
        return db.query(SystemSettings).all()

    def get_by_key(self, db: Session, setting_key: str) -> Optional[SystemSettings]:
        return db.query(SystemSettings).filter(SystemSettings.setting_key == setting_key).first()

    def create_or_update(self, db: Session, setting_key: str, setting_value: str, description: str = None) -> SystemSettings:
        existing = self.get_by_key(db, setting_key)
        if existing:
            existing.setting_value = setting_value
            if description:
                existing.description = description
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            obj_in = SystemSettingsCreate(
                setting_key=setting_key,
                setting_value=setting_value,
                description=description
            )
            db_obj = SystemSettings(**obj_in.dict())
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

    def delete_by_key(self, db: Session, setting_key: str) -> bool:
        setting = self.get_by_key(db, setting_key)
        if setting:
            db.delete(setting)
            db.commit()
            return True
        return False

company_settings_crud = CompanySettingsCRUD()
user_settings_crud = UserSettingsCRUD()
system_settings_crud = SystemSettingsCRUD()