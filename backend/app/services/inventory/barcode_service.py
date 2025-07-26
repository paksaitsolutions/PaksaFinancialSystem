"""
Barcode scanning and management service.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.inventory.item import InventoryItem
from app.models.inventory.transfer import BarcodeMapping

class BarcodeService:
    """Barcode scanning and management service."""
    
    async def create_barcode_mapping(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        item_id: UUID,
        barcode: str,
        barcode_type: str = "UPC",
        is_primary: bool = False
    ) -> BarcodeMapping:
        """Create barcode mapping for item."""
        # Check if barcode already exists
        existing_result = await db.execute(
            select(BarcodeMapping).where(
                and_(
                    BarcodeMapping.tenant_id == tenant_id,
                    BarcodeMapping.barcode == barcode
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise ValueError("Barcode already exists")
        
        # If setting as primary, unset other primary barcodes for this item
        if is_primary:
            await self._unset_primary_barcodes(db, item_id)
        
        mapping = BarcodeMapping(
            tenant_id=tenant_id,
            item_id=item_id,
            barcode=barcode,
            barcode_type=barcode_type,
            is_primary=is_primary
        )
        db.add(mapping)
        await db.commit()
        await db.refresh(mapping)
        return mapping
    
    async def scan_barcode(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        barcode: str
    ) -> Dict[str, Any]:
        """Scan barcode and return item information."""
        # First check barcode mappings
        mapping_result = await db.execute(
            select(BarcodeMapping).where(
                and_(
                    BarcodeMapping.tenant_id == tenant_id,
                    BarcodeMapping.barcode == barcode,
                    BarcodeMapping.is_active == True
                )
            )
        )
        mapping = mapping_result.scalar_one_or_none()
        
        if mapping:
            # Get item details
            item_result = await db.execute(
                select(InventoryItem).where(InventoryItem.id == mapping.item_id)
            )
            item = item_result.scalar_one_or_none()
            
            if item:
                return {
                    "found": True,
                    "item_id": str(item.id),
                    "sku": item.sku,
                    "name": item.name,
                    "barcode": barcode,
                    "barcode_type": mapping.barcode_type,
                    "quantity_on_hand": float(item.quantity_on_hand),
                    "quantity_available": float(item.quantity_available),
                    "unit_cost": float(item.unit_cost),
                    "location_id": str(item.default_location_id) if item.default_location_id else None
                }
        
        # Check if barcode matches item's primary barcode field
        item_result = await db.execute(
            select(InventoryItem).where(InventoryItem.barcode == barcode)
        )
        item = item_result.scalar_one_or_none()
        
        if item:
            return {
                "found": True,
                "item_id": str(item.id),
                "sku": item.sku,
                "name": item.name,
                "barcode": barcode,
                "barcode_type": "Primary",
                "quantity_on_hand": float(item.quantity_on_hand),
                "quantity_available": float(item.quantity_available),
                "unit_cost": float(item.unit_cost),
                "location_id": str(item.default_location_id) if item.default_location_id else None
            }
        
        return {
            "found": False,
            "barcode": barcode,
            "message": "Item not found for this barcode"
        }
    
    async def get_item_barcodes(
        self,
        db: AsyncSession,
        item_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all barcodes for an item."""
        result = await db.execute(
            select(BarcodeMapping).where(
                and_(
                    BarcodeMapping.item_id == item_id,
                    BarcodeMapping.is_active == True
                )
            )
        )
        mappings = result.scalars().all()
        
        barcodes = []
        for mapping in mappings:
            barcodes.append({
                "id": str(mapping.id),
                "barcode": mapping.barcode,
                "barcode_type": mapping.barcode_type,
                "is_primary": mapping.is_primary,
                "created_at": mapping.created_at.isoformat()
            })
        
        return barcodes
    
    async def update_item_quantity_by_barcode(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        barcode: str,
        quantity_change: float,
        transaction_type: str = "adjustment",
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update item quantity using barcode scan."""
        scan_result = await self.scan_barcode(db, tenant_id, barcode)
        
        if not scan_result["found"]:
            raise ValueError("Item not found for barcode")
        
        item_id = UUID(scan_result["item_id"])
        
        # Get item
        item_result = await db.execute(
            select(InventoryItem).where(InventoryItem.id == item_id)
        )
        item = item_result.scalar_one_or_none()
        
        if not item:
            raise ValueError("Item not found")
        
        # Update quantities
        old_quantity = item.quantity_on_hand
        item.quantity_on_hand += quantity_change
        item.quantity_available += quantity_change
        
        await db.commit()
        await db.refresh(item)
        
        return {
            "item_id": str(item.id),
            "sku": item.sku,
            "name": item.name,
            "barcode": barcode,
            "old_quantity": float(old_quantity),
            "quantity_change": quantity_change,
            "new_quantity": float(item.quantity_on_hand),
            "transaction_type": transaction_type,
            "notes": notes
        }
    
    async def generate_barcode_report(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        barcode_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate barcode usage report."""
        filters = [BarcodeMapping.tenant_id == tenant_id, BarcodeMapping.is_active == True]
        
        if barcode_type:
            filters.append(BarcodeMapping.barcode_type == barcode_type)
        
        result = await db.execute(
            select(BarcodeMapping).where(and_(*filters))
        )
        mappings = result.scalars().all()
        
        # Count by type
        type_counts = {}
        for mapping in mappings:
            type_counts[mapping.barcode_type] = type_counts.get(mapping.barcode_type, 0) + 1
        
        return {
            "total_barcodes": len(mappings),
            "barcode_types": type_counts,
            "primary_barcodes": len([m for m in mappings if m.is_primary]),
            "secondary_barcodes": len([m for m in mappings if not m.is_primary])
        }
    
    async def _unset_primary_barcodes(self, db: AsyncSession, item_id: UUID) -> None:
        """Unset primary flag for all barcodes of an item."""
        result = await db.execute(
            select(BarcodeMapping).where(
                and_(
                    BarcodeMapping.item_id == item_id,
                    BarcodeMapping.is_primary == True
                )
            )
        )
        primary_mappings = result.scalars().all()
        
        for mapping in primary_mappings:
            mapping.is_primary = False