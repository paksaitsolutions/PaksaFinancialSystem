"""
Schemas for inventory reporting and analytics.
"""
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class InventoryValueReport(BaseModel):
    """Schema for inventory valuation report."""
    item_id: str
    sku: str
    name: str
    category: Optional[str] = None
    quantity_on_hand: Decimal
    unit_cost: Decimal
    total_value: Decimal

class StockLevelReport(BaseModel):
    """Schema for stock level report."""
    item_id: str
    sku: str
    name: str
    quantity_on_hand: Decimal
    quantity_available: Decimal
    quantity_committed: Decimal
    reorder_point: Decimal
    reorder_quantity: Decimal
    status: str

class TransactionSummary(BaseModel):
    """Schema for transaction summary."""
    transaction_type: str
    total_quantity: Decimal
    total_value: Decimal
    transaction_count: int

class InventoryAnalytics(BaseModel):
    """Schema for inventory analytics dashboard."""
    total_items: int
    total_value: Decimal
    low_stock_items: int
    out_of_stock_items: int
    transaction_summary: List[TransactionSummary]
    top_items_by_value: List[InventoryValueReport]
    recent_transactions: List[Dict[str, Any]]