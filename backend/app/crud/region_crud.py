"""
CRUD operations for regions and countries.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.region import Region, Country
from app.models.currency import Currency


class RegionCRUD:
    """CRUD operations for regions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_regions(self, include_inactive: bool = False) -> List[Region]:
        """Get all regions."""
        query = self.db.query(Region)
        if not include_inactive:
            query = query.filter(Region.status == True)
        return query.order_by(Region.name).all()
    
    def get_region_by_id(self, region_id: UUID) -> Optional[Region]:
        """Get region by ID."""
        return self.db.query(Region).filter(Region.id == region_id).first()
    
    def get_region_by_code(self, code: str) -> Optional[Region]:
        """Get region by code."""
        return self.db.query(Region).filter(Region.code == code.upper()).first()
    
    def create_region(self, region_data: dict) -> Region:
        """Create a new region."""
        region = Region(**region_data)
        self.db.add(region)
        self.db.commit()
        self.db.refresh(region)
        return region
    
    def update_region(self, region_id: UUID, region_data: dict) -> Optional[Region]:
        """Update an existing region."""
        region = self.get_region_by_id(region_id)
        if not region:
            return None
        
        for key, value in region_data.items():
            setattr(region, key, value)
        
        self.db.commit()
        self.db.refresh(region)
        return region
    
    def delete_region(self, region_id: UUID) -> bool:
        """Delete a region."""
        region = self.get_region_by_id(region_id)
        if not region:
            return False
        
        self.db.delete(region)
        self.db.commit()
        return True


class CountryCRUD:
    """CRUD operations for countries."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_countries(self, include_inactive: bool = False) -> List[Country]:
        """Get all countries with region details."""
        query = self.db.query(Country).options(joinedload(Country.region))
        if not include_inactive:
            query = query.filter(Country.status == True)
        return query.order_by(Country.name).all()
    
    def get_countries_by_region(self, region_id: UUID, include_inactive: bool = False) -> List[Country]:
        """Get countries by region."""
        query = self.db.query(Country).filter(Country.region_id == region_id)
        if not include_inactive:
            query = query.filter(Country.status == True)
        return query.order_by(Country.name).all()
    
    def get_country_by_id(self, country_id: UUID) -> Optional[Country]:
        """Get country by ID."""
        return self.db.query(Country).options(joinedload(Country.region)).filter(Country.id == country_id).first()
    
    def get_country_by_code(self, code: str) -> Optional[Country]:
        """Get country by code."""
        return self.db.query(Country).options(joinedload(Country.region)).filter(Country.code == code.upper()).first()
    
    def create_country(self, country_data: dict) -> Country:
        """Create a new country."""
        country = Country(**country_data)
        self.db.add(country)
        self.db.commit()
        self.db.refresh(country)
        return country
    
    def update_country(self, country_id: UUID, country_data: dict) -> Optional[Country]:
        """Update an existing country."""
        country = self.get_country_by_id(country_id)
        if not country:
            return None
        
        for key, value in country_data.items():
            setattr(country, key, value)
        
        self.db.commit()
        self.db.refresh(country)
        return country
    
    def delete_country(self, country_id: UUID) -> bool:
        """Delete a country."""
        country = self.get_country_by_id(country_id)
        if not country:
            return False
        
        self.db.delete(country)
        self.db.commit()
        return True