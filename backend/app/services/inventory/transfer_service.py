"""
Multi-location transfer service.
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional

from decimal import Decimal
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.inventory.item import InventoryItem, InventoryLocation
from app.models.inventory.transaction import InventoryTransaction
from app.models.inventory.transfer import LocationTransfer, TransferItem




class TransferService:
    """Multi-location transfer service."""
    
    async def create_transfer(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        transfer_data: Dict[str, Any]
    ) -> LocationTransfer:
        """Create Transfer."""
        """Create a new location transfer."""
        transfer_number = await self._generate_transfer_number(db, tenant_id)
        
        transfer = LocationTransfer(
            tenant_id=tenant_id,
            transfer_number=transfer_number,
            **transfer_data
        )
        db.add(transfer)
        await db.commit()
        await db.refresh(transfer)
        return transfer
    
    async def approve_transfer(
        self,
        db: AsyncSession,
        transfer_id: UUID,
        approved_by: UUID
    ) -> LocationTransfer:
        """Approve Transfer."""
        """Approve transfer request."""
        result = await db.execute(
            select(LocationTransfer).where(LocationTransfer.id == transfer_id)
        )
        transfer = result.scalar_one_or_none()
        
        if not transfer:
            raise ValueError("Transfer not found")
        
        transfer.status = "approved"
        transfer.approved_by = approved_by
        transfer.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(transfer)
        return transfer
    
    async def ship_transfer(
        self,
        db: AsyncSession,
        transfer_id: UUID,
        shipping_data: Dict[str, Any]
    ) -> LocationTransfer:
        """Ship Transfer."""
        """Ship transfer items."""
        result = await db.execute(
            select(LocationTransfer).where(LocationTransfer.id == transfer_id)
        )
        transfer = result.scalar_one_or_none()
        
        if not transfer:
            raise ValueError("Transfer not found")
        
        transfer.status = "in_transit"
        transfer.shipped_date = shipping_data.get("shipped_date", date.today())
        transfer.tracking_number = shipping_data.get("tracking_number")
        transfer.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(transfer)
        return transfer
    
    async def get_transfer_status(
        self,
        db: AsyncSession,
        transfer_id: UUID
    ) -> Dict[str, Any]:
        """Get Transfer Status."""
        """Get detailed transfer status."""
        result = await db.execute(
            select(LocationTransfer).where(LocationTransfer.id == transfer_id)
        )
        transfer = result.scalar_one_or_none()
        
        if not transfer:
            raise ValueError("Transfer not found")
        
        return {
            "transfer_id": str(transfer.id),
            "transfer_number": transfer.transfer_number,
            "status": transfer.status,
            "from_location": str(transfer.from_location_id),
            "to_location": str(transfer.to_location_id),
            "transfer_date": transfer.transfer_date.isoformat() if transfer.transfer_date else None,
            "shipped_date": transfer.shipped_date.isoformat() if transfer.shipped_date else None,
            "tracking_number": transfer.tracking_number
        }
    
    async def _generate_transfer_number(self, db: AsyncSession, tenant_id: UUID) -> str:
        """Generate Transfer Number."""
        """Generate unique transfer number."""
        today = date.today()
        prefix = f"TRF-{today.strftime('%Y%m%d')}"
        
        result = await db.execute(
            select(func.count(LocationTransfer.id))
            .where(
                and_(
                    LocationTransfer.tenant_id == tenant_id,
                    LocationTransfer.transfer_number.like(f"{prefix}%")
                )
            )
        )
        count = result.scalar() or 0
        
        return f"{prefix}-{count + 1:04d}"