from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

class HRMService:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def get_employees(self) -> List[dict]:
        return [
            {"id": 1, "employee_id": "EMP001", "name": "John Smith", "department": "Finance", "position": "Accountant", "status": "active"},
            {"id": 2, "employee_id": "EMP002", "name": "Sarah Johnson", "department": "HR", "position": "HR Manager", "status": "active"}
        ]
    
    async def get_departments(self) -> List[dict]:
        return [
            {"id": 1, "name": "Finance", "head": "John Smith", "employees": 15},
            {"id": 2, "name": "HR", "head": "Sarah Johnson", "employees": 8}
        ]