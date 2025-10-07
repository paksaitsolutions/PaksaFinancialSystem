from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from decimal import Decimal
from ..models import Customer, Invoice

class CollectionsService:
    """Service for collections management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_overdue_invoices(self, days_overdue: int = 0):
        """Get overdue invoices for collections"""
        today = date.today()
        cutoff_date = today - timedelta(days=days_overdue)
        
        query = select(Invoice).where(
            Invoice.balance_due > 0,
            Invoice.due_date <= cutoff_date,
            Invoice.status.in_(['sent', 'viewed', 'partially_paid'])
        ).order_by(Invoice.due_date)
        
        result = await self.db.execute(query)
        invoices = result.scalars().all()
        
        return [
            {
                "invoice_id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "customer_id": inv.customer_id,
                "issue_date": inv.issue_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "total_amount": float(inv.total_amount),
                "balance_due": float(inv.balance_due),
                "days_overdue": inv.days_overdue,
                "status": inv.status.value
            }
            for inv in invoices
        ]
    
    async def get_collections_dashboard(self):
        """Get collections dashboard data"""
        today = date.today()
        
        # Get overdue invoices
        query = select(Invoice).where(
            Invoice.balance_due > 0,
            Invoice.due_date < today
        )
        
        result = await self.db.execute(query)
        overdue_invoices = result.scalars().all()
        
        # Calculate aging buckets
        days_1_30 = days_31_60 = days_61_90 = over_90 = Decimal('0')
        total_overdue = Decimal('0')
        
        for invoice in overdue_invoices:
            days_overdue = invoice.days_overdue
            balance = invoice.balance_due
            total_overdue += balance
            
            if days_overdue <= 30:
                days_1_30 += balance
            elif days_overdue <= 60:
                days_31_60 += balance
            elif days_overdue <= 90:
                days_61_90 += balance
            else:
                over_90 += balance
        
        return {
            "total_overdue": float(total_overdue),
            "aging_buckets": {
                "days_1_30": float(days_1_30),
                "days_31_60": float(days_31_60),
                "days_61_90": float(days_61_90),
                "over_90_days": float(over_90)
            },
            "total_overdue_invoices": len(overdue_invoices),
            "collection_effectiveness": self._calculate_collection_effectiveness(overdue_invoices)
        }
    
    def _calculate_collection_effectiveness(self, overdue_invoices):
        """Calculate collection effectiveness percentage"""
        if not overdue_invoices:
            return 100.0
            
        # Simple effectiveness calculation based on aging
        total_balance = sum(inv.balance_due for inv in overdue_invoices)
        weighted_days = sum(inv.balance_due * inv.days_overdue for inv in overdue_invoices)
        
        if total_balance == 0:
            return 100.0
            
        avg_days_overdue = weighted_days / total_balance
        # Effectiveness decreases as average days overdue increases
        effectiveness = max(0, 100 - (avg_days_overdue / 90 * 100))
        
        return round(float(effectiveness), 1)
    
    async def create_collection_activity(self, activity_data: dict, user_id: int):
        """Create a collection activity record - placeholder implementation"""
        return {
            "activity_id": f"ACT-{datetime.now().strftime('%Y%m%d')}-001",
            "customer_id": activity_data["customer_id"],
            "activity_type": activity_data["activity_type"],
            "activity_date": activity_data["activity_date"],
            "status": activity_data.get("status", "current"),
            "created_by": user_id,
            "created_at": datetime.now().isoformat()
        }
    
    async def send_dunning_letter(self, dunning_data: dict, user_id: int):
        """Send dunning letter to customer - placeholder implementation"""
        return {
            "customer_id": dunning_data["customer_id"],
            "letter_type": dunning_data.get("letter_type", "first_notice"),
            "sent_date": date.today().isoformat(),
            "activity_id": f"ACT-{datetime.now().strftime('%Y%m%d')}-001"
        }