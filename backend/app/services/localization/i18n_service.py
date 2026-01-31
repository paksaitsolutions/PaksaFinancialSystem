"""
Internationalization service.
"""
from typing import Dict, Any, List, Optional

from sqlalchemy import Column, String, Text, Boolean, JSON
from sqlalchemy.orm import Session

from app.models.base import BaseModel



class Language(BaseModel):
    """Supported languages."""
    __tablename__ = "languages"
    
    code = Column(String(10), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    native_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)


class Translation(BaseModel):
    """Translation strings."""
    __tablename__ = "translations"
    
    key = Column(String(200), nullable=False)
    language_code = Column(String(10), nullable=False)
    value = Column(Text, nullable=False)


class RegionalSetting(BaseModel):
    """Regional settings."""
    __tablename__ = "regional_settings"
    
    region_code = Column(String(10), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    currency_code = Column(String(3), nullable=False)
    timezone = Column(String(50), nullable=False)
    date_format = Column(String(20), nullable=False, default="YYYY-MM-DD")


class I18nService:
    """Service for internationalization."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def get_translation(self, key: str, language_code: str = "en") -> str:
        """Get Translation."""
        """Get translation for a key."""
        translation = self.db.query(Translation).filter(
            Translation.key == key,
            Translation.language_code == language_code
        ).first()
        
        return translation.value if translation else key
    
    def set_translation(self, key: str, language_code: str, value: str) -> Translation:
        """Set Translation."""
        """Set translation for a key."""
        translation = self.db.query(Translation).filter(
            Translation.key == key,
            Translation.language_code == language_code
        ).first()
        
        if translation:
            translation.value = value
        else:
            translation = Translation(
                key=key,
                language_code=language_code,
                value=value
            )
            self.db.add(translation)
        
        self.db.commit()
        self.db.refresh(translation)
        
        return translation
    
    def get_supported_languages(self) -> List[Language]:
        """Get Supported Languages."""
        """Get supported languages."""
        return self.db.query(Language).filter(Language.is_active == True).all()
    
    def format_currency(self, amount: float, currency_code: str) -> str:
        """Format Currency."""
        """Format currency amount."""
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£"
        }
        
        symbol = currency_symbols.get(currency_code, currency_code)
        return f"{symbol}{amount:,.2f}"