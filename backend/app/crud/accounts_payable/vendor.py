"""
CRUD operations for Vendor model
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models import Vendor, VendorContact
from app.schemas.accounts_payable.vendor import VendorCreate, VendorUpdate

class VendorCRUD:
    """CRUD operations for vendors"""
    
    async def get_vendors(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Vendor]:
        """Get vendors with filtering"""
        query = select(Vendor).options(selectinload(Vendor.contacts))
        
        if status:
            query = query.where(Vendor.status == status)
            
        if search:
            query = query.where(
                or_(
                    Vendor.name.ilike(f"%{search}%"),
                    Vendor.code.ilike(f"%{search}%"),
                    Vendor.email.ilike(f"%{search}%")
                )
            )
        
        query = query.offset(skip).limit(limit).order_by(Vendor.name)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_vendors(
        self, 
        db: AsyncSession,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> int:
        """Count vendors with filtering"""
        query = select(func.count(Vendor.id))
        
        if status:
            query = query.where(Vendor.status == status)
            
        if search:
            query = query.where(
                or_(
                    Vendor.name.ilike(f"%{search}%"),
                    Vendor.code.ilike(f"%{search}%"),
                    Vendor.email.ilike(f"%{search}%")
                )
            )
        
        result = await db.execute(query)
        return result.scalar()
    
    async def get_vendor(self, db: AsyncSession, vendor_id: str) -> Optional[Vendor]:
        """Get vendor by ID"""
        query = select(Vendor).options(selectinload(Vendor.contacts)).where(Vendor.id == vendor_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_vendor(self, db: AsyncSession, vendor: VendorCreate) -> Vendor:
        """Create new vendor"""
        db_vendor = Vendor(**vendor.dict())
        db.add(db_vendor)
        await db.flush()
        await db.refresh(db_vendor)
        return db_vendor
    
    async def update_vendor(self, db: AsyncSession, vendor_id: str, vendor: VendorUpdate) -> Optional[Vendor]:
        """Update vendor"""
        db_vendor = await self.get_vendor(db, vendor_id)
        if not db_vendor:
            return None
            
        update_data = vendor.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vendor, field, value)
        
        await db.flush()
        await db.refresh(db_vendor)
        return db_vendor
    
    async def delete_vendor(self, db: AsyncSession, vendor_id: str) -> bool:
        """Delete vendor"""
        db_vendor = await self.get_vendor(db, vendor_id)
        if not db_vendor:
            return False
            
        await db.delete(db_vendor)
        await db.flush()
        return True

# Create instance for use in endpoints
vendor_crud = VendorCRUD()