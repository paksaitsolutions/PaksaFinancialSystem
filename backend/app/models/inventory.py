# Import all unified models from core_models to eliminate duplicates
from app.models.core_models import (
    InventoryItem,
    InventoryCategory,
    PurchaseOrder,
    PurchaseOrderLineItem,
    FixedAsset,
    AssetDepreciation
)

# Create missing model aliases for compatibility
class InventoryLocation:
    """Placeholder for inventory location - use InventoryItem.location field"""
    pass

class AssetMaintenance:
    """Placeholder for asset maintenance - integrated with AP module"""
    pass

# All inventory and fixed asset models are now unified in core_models.py
# This file serves as a compatibility layer for existing imports