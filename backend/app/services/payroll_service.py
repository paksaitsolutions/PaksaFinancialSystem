from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

class PayrollService:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def get_payroll_runs(self) -> List[dict]:
        return [
            {"id": 1, "period": "2024-01", "employees": 25, "gross_pay": 125000.00, "net_pay": 95000.00, "status": "completed"},
            {"id": 2, "period": "2024-02", "employees": 25, "gross_pay": 128000.00, "net_pay": 97000.00, "status": "processing"}
        ]
    
    async def get_employee_payslips(self) -> List[dict]:
        return [
            {"id": 1, "employee": "John Smith", "period": "2024-01", "gross": 5000.00, "net": 3800.00, "status": "paid"},
            {"id": 2, "employee": "Sarah Johnson", "period": "2024-01", "gross": 6000.00, "net": 4500.00, "status": "paid"}
        ]