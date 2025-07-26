from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

class CustomerService:
    """Service for customer management operations"""
    
    async def create_customer(self, db: AsyncSession, customer_data: dict):
        """Create a new customer"""
        customer = {
            "id": 1,
            "customer_id": f"CUST-{datetime.now().strftime('%Y%m%d')}-001",
            "name": customer_data.get("name"),
            "email": customer_data.get("email"),
            "status": "active",
            "credit_limit": customer_data.get("credit_limit", 10000.00),
            "created_at": datetime.now().isoformat()
        }
        return customer
    
    async def get_customers(self, db: AsyncSession, skip: int = 0, limit: int = 100, status: Optional[str] = None):
        """Get customers with filtering"""
        customers = [
            {
                "id": 1,
                "customer_id": "CUST-20240101-001",
                "name": "ABC Corporation",
                "email": "billing@abccorp.com",
                "status": "active",
                "credit_limit": 50000.00,
                "current_balance": 15000.00
            }
        ]
        
        if status:
            customers = [c for c in customers if c["status"] == status]
            
        return customers[skip:skip+limit]
    
    async def get_customer_credit(self, db: AsyncSession, customer_id: int):
        """Get customer credit information"""
        return {
            "customer_id": customer_id,
            "credit_limit": 50000.00,
            "current_balance": 15000.00,
            "available_credit": 35000.00,
            "credit_rating": "A"
        }