from typing import List, Dict, Any
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .models import FixedAsset, DepreciationEntry
from .schemas import BulkAssetUpdate, BulkDepreciationRequest

class BulkOperationsService:
    """Service for bulk asset operations"""
    
    async def bulk_update_assets(
        self,
        db: AsyncSession,
        asset_ids: List[int],
        update_data: BulkAssetUpdate
    ) -> Dict[str, Any]:
        """Update multiple assets with same data"""
        
        update_dict = {}
        if update_data.category:
            update_dict['category'] = update_data.category
        if update_data.location:
            update_dict['location'] = update_data.location
        if update_data.status:
            update_dict['status'] = update_data.status
        
        if not update_dict:
            return {"updated": 0, "message": "No update data provided"}
        
        # Execute bulk update
        result = await db.execute(
            update(FixedAsset)
            .where(FixedAsset.id.in_(asset_ids))
            .values(**update_dict)
        )
        
        await db.commit()
        
        return {
            "updated": result.rowcount,
            "message": f"Successfully updated {result.rowcount} assets"
        }
    
    async def bulk_calculate_depreciation(
        self,
        db: AsyncSession,
        request: BulkDepreciationRequest
    ) -> Dict[str, Any]:
        """Calculate depreciation for multiple assets"""
        
        # Get assets by category or all active assets
        query = select(FixedAsset).where(FixedAsset.status == 'active')
        if request.category:
            query = query.where(FixedAsset.category == request.category)
        
        result = await db.execute(query)
        assets = result.scalars().all()
        
        depreciation_entries = []
        total_depreciation = Decimal('0')
        
        for asset in assets:
            # Calculate monthly depreciation
            depreciable_amount = asset.purchase_cost - asset.salvage_value
            monthly_depreciation = depreciable_amount / (asset.useful_life_years * 12)
            
            new_accumulated = asset.accumulated_depreciation + monthly_depreciation
            book_value = asset.purchase_cost - new_accumulated
            
            # Create depreciation entry
            entry = DepreciationEntry(
                asset_id=asset.id,
                period_date=request.period_date,
                depreciation_amount=monthly_depreciation,
                accumulated_depreciation=new_accumulated,
                book_value=book_value
            )
            
            depreciation_entries.append(entry)
            total_depreciation += monthly_depreciation
            
            # Update asset accumulated depreciation
            asset.accumulated_depreciation = new_accumulated
            db.add(asset)
        
        # Bulk insert depreciation entries
        db.add_all(depreciation_entries)
        await db.commit()
        
        return {
            "assets_processed": len(assets),
            "total_depreciation": float(total_depreciation),
            "period_date": request.period_date.isoformat(),
            "entries_created": len(depreciation_entries)
        }
    
    async def bulk_transfer_assets(
        self,
        db: AsyncSession,
        asset_ids: List[int],
        new_location: str,
        transfer_date: date,
        user_id: int
    ) -> Dict[str, Any]:
        """Transfer multiple assets to new location"""
        
        # Update asset locations
        result = await db.execute(
            update(FixedAsset)
            .where(FixedAsset.id.in_(asset_ids))
            .values(location=new_location)
        )
        
        await db.commit()
        
        return {
            "transferred": result.rowcount,
            "new_location": new_location,
            "transfer_date": transfer_date.isoformat(),
            "message": f"Successfully transferred {result.rowcount} assets"
        }