from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from ..models import Vendor

class VendorService:
    """Service for vendor management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_vendor(self, vendor_data: dict):
        """Create a new vendor"""
        vendor = Vendor(
            name=vendor_data.get("name"),
            contact_person=vendor_data.get("contact_person"),
            email=vendor_data.get("email"),
            phone=vendor_data.get("phone"),
            address=vendor_data.get("address"),
            tax_id=vendor_data.get("tax_id"),
            default_currency=vendor_data.get("default_currency", "USD"),
            is_active=vendor_data.get("is_active", True)
        )
        
        self.db.add(vendor)
        await self.db.commit()
        await self.db.refresh(vendor)
        return vendor
    
    async def get_vendor_by_id(self, vendor_id):
        """Get vendor by ID"""
        result = await self.db.execute(
            select(Vendor).where(Vendor.id == vendor_id)
        )
        return result.scalar_one_or_none()
    
    async def get_vendors(self, skip: int = 0, limit: int = 100):
        """Get list of vendors"""
        result = await self.db.execute(
            select(Vendor).offset(skip).limit(limit).order_by(Vendor.name)
        )
        return result.scalars().all()
    
    async def update_vendor(self, vendor_id, vendor_data: dict):
        """Update vendor"""
        vendor = await self.get_vendor_by_id(vendor_id)
        if not vendor:
            return None
            
        for field, value in vendor_data.items():
            if hasattr(vendor, field) and value is not None:
                setattr(vendor, field, value)
                
        await self.db.commit()
        await self.db.refresh(vendor)
        return vendor
    
    async def delete_vendor(self, vendor_id):
        """Delete vendor"""
        vendor = await self.get_vendor_by_id(vendor_id)
        if not vendor:
            return False
            
        await self.db.delete(vendor)
        await self.db.commit()
        return True