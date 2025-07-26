from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from decimal import Decimal
from ..models import Customer, ARInvoice, CollectionActivity

class CollectionsService:
    """Service for collections management operations"""
    
    async def get_overdue_invoices(self, db: AsyncSession, days_overdue: int = 0):
        """Get overdue invoices for collections"""
        today = date.today()
        cutoff_date = today - timedelta(days=days_overdue)
        
        query = select(ARInvoice).options(
            selectinload(ARInvoice.customer)
        ).where(
            ARInvoice.balance_due > 0,
            ARInvoice.due_date <= cutoff_date,
            ARInvoice.status.in_(["sent", "viewed", "partially_paid"])
        ).order_by(ARInvoice.due_date)
        
        result = await db.execute(query)
        invoices = result.scalars().all()
        
        return [
            {
                "invoice_id": inv.id,
                "invoice_number": inv.invoice_number,
                "customer_id": inv.customer_id,
                "customer_name": inv.customer.name,
                "customer_email": inv.customer.email,
                "customer_phone": inv.customer.phone,
                "invoice_date": inv.invoice_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "total_amount": float(inv.total_amount),
                "balance_due": float(inv.balance_due),
                "days_overdue": inv.days_overdue,
                "status": inv.status
            }
            for inv in invoices
        ]
    
    async def get_collections_dashboard(self, db: AsyncSession):
        """Get collections dashboard data"""
        today = date.today()
        
        # Get overdue amounts by aging buckets
        query = select(ARInvoice).options(
            selectinload(ARInvoice.customer)
        ).where(
            ARInvoice.balance_due > 0,
            ARInvoice.due_date < today
        )
        
        result = await db.execute(query)
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
        
        # Get collection activity stats
        activity_query = select(func.count(CollectionActivity.id)).where(
            CollectionActivity.activity_date >= today - timedelta(days=30)
        )
        recent_activities = await db.scalar(activity_query)
        
        return {
            "total_overdue": float(total_overdue),
            "aging_buckets": {
                "days_1_30": float(days_1_30),
                "days_31_60": float(days_31_60),
                "days_61_90": float(days_61_90),
                "over_90_days": float(over_90)
            },
            "total_overdue_invoices": len(overdue_invoices),
            "recent_activities": recent_activities or 0,
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
    
    async def create_collection_activity(self, db: AsyncSession, activity_data: dict, user_id: int):
        """Create a collection activity record"""
        activity = CollectionActivity(
            customer_id=activity_data["customer_id"],
            invoice_id=activity_data.get("invoice_id"),
            activity_date=datetime.strptime(activity_data["activity_date"], "%Y-%m-%d").date(),
            activity_type=activity_data["activity_type"],
            status=activity_data.get("status", "current"),
            subject=activity_data.get("subject"),
            description=activity_data.get("description"),
            outcome=activity_data.get("outcome"),
            follow_up_date=datetime.strptime(activity_data["follow_up_date"], "%Y-%m-%d").date() if activity_data.get("follow_up_date") else None,
            follow_up_action=activity_data.get("follow_up_action"),
            created_by=user_id
        )
        
        db.add(activity)
        await db.commit()
        await db.refresh(activity)
        
        return {
            "activity_id": activity.id,
            "customer_id": activity.customer_id,
            "activity_type": activity.activity_type,
            "activity_date": activity.activity_date.isoformat(),
            "status": activity.status,
            "follow_up_date": activity.follow_up_date.isoformat() if activity.follow_up_date else None,
            "created_by": user_id
        }
    
    async def get_collection_activities(self, db: AsyncSession, customer_id: Optional[int] = None, 
                                      invoice_id: Optional[int] = None, limit: int = 100):
        """Get collection activities with filtering"""
        query = select(CollectionActivity)
        
        if customer_id:
            query = query.where(CollectionActivity.customer_id == customer_id)
        if invoice_id:
            query = query.where(CollectionActivity.invoice_id == invoice_id)
            
        query = query.order_by(desc(CollectionActivity.activity_date)).limit(limit)
        
        result = await db.execute(query)
        activities = result.scalars().all()
        
        return [
            {
                "id": activity.id,
                "customer_id": activity.customer_id,
                "invoice_id": activity.invoice_id,
                "activity_date": activity.activity_date.isoformat(),
                "activity_type": activity.activity_type,
                "status": activity.status,
                "subject": activity.subject,
                "description": activity.description,
                "outcome": activity.outcome,
                "follow_up_date": activity.follow_up_date.isoformat() if activity.follow_up_date else None,
                "follow_up_action": activity.follow_up_action
            }
            for activity in activities
        ]
    
    async def send_dunning_letter(self, db: AsyncSession, dunning_data: dict, user_id: int):
        """Send dunning letter to customer"""
        customer_id = dunning_data["customer_id"]
        letter_type = dunning_data.get("letter_type", "first_notice")
        
        # Get customer and overdue invoices
        customer_query = select(Customer).options(
            selectinload(Customer.invoices)
        ).where(Customer.id == customer_id)
        
        result = await db.execute(customer_query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return None
        
        # Get overdue invoices
        today = date.today()
        overdue_invoices = [
            inv for inv in customer.invoices 
            if inv.balance_due > 0 and inv.due_date < today
        ]
        
        if not overdue_invoices:
            return {"error": "No overdue invoices found for customer"}
        
        # Determine collection status based on letter type
        status_mapping = {
            "first_notice": "first_notice",
            "second_notice": "second_notice", 
            "final_notice": "final_notice",
            "collections": "collections"
        }
        
        collection_status = status_mapping.get(letter_type, "first_notice")
        
        # Create collection activity
        activity_data = {
            "customer_id": customer_id,
            "activity_date": date.today().isoformat(),
            "activity_type": "letter",
            "status": collection_status,
            "subject": f"{letter_type.replace('_', ' ').title()} - Overdue Account",
            "description": f"Sent {letter_type} for {len(overdue_invoices)} overdue invoices totaling ${sum(inv.balance_due for inv in overdue_invoices):.2f}",
            "outcome": "Letter sent via email and mail",
            "follow_up_date": (date.today() + timedelta(days=7)).isoformat(),
            "follow_up_action": "Follow up if no response received"
        }
        
        activity = await self.create_collection_activity(db, activity_data, user_id)
        
        # In real implementation, this would generate and send the actual letter
        return {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "letter_type": letter_type,
            "overdue_invoices": len(overdue_invoices),
            "total_overdue": float(sum(inv.balance_due for inv in overdue_invoices)),
            "activity_id": activity["activity_id"],
            "sent_date": date.today().isoformat()
        }
    
    async def setup_payment_reminder(self, db: AsyncSession, reminder_data: dict, user_id: int):
        """Set up automated payment reminder"""
        customer_id = reminder_data["customer_id"]
        reminder_type = reminder_data.get("reminder_type", "email")
        days_before_due = reminder_data.get("days_before_due", 3)
        
        # Get customer
        customer_query = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(customer_query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return None
        
        # Create reminder activity
        activity_data = {
            "customer_id": customer_id,
            "activity_date": date.today().isoformat(),
            "activity_type": "reminder_setup",
            "status": "current",
            "subject": f"Payment Reminder Setup - {reminder_type}",
            "description": f"Automated {reminder_type} reminders set up {days_before_due} days before due date",
            "outcome": "Reminder system configured",
            "follow_up_date": (date.today() + timedelta(days=30)).isoformat(),
            "follow_up_action": "Review reminder effectiveness"
        }
        
        activity = await self.create_collection_activity(db, activity_data, user_id)
        
        # In real implementation, this would configure the reminder system
        return {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "reminder_type": reminder_type,
            "days_before_due": days_before_due,
            "activity_id": activity["activity_id"],
            "setup_date": date.today().isoformat()
        }
    
    async def get_follow_up_tasks(self, db: AsyncSession, user_id: Optional[int] = None):
        """Get collection follow-up tasks"""
        today = date.today()
        
        query = select(CollectionActivity).where(
            CollectionActivity.follow_up_date <= today,
            CollectionActivity.follow_up_action.isnot(None)
        )
        
        if user_id:
            query = query.where(CollectionActivity.created_by == user_id)
            
        query = query.order_by(CollectionActivity.follow_up_date)
        
        result = await db.execute(query)
        activities = result.scalars().all()
        
        return [
            {
                "activity_id": activity.id,
                "customer_id": activity.customer_id,
                "invoice_id": activity.invoice_id,
                "follow_up_date": activity.follow_up_date.isoformat(),
                "follow_up_action": activity.follow_up_action,
                "original_activity": activity.activity_type,
                "status": activity.status,
                "days_overdue": (today - activity.follow_up_date).days
            }
            for activity in activities
        ]