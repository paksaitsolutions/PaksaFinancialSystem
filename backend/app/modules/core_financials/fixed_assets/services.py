from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.crud.base import CRUDBase
from .models import FixedAsset, DepreciationEntry, MaintenanceRecord, AssetCategory, AssetStatus, DepreciationMethod
from .schemas import (
    FixedAssetCreate, FixedAssetUpdate, DepreciationEntryCreate, 
    MaintenanceRecordCreate, MaintenanceRecordUpdate, AssetCategoryCreate,
    AssetDisposalRequest, AssetReport
)

class FixedAssetService(CRUDBase[FixedAsset, FixedAssetCreate, FixedAssetUpdate]):
    def __init__(self):
        super().__init__(FixedAsset)
    
    async def get_by_asset_number(self, db: AsyncSession, asset_number: str) -> Optional[FixedAsset]:
        result = await db.execute(select(FixedAsset).where(FixedAsset.asset_number == asset_number))
        return result.scalar_one_or_none()
    
    async def get_assets_by_category(self, db: AsyncSession, category: str) -> List[FixedAsset]:
        result = await db.execute(
            select(FixedAsset).where(
                and_(FixedAsset.category == category, FixedAsset.is_active == True)
            )
        )
        return result.scalars().all()
    
    async def get_assets_by_status(self, db: AsyncSession, status: AssetStatus) -> List[FixedAsset]:
        result = await db.execute(
            select(FixedAsset).where(
                and_(FixedAsset.status == status, FixedAsset.is_active == True)
            )
        )
        return result.scalars().all()
    
    async def calculate_depreciation(self, asset: FixedAsset, period_date: date) -> Decimal:
        """Calculate depreciation for a specific period"""
        if asset.status != AssetStatus.ACTIVE:
            return Decimal('0')
        
        months_since_purchase = (period_date.year - asset.purchase_date.year) * 12 + \
                               (period_date.month - asset.purchase_date.month)
        
        if months_since_purchase <= 0:
            return Decimal('0')
        
        depreciable_amount = asset.purchase_cost - asset.salvage_value
        
        if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            monthly_depreciation = depreciable_amount / (asset.useful_life_years * 12)
            return monthly_depreciation
        
        elif asset.depreciation_method == DepreciationMethod.DECLINING_BALANCE:
            # Double declining balance method
            rate = Decimal('2') / asset.useful_life_years
            current_book_value = asset.purchase_cost - asset.accumulated_depreciation
            annual_depreciation = current_book_value * rate
            monthly_depreciation = annual_depreciation / 12
            
            # Ensure we don't depreciate below salvage value
            remaining_depreciable = current_book_value - asset.salvage_value
            return min(monthly_depreciation, remaining_depreciable)
        
        return Decimal('0')
    
    async def create_depreciation_entry(
        self, 
        db: AsyncSession, 
        asset_id: int, 
        period_date: date
    ) -> Optional[DepreciationEntry]:
        """Create a depreciation entry for an asset"""
        asset = await self.get(db, asset_id)
        if not asset:
            return None
        
        depreciation_amount = await self.calculate_depreciation(asset, period_date)
        if depreciation_amount <= 0:
            return None
        
        new_accumulated = asset.accumulated_depreciation + depreciation_amount
        book_value = asset.purchase_cost - new_accumulated
        
        # Create depreciation entry
        entry = DepreciationEntry(
            asset_id=asset_id,
            period_date=period_date,
            depreciation_amount=depreciation_amount,
            accumulated_depreciation=new_accumulated,
            book_value=book_value
        )
        
        db.add(entry)
        
        # Update asset's accumulated depreciation
        asset.accumulated_depreciation = new_accumulated
        db.add(asset)
        
        await db.commit()
        await db.refresh(entry)
        return entry
    
    async def dispose_asset(
        self, 
        db: AsyncSession, 
        asset_id: int, 
        disposal_request: AssetDisposalRequest
    ) -> Optional[FixedAsset]:
        """Dispose of an asset"""
        asset = await self.get(db, asset_id)
        if not asset:
            return None
        
        asset.status = AssetStatus.DISPOSED
        asset.disposal_date = disposal_request.disposal_date
        asset.disposal_amount = disposal_request.disposal_amount
        asset.disposal_reason = disposal_request.disposal_reason
        
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        return asset
    
    async def get_asset_report(self, db: AsyncSession) -> AssetReport:
        """Generate asset summary report"""
        # Get total counts and values
        result = await db.execute(
            select(
                func.count(FixedAsset.id).label('total_assets'),
                func.sum(FixedAsset.purchase_cost).label('total_cost'),
                func.sum(FixedAsset.accumulated_depreciation).label('total_accumulated_depreciation')
            ).where(FixedAsset.is_active == True)
        )
        
        totals = result.first()
        total_cost = totals.total_cost or Decimal('0')
        total_accumulated = totals.total_accumulated_depreciation or Decimal('0')
        
        # Assets by category
        category_result = await db.execute(
            select(
                FixedAsset.category,
                func.count(FixedAsset.id).label('count'),
                func.sum(FixedAsset.purchase_cost).label('total_cost')
            ).where(FixedAsset.is_active == True)
            .group_by(FixedAsset.category)
        )
        
        assets_by_category = [
            {
                'category': row.category,
                'count': row.count,
                'total_cost': float(row.total_cost or 0)
            }
            for row in category_result
        ]
        
        # Assets by status
        status_result = await db.execute(
            select(
                FixedAsset.status,
                func.count(FixedAsset.id).label('count')
            ).where(FixedAsset.is_active == True)
            .group_by(FixedAsset.status)
        )
        
        assets_by_status = [
            {
                'status': row.status.value,
                'count': row.count
            }
            for row in status_result
        ]
        
        return AssetReport(
            total_assets=totals.total_assets or 0,
            total_cost=total_cost,
            total_accumulated_depreciation=total_accumulated,
            total_book_value=total_cost - total_accumulated,
            assets_by_category=assets_by_category,
            assets_by_status=assets_by_status
        )

class MaintenanceService(CRUDBase[MaintenanceRecord, MaintenanceRecordCreate, MaintenanceRecordUpdate]):
    def __init__(self):
        super().__init__(MaintenanceRecord)
    
    async def get_by_asset(self, db: AsyncSession, asset_id: int) -> List[MaintenanceRecord]:
        result = await db.execute(
            select(MaintenanceRecord)
            .where(MaintenanceRecord.asset_id == asset_id)
            .order_by(MaintenanceRecord.scheduled_date.desc())
        )
        return result.scalars().all()
    
    async def get_upcoming_maintenance(self, db: AsyncSession, days_ahead: int = 30) -> List[MaintenanceRecord]:
        future_date = date.today() + relativedelta(days=days_ahead)
        result = await db.execute(
            select(MaintenanceRecord)
            .where(
                and_(
                    MaintenanceRecord.scheduled_date <= future_date,
                    MaintenanceRecord.scheduled_date >= date.today(),
                    MaintenanceRecord.status == 'scheduled'
                )
            )
            .order_by(MaintenanceRecord.scheduled_date)
        )
        return result.scalars().all()

class AssetCategoryService(CRUDBase[AssetCategory, AssetCategoryCreate, None]):
    def __init__(self):
        super().__init__(AssetCategory)
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[AssetCategory]:
        result = await db.execute(select(AssetCategory).where(AssetCategory.name == name))
        return result.scalar_one_or_none()