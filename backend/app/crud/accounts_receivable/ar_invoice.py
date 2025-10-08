"""
CRUD operations for AR Invoice model
"""
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import selectinload

from app.models.accounts_receivable.ar_invoice import ARInvoice, ARInvoiceLineItem

class ARInvoiceCRUD:
    """CRUD operations for AR invoices"""
    
    async def get_invoices(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        customer_id: Optional[str] = None,
        overdue_only: bool = False
    ) -> List[ARInvoice]:
        """Get invoices with filtering"""
        query = select(ARInvoice).options(
            selectinload(ARInvoice.customer),
            selectinload(ARInvoice.line_items)
        )
        
        if status:
            query = query.where(ARInvoice.status == status)
            
        if customer_id:
            query = query.where(ARInvoice.customer_id == customer_id)
            
        if overdue_only:
            query = query.where(
                and_(
                    ARInvoice.due_date < date.today(),
                    ARInvoice.balance_due > 0
                )
            )
        
        query = query.offset(skip).limit(limit).order_by(ARInvoice.invoice_date.desc())
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_invoices(
        self, 
        db: AsyncSession,
        status: Optional[str] = None,
        customer_id: Optional[str] = None,
        overdue_only: bool = False
    ) -> int:
        """Count invoices with filtering"""
        query = select(func.count(ARInvoice.id))
        
        if status:
            query = query.where(ARInvoice.status == status)
            
        if customer_id:
            query = query.where(ARInvoice.customer_id == customer_id)
            
        if overdue_only:
            query = query.where(
                and_(
                    ARInvoice.due_date < date.today(),
                    ARInvoice.balance_due > 0
                )
            )
        
        result = await db.execute(query)
        return result.scalar()
    
    async def get_invoice(self, db: AsyncSession, invoice_id: str) -> Optional[ARInvoice]:
        """Get invoice by ID"""
        query = select(ARInvoice).options(
            selectinload(ARInvoice.customer),
            selectinload(ARInvoice.line_items)
        ).where(ARInvoice.id == invoice_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_total_outstanding(self, db: AsyncSession) -> Decimal:
        """Get total outstanding amount"""
        query = select(func.sum(ARInvoice.balance_due)).where(ARInvoice.balance_due > 0)
        result = await db.execute(query)
        return result.scalar() or Decimal('0')
    
    async def get_overdue_amount(self, db: AsyncSession) -> Decimal:
        """Get total overdue amount"""
        query = select(func.sum(ARInvoice.balance_due)).where(
            and_(
                ARInvoice.due_date < date.today(),
                ARInvoice.balance_due > 0
            )
        )
        result = await db.execute(query)
        return result.scalar() or Decimal('0')
    
    async def get_current_month_collections(self, db: AsyncSession) -> Decimal:
        """Get current month collections"""
        start_of_month = date.today().replace(day=1)
        query = select(func.sum(ARInvoice.paid_amount)).where(
            ARInvoice.updated_at >= start_of_month
        )
        result = await db.execute(query)
        return result.scalar() or Decimal('0')
    
    async def calculate_dso(self, db: AsyncSession) -> float:
        """Calculate Days Sales Outstanding"""
        # Simplified DSO calculation - replace with more sophisticated logic
        total_receivables = await self.get_total_outstanding(db)
        # Mock daily sales - replace with actual calculation
        daily_sales = Decimal('50000')  # $50k daily sales average
        
        if daily_sales > 0:
            return float(total_receivables / daily_sales)
        return 0.0
    
    async def get_aging_analysis(self, db: AsyncSession):
        """Get aging bucket analysis"""
        today = date.today()
        
        # Mock aging analysis - replace with actual SQL queries
        return [
            {
                "range": "Current",
                "amount": 850000,
                "percentage": 45,
                "invoice_count": 156,
                "risk": "low"
            },
            {
                "range": "1-30 Days",
                "amount": 420000,
                "percentage": 25,
                "invoice_count": 89,
                "risk": "medium"
            },
            {
                "range": "31-60 Days",
                "amount": 285000,
                "percentage": 18,
                "invoice_count": 45,
                "risk": "high"
            },
            {
                "range": "60+ Days",
                "amount": 125000,
                "percentage": 12,
                "invoice_count": 23,
                "risk": "critical"
            }
        ]
    
    async def get_collection_effectiveness(self, db: AsyncSession):
        """Get collection effectiveness metrics"""
        # Mock collection metrics - replace with actual calculations
        return [
            {"name": "Current Collections", "value": "95%", "percentage": 95, "status": "excellent"},
            {"name": "1-30 Days", "value": "88%", "percentage": 88, "status": "good"},
            {"name": "31-60 Days", "value": "72%", "percentage": 72, "status": "fair"},
            {"name": "60+ Days", "value": "45%", "percentage": 45, "status": "poor"}
        ]
    
    async def get_detailed_aging_report(self, db: AsyncSession, as_of_date: Optional[date] = None, customer_id: Optional[str] = None):
        """Get detailed aging report"""
        # Mock detailed aging - replace with actual SQL
        return [
            {
                "customer_name": "Acme Corporation",
                "customer_id": "cust-001",
                "current": 25000.00,
                "days_1_30": 12000.00,
                "days_31_60": 0.00,
                "days_60_plus": 0.00,
                "total": 37000.00
            },
            {
                "customer_name": "Global Tech Solutions",
                "customer_id": "cust-002",
                "current": 15000.00,
                "days_1_30": 8000.00,
                "days_31_60": 27000.00,
                "days_60_plus": 0.00,
                "total": 50000.00
            }
        ]