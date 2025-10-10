"""
Region and Country models for geographical management.
"""
from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel, GUID


class RegionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Region(BaseModel):
    """
    Represents a geographical region (continent/area).
    """
    __tablename__ = "regions"
    
    # Region code (e.g., NA, EU, AS, AF, SA, OC, AN)
    code = Column(String(10), unique=True, index=True, nullable=False)
    
    # Region name (e.g., North America, Europe, Asia)
    name = Column(String(100), nullable=False)
    
    # Status (active/inactive)
    status = Column(Boolean, default=True, nullable=False)
    
    # Countries in this region
    countries = relationship("Country", back_populates="region")
    
    def __repr__(self) -> str:
        return f"<Region(id={self.id}, code='{self.code}', name='{self.name}')>"


class Country(BaseModel):
    """
    Represents a country with its details.
    """
    __tablename__ = "countries"
    
    # ISO 3166-1 alpha-2 country code (e.g., US, GB, DE)
    code = Column(String(2), unique=True, index=True, nullable=False)
    
    # ISO 3166-1 alpha-3 country code (e.g., USA, GBR, DEU)
    code_alpha3 = Column(String(3), unique=True, index=True, nullable=True)
    
    # Country name (e.g., United States, United Kingdom, Germany)
    name = Column(String(100), nullable=False)
    
    # Official country name
    official_name = Column(String(200), nullable=True)
    
    # Region this country belongs to
    region_id = Column(GUID(), ForeignKey("regions.id"), nullable=True)
    
    # Default currency for this country
    default_currency_id = Column(GUID(), ForeignKey("currencies.id"), nullable=True)
    
    # Phone country code (e.g., +1, +44, +49)
    phone_code = Column(String(10), nullable=True)
    
    # Status (active/inactive)
    status = Column(Boolean, default=True, nullable=False)
    
    # Additional information
    capital = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    # Relationships
    region = relationship("Region", back_populates="countries")
    default_currency = relationship("Currency")
    
    def __repr__(self) -> str:
        return f"<Country(id={self.id}, code='{self.code}', name='{self.name}')>"