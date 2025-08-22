from typing import Optional, List
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from .models import FixedAsset, AssetStatus, DepreciationEntry
from .schemas import AssetDisposalRequest, AssetDisposalResult

class AssetDisposalService:
    """Service for handling asset disposal workflows"""
    
    async def initiate_disposal(
        self, 
        db: AsyncSession, 
        asset_id: int, 
        disposal_request: AssetDisposalRequest,
        user_id: int
    ) -> AssetDisposalResult:
        """Initiate asset disposal with gain/loss calculation"""
        
        # Get asset
        result = await db.execute(select(FixedAsset).where(FixedAsset.id == asset_id))
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise ValueError("Asset not found")
        
        if asset.status != AssetStatus.ACTIVE:
            raise ValueError("Only active assets can be disposed")
        
        # Calculate current book value
        book_value = asset.purchase_cost - asset.accumulated_depreciation
        
        # Calculate gain/loss on disposal
        gain_loss = disposal_request.disposal_amount - book_value
        
        # Update asset status
        asset.status = AssetStatus.DISPOSED
        asset.disposal_date = disposal_request.disposal_date
        asset.disposal_amount = disposal_request.disposal_amount
        asset.disposal_reason = disposal_request.disposal_reason
        
        db.add(asset)
        await db.commit()
        
        return AssetDisposalResult(
            asset_id=asset_id,
            book_value=book_value,
            disposal_amount=disposal_request.disposal_amount,
            gain_loss=gain_loss,
            disposal_date=disposal_request.disposal_date,
            status="completed"
        )
    
    async def bulk_dispose_assets(
        self,
        db: AsyncSession,
        asset_ids: List[int],
        disposal_request: AssetDisposalRequest,
        user_id: int
    ) -> List[AssetDisposalResult]:
        """Dispose multiple assets in bulk"""
        
        results = []
        for asset_id in asset_ids:
            try:
                result = await self.initiate_disposal(db, asset_id, disposal_request, user_id)
                results.append(result)
            except Exception as e:
                results.append(AssetDisposalResult(
                    asset_id=asset_id,
                    status="failed",
                    error=str(e)
                ))
        
        return results