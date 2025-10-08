"""
CRUD operations for AR Payment model
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.accounts_receivable.ar_invoice import ARPayment

class ARPaymentCRUD:
    """CRUD operations for AR payments"""
    
    async def get_payments(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> List[ARPayment]:
        """Get payments with filtering"""
        query = select(ARPayment).options(selectinload(ARPayment.customer))
        
        if status:
            query = query.where(ARPayment.status == status)
            
        if customer_id:
            query = query.where(ARPayment.customer_id == customer_id)
        
        query = query.offset(skip).limit(limit).order_by(ARPayment.payment_date.desc())
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_payments(
        self, 
        db: AsyncSession,
        status: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> int:
        """Count payments with filtering"""
        query = select(func.count(ARPayment.id))
        
        if status:
            query = query.where(ARPayment.status == status)
            
        if customer_id:
            query = query.where(ARPayment.customer_id == customer_id)
        
        result = await db.execute(query)
        return result.scalar()
    
    async def get_payment(self, db: AsyncSession, payment_id: str) -> Optional[ARPayment]:
        """Get payment by ID"""
        query = select(ARPayment).options(selectinload(ARPayment.customer)).where(ARPayment.id == payment_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()