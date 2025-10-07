from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from decimal import Decimal
from ..models import Customer, Invoice, Payment

class CustomerService:
    """Service for customer management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_customer(self, customer_data: dict, user_id: int):
        """Create a new customer with real database persistence"""
        # Generate unique customer ID
        customer_count = await self.db.scalar(select(func.count(Customer.id)))
        customer_id = f"CUST-{datetime.now().strftime('%Y%m%d')}-{customer_count + 1:04d}"
        
        # Create customer instance
        customer = Customer(
            customer_id=customer_id,
            name=customer_data["name"],
            legal_name=customer_data.get("legal_name", customer_data["name"]),
            customer_type=customer_data.get("customer_type", "business"),
            email=customer_data.get("email"),
            phone=customer_data.get("phone"),
            contact_person=customer_data.get("contact_person"),
            billing_address_line1=customer_data.get("billing_address_line1"),
            billing_city=customer_data.get("billing_city"),
            billing_state=customer_data.get("billing_state"),
            billing_postal_code=customer_data.get("billing_postal_code"),
            billing_country=customer_data.get("billing_country", "US"),
            credit_limit=Decimal(str(customer_data.get("credit_limit", 0))),
            payment_terms=customer_data.get("payment_terms", "NET30"),
            tax_id=customer_data.get("tax_id"),
            tax_exempt=customer_data.get("tax_exempt", False),
            status="active",
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer
    
    async def get_customers(self, skip: int = 0, limit: int = 100,
                           status: Optional[str] = None, customer_type: Optional[str] = None):
        """Get customers with real database filtering"""
        query = select(Customer).options(
            selectinload(Customer.invoices),
            selectinload(Customer.payments)
        )
        
        # Apply filters
        if status:
            query = query.where(Customer.status == status)
        if customer_type:
            query = query.where(Customer.customer_type == customer_type)
            
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(Customer.name)
        
        result = await self.db.execute(query)
        customers = result.scalars().all()
        
        return [
            {
                "id": customer.id,
                "customer_id": customer.customer_id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "status": customer.status,
                "customer_type": customer.customer_type,
                "credit_limit": float(customer.credit_limit or 0),
                "current_balance": float(customer.current_balance or 0),
                "outstanding_balance": float(customer.outstanding_balance or 0),
                "overdue_balance": float(customer.overdue_balance or 0),
                "total_sales_ytd": float(customer.total_sales_ytd or 0),
                "created_at": customer.created_at.isoformat() if customer.created_at else None
            }
            for customer in customers
        ]
    
    async def get_customer(self, customer_id: int):
        """Get customer by ID with complete details"""
        query = select(Customer).options(
            selectinload(Customer.invoices),
            selectinload(Customer.payments)
        ).where(Customer.id == customer_id)
        
        result = await self.db.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return None
            
        return {
            "id": customer.id,
            "customer_id": customer.customer_id,
            "name": customer.name,
            "legal_name": customer.legal_name,
            "customer_type": customer.customer_type,
            "email": customer.email,
            "phone": customer.phone,
            "contact_person": customer.contact_person,
            "billing_address_line1": customer.billing_address_line1,
            "billing_city": customer.billing_city,
            "billing_state": customer.billing_state,
            "billing_postal_code": customer.billing_postal_code,
            "billing_country": customer.billing_country,
            "credit_limit": float(customer.credit_limit or 0),
            "current_balance": float(customer.current_balance or 0),
            "outstanding_balance": float(customer.outstanding_balance or 0),
            "overdue_balance": float(customer.overdue_balance or 0),
            "credit_rating": customer.credit_rating,
            "payment_terms": customer.payment_terms,
            "credit_hold": customer.credit_hold,
            "status": customer.status,
            "customer_since": customer.customer_since.isoformat() if customer.customer_since else None,
            "total_sales_ytd": float(customer.total_sales_ytd or 0),
            "average_days_to_pay": customer.average_days_to_pay,
            "created_at": customer.created_at.isoformat() if customer.created_at else None
        }
    
    async def update_customer(self, customer_id: int, customer_data: dict, user_id: int):
        """Update customer with real database persistence"""
        query = select(Customer).where(Customer.id == customer_id)
        result = await self.db.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return None
            
        # Update fields
        for field, value in customer_data.items():
            if hasattr(customer, field) and value is not None:
                if field == "credit_limit":
                    setattr(customer, field, Decimal(str(value)))
                else:
                    setattr(customer, field, value)
                    
        customer.updated_by = user_id
        customer.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(customer)
        return await self.get_customer(customer_id)
    
    async def get_customer_aging_analysis(self, customer_id: Optional[int] = None):
        """Get customer aging analysis from real data"""
        query = select(Customer).options(selectinload(Customer.invoices))
        
        if customer_id:
            query = query.where(Customer.id == customer_id)
            
        result = await self.db.execute(query)
        customers = result.scalars().all()
        
        aging_data = []
        today = date.today()
        
        for customer in customers:
            current = days_30 = days_60 = days_90 = over_90 = Decimal('0')
            
            for invoice in customer.invoices:
                if invoice.balance_due > 0:
                    days_overdue = invoice.days_overdue
                    balance = invoice.balance_due
                    
                    if days_overdue <= 0:
                        current += balance
                    elif days_overdue <= 30:
                        days_30 += balance
                    elif days_overdue <= 60:
                        days_60 += balance
                    elif days_overdue <= 90:
                        days_90 += balance
                    else:
                        over_90 += balance
            
            total_outstanding = current + days_30 + days_60 + days_90 + over_90
            
            if total_outstanding > 0:
                aging_data.append({
                    "customer_id": customer.id,
                    "customer_name": customer.name,
                    "current": float(current),
                    "days_1_30": float(days_30),
                    "days_31_60": float(days_60),
                    "days_61_90": float(days_90),
                    "over_90_days": float(over_90),
                    "total_outstanding": float(total_outstanding)
                })
        
        return aging_data
    
    async def update_credit_limit(self, customer_id: int, credit_data: dict, user_id: int):
        """Update customer credit limit with validation"""
        query = select(Customer).where(Customer.id == customer_id)
        result = await self.db.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return None
            
        new_limit = Decimal(str(credit_data["credit_limit"]))
        old_limit = customer.credit_limit
        
        customer.credit_limit = new_limit
        customer.credit_rating = credit_data.get("credit_rating", customer.credit_rating)
        customer.updated_by = user_id
        customer.updated_at = datetime.utcnow()
        
        # Add note about credit limit change
        note = f"Credit limit changed from ${old_limit} to ${new_limit} on {datetime.now().strftime('%Y-%m-%d')}"
        if credit_data.get("reason"):
            note += f": {credit_data['reason']}"
            
        if customer.internal_notes:
            customer.internal_notes += f"\n{note}"
        else:
            customer.internal_notes = note
            
        await self.db.commit()
        await self.db.refresh(customer)
        
        return {
            "customer_id": customer_id,
            "old_credit_limit": float(old_limit),
            "new_credit_limit": float(new_limit),
            "updated_by": user_id,
            "updated_at": datetime.now().isoformat()
        }
    
    async def place_credit_hold(self, customer_id: int, hold_data: dict, user_id: int):
        """Place or remove credit hold on customer"""
        query = select(Customer).where(Customer.id == customer_id)
        result = await self.db.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return None
            
        customer.credit_hold = hold_data.get("credit_hold", True)
        customer.updated_by = user_id
        customer.updated_at = datetime.utcnow()
        
        # Add note about credit hold change
        action = "placed on" if customer.credit_hold else "removed from"
        note = f"Credit hold {action} {datetime.now().strftime('%Y-%m-%d')}"
        if hold_data.get("reason"):
            note += f": {hold_data['reason']}"
            
        if customer.internal_notes:
            customer.internal_notes += f"\n{note}"
        else:
            customer.internal_notes = note
            
        await self.db.commit()
        
        return {
            "customer_id": customer_id,
            "credit_hold": customer.credit_hold,
            "reason": hold_data.get("reason"),
            "updated_by": user_id
        }
    
    async def get_customer_payment_history(self, customer_id: int, limit: int = 50):
        """Get customer payment history"""
        query = select(Payment).where(
            Payment.customer_id == customer_id,
            Payment.status == "completed"
        ).order_by(desc(Payment.payment_date)).limit(limit)
        
        result = await self.db.execute(query)
        payments = result.scalars().all()
        
        return [
            {
                "payment_id": payment.id,
                "payment_number": payment.payment_number,
                "payment_date": payment.payment_date.isoformat(),
                "amount": float(payment.amount),
                "payment_method": payment.payment_method,
                "reference_number": payment.reference_number,
                "invoice_id": payment.invoice_id
            }
            for payment in payments
        ]