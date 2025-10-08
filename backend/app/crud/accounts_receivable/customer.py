"""
CRUD operations for Customer model
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, text
from sqlalchemy.orm import selectinload

from app.models.accounts_receivable.customer import Customer, CustomerContact

class CustomerCRUD:
    """CRUD operations for customers"""
    
    async def get_customers(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Customer]:
        """Get customers with filtering"""
        query = select(Customer).options(selectinload(Customer.contacts))
        
        if status:
            query = query.where(Customer.status == status)
            
        if search:
            query = query.where(
                or_(
                    Customer.name.ilike(f"%{search}%"),
                    Customer.code.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%")
                )
            )
        
        query = query.offset(skip).limit(limit).order_by(Customer.name)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_customers(
        self, 
        db: AsyncSession,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> int:
        """Count customers with filtering"""
        query = select(func.count(Customer.id))
        
        if status:
            query = query.where(Customer.status == status)
            
        if search:
            query = query.where(
                or_(
                    Customer.name.ilike(f"%{search}%"),
                    Customer.code.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%")
                )
            )
        
        result = await db.execute(query)
        return result.scalar()
    
    async def get_customer(self, db: AsyncSession, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        query = select(Customer).options(selectinload(Customer.contacts)).where(Customer.id == customer_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_customer_segmentation(self, db: AsyncSession):
        """Get customer segmentation analysis"""
        # Mock segmentation - replace with actual analysis
        return [
            {
                "id": 1,
                "name": "Champions",
                "count": 45,
                "value": 850000,
                "percentage": 35,
                "color": "#10B981",
                "criteria": "High value, frequent purchases, low risk"
            },
            {
                "id": 2,
                "name": "Loyal Customers",
                "count": 78,
                "value": 650000,
                "percentage": 28,
                "color": "#3B82F6",
                "criteria": "Regular purchases, good payment history"
            },
            {
                "id": 3,
                "name": "Potential Loyalists",
                "count": 52,
                "value": 420000,
                "percentage": 22,
                "color": "#F59E0B",
                "criteria": "Recent customers with growth potential"
            },
            {
                "id": 4,
                "name": "At Risk",
                "count": 23,
                "value": 180000,
                "percentage": 15,
                "color": "#EF4444",
                "criteria": "Declining purchases, payment delays"
            }
        ]