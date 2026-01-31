from typing import List

from sqlalchemy.ext.asyncio import AsyncSession


class InventoryService:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def get_items(self) -> List[dict]:
        return [
            {"id": 1, "sku": "ITEM001", "name": "Office Chair", "quantity": 50, "unit_cost": 150.00, "location": "Warehouse A"},
            {"id": 2, "sku": "ITEM002", "name": "Laptop", "quantity": 25, "unit_cost": 1200.00, "location": "IT Storage"}
        ]
    
    async def get_locations(self) -> List[dict]:
        return [
            {"id": 1, "name": "Warehouse A", "items": 150, "value": 75000.00},
            {"id": 2, "name": "IT Storage", "items": 45, "value": 125000.00}
        ]