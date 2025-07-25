"""
CRUD operations for Accounts Payable module
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.core.database import get_db
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ValidationException,
    ConflictException
)

# Import models and schemas
from models.accounts_payable import Bill, BillItem, Payment, BillStatus, PaymentMethod
from models.chart_of_accounts import ChartOfAccounts
from models.user import User
from schemas.accounts_payable import BillCreate, BillUpdate, PaymentCreate, PaymentUpdate

# Import base CRUD class
from .base_ap import CRUDBaseAP


class CRUDBill(CRUDBaseAP[Bill, BillCreate, BillUpdate]):
    """CRUD operations for Bill model"""
    
    def __init__(self):
        super().__init__(Bill)
    
    async def get_by_number(self, db: AsyncSession, bill_number: str) -> Optional[Bill]:
        """Get a bill by bill number"""
        result = await db.execute(
            select(Bill)
            .options(
                selectinload(Bill.items),
                selectinload(Bill.vendor),
                selectinload(Bill.payments)
            )
            .where(Bill.bill_number == bill_number)
        )
        return result.scalars().first()
    
    async def get_with_items(self, db: AsyncSession, bill_id: UUID) -> Optional[Bill]:
        """Get a bill with its items"""
        result = await db.execute(
            select(Bill)
            .options(selectinload(Bill.items))
            .where(Bill.id == bill_id)
        )
        return result.scalars().first()
    
    async def create_with_items(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: BillCreate, 
        created_by_id: UUID
    ) -> Bill:
        """Create a new bill with items"""
        # Generate bill number
        bill_number = await self._generate_bill_number(db)
        
        # Calculate totals
        subtotal = Decimal('0')
        tax_amount = Decimal('0')
        discount_amount = Decimal('0')
        
        # Create bill items
        items = []
        for item_in in obj_in.items:
            # Validate account exists and is active
            account = await db.get(ChartOfAccounts, item_in.account_id)
            if not account or not account.is_active:
                raise ValidationException(
                    f"Invalid or inactive account ID: {item_in.account_id}"
                )
            
            # Calculate item amount
            item_amount = (
                Decimal(str(item_in.quantity)) * 
                Decimal(str(item_in.unit_price)) * 
                (1 - Decimal(str(item_in.discount_percent)) / 100) * 
                (1 + Decimal(str(item_in.tax_rate)))
            )
            
            # Update totals
            subtotal += item_amount / (1 + Decimal(str(item_in.tax_rate)))
            tax_amount += item_amount - (item_amount / (1 + Decimal(str(item_in.tax_rate))))
            discount_amount += (
                Decimal(str(item_in.quantity)) * 
                Decimal(str(item_in.unit_price)) * 
                (Decimal(str(item_in.discount_percent)) / 100)
            )
            
            # Create bill item
            item_data = item_in.dict()
            item_data['amount'] = item_amount
            items.append(BillItem(**item_data))
        
        # Calculate total amount
        total_amount = subtotal + tax_amount
        
        # Create bill
        bill_data = obj_in.dict(exclude={"items"})
        bill_data.update({
            "bill_number": bill_number,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "discount_amount": discount_amount,
            "total_amount": total_amount,
            "balance_due": total_amount,
            "status": BillStatus.DRAFT,
            "created_by_id": created_by_id,
            "updated_by_id": created_by_id,
            "items": items
        })
        
        db_bill = Bill(**bill_data)
        db.add(db_bill)
        await db.commit()
        await db.refresh(db_bill)
        
        return db_bill
    
    async def update_with_items(
        self,
        db: AsyncSession,
        *,
        db_obj: Bill,
        obj_in: Union[BillUpdate, Dict[str, Any]],
        updated_by_id: UUID
    ) -> Bill:
        """Update a bill with its items"""
        # Check if bill can be updated
        if db_obj.status not in [BillStatus.DRAFT, BillStatus.AWAITING_APPROVAL]:
            raise BadRequestException(
                f"Cannot update a bill with status '{db_obj.status}'. "
                "Only draft or awaiting_approval bills can be updated."
            )
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Update bill fields
        for field, value in update_data.items():
            if field != 'items' and hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Update items if provided
        if 'items' in update_data and update_data['items'] is not None:
            # Delete existing items
            await db.execute(
                delete(BillItem).where(BillItem.bill_id == db_obj.id)
            )
            
            # Reset totals
            subtotal = Decimal('0')
            tax_amount = Decimal('0')
            discount_amount = Decimal('0')
            
            # Add new items
            for item_in in update_data['items']:
                # Validate account exists and is active
                account = await db.get(ChartOfAccounts, item_in['account_id'])
                if not account or not account.is_active:
                    raise ValidationException(
                        f"Invalid or inactive account ID: {item_in['account_id']}"
                    )
                
                # Calculate item amount
                item_amount = (
                    Decimal(str(item_in['quantity'])) * 
                    Decimal(str(item_in['unit_price'])) * 
                    (1 - Decimal(str(item_in.get('discount_percent', 0))) / 100) * 
                    (1 + Decimal(str(item_in.get('tax_rate', 0))))
                )
                
                # Update totals
                subtotal += item_amount / (1 + Decimal(str(item_in.get('tax_rate', 0))))
                tax_amount += item_amount - (item_amount / (1 + Decimal(str(item_in.get('tax_rate', 0)))))
                discount_amount += (
                    Decimal(str(item_in['quantity'])) * 
                    Decimal(str(item_in['unit_price'])) * 
                    (Decimal(str(item_in.get('discount_percent', 0))) / 100)
                )
                
                # Create bill item
                item_data = item_in.copy()
                item_data['amount'] = item_amount
                db_obj.items.append(BillItem(**item_data))
            
            # Update bill totals
            db_obj.subtotal = subtotal
            db_obj.tax_amount = tax_amount
            db_obj.discount_amount = discount_amount
            db_obj.total_amount = subtotal + tax_amount
            db_obj.balance_due = db_obj.total_amount - db_obj.amount_paid
        
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by_id = updated_by_id
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def submit_for_approval(self, db: AsyncSession, *, bill_id: UUID, user_id: UUID) -> Bill:
        """Submit a bill for approval"""
        bill = await self.get(db, bill_id)
        if not bill:
            raise NotFoundException("Bill not found")
        
        if bill.status != BillStatus.DRAFT:
            raise BadRequestException(
                f"Cannot submit a bill with status '{bill.status}'. "
                "Only draft bills can be submitted for approval."
            )
        
        # Additional validation can be added here
        if not bill.items:
            raise ValidationException("Cannot submit a bill with no items")
        
        bill.status = BillStatus.AWAITING_APPROVAL
        bill.updated_at = datetime.utcnow()
        bill.updated_by_id = user_id
        
        db.add(bill)
        await db.commit()
        await db.refresh(bill)
        
        return bill
    
    async def approve(self, db: AsyncSession, *, bill_id: UUID, user_id: UUID) -> Bill:
        """Approve a bill"""
        bill = await self.get(db, bill_id)
        if not bill:
            raise NotFoundException("Bill not found")
        
        if bill.status != BillStatus.AWAITING_APPROVAL:
            raise BadRequestException(
                f"Cannot approve a bill with status '{bill.status}'. "
                "Only bills awaiting approval can be approved."
            )
        
        bill.status = BillStatus.APPROVED
        bill.approved_at = datetime.utcnow()
        bill.approved_by_id = user_id
        bill.updated_at = datetime.utcnow()
        bill.updated_by_id = user_id
        
        # Create journal entry for the bill
        # This would be implemented based on your GL integration
        # await self._create_bill_journal_entry(db, bill, user_id)
        
        db.add(bill)
        await db.commit()
        await db.refresh(bill)
        
        return bill
    
    async def _generate_bill_number(self, db: AsyncSession) -> str:
        """Generate a unique bill number"""
        # Implement your bill number generation logic
        # Example: BILL-YYYYMMDD-XXXXX
        from datetime import datetime
        
        today = datetime.utcnow().strftime("%Y%m%d")
        
        # Get the last bill number for today
        result = await db.execute(
            select(Bill.bill_number)
            .where(Bill.bill_number.like(f"BILL-{today}-%"))
            .order_by(Bill.bill_number.desc())
            .limit(1)
        )
        
        last_bill = result.scalars().first()
        
        if last_bill:
            # Increment the sequence number
            sequence = int(last_bill.split("-")[2]) + 1
        else:
            # First bill of the day
            sequence = 1
        
        return f"BILL-{today}-{sequence:05d}"


class CRUDPayment(CRUDBaseAP[Payment, PaymentCreate, PaymentUpdate]):
    """CRUD operations for Payment model"""
    
    def __init__(self):
        super().__init__(Payment)
    
    async def get_by_number(self, db: AsyncSession, payment_number: str) -> Optional[Payment]:
        """Get a payment by payment number"""
        result = await db.execute(
            select(Payment)
            .options(
                selectinload(Payment.bill),
                selectinload(Payment.created_by),
                selectinload(Payment.updated_by)
            )
            .where(Payment.payment_number == payment_number)
        )
        return result.scalars().first()
    
    async def create_with_validation(
        self,
        db: AsyncSession,
        *,
        obj_in: PaymentCreate,
        created_by_id: UUID
    ) -> Payment:
        """Create a new payment with validation"""
        # Get the bill
        bill = await db.get(Bill, obj_in.bill_id)
        if not bill:
            raise NotFoundException("Bill not found")
        
        # Validate bill status
        if bill.status not in [BillStatus.APPROVED, BillStatus.PARTIALLY_PAID]:
            raise BadRequestException(
                f"Cannot create payment for bill with status '{bill.status}'. "
                "Only approved or partially paid bills can have payments."
            )
        
        # Validate payment amount
        if obj_in.amount <= 0:
            raise ValidationException("Payment amount must be greater than zero")
        
        if obj_in.amount > bill.balance_due:
            raise ValidationException(
                f"Payment amount (${obj_in.amount:,.2f}) exceeds the remaining balance "
                f"(${bill.balance_due:,.2f}) for this bill."
            )
        
        # Generate payment number
        payment_number = await self._generate_payment_number(db)
        
        # Create payment
        payment_data = obj_in.dict()
        payment_data.update({
            "payment_number": payment_number,
            "is_posted": False,
            "created_by_id": created_by_id,
            "updated_by_id": created_by_id
        })
        
        db_payment = Payment(**payment_data)
        db.add(db_payment)
        
        # Update bill status and amounts
        bill.amount_paid = (bill.amount_paid or 0) + obj_in.amount
        bill.balance_due = bill.total_amount - bill.amount_paid
        
        # Update bill status if fully paid
        if abs(bill.balance_due) < 0.01:  # Account for floating point precision
            bill.status = BillStatus.PAID
        else:
            bill.status = BillStatus.PARTIALLY_PAID
        
        bill.updated_at = datetime.utcnow()
        bill.updated_by_id = created_by_id
        
        db.add(bill)
        await db.commit()
        await db.refresh(db_payment)
        
        return db_payment
    
    async def post_payment(self, db: AsyncSession, *, payment_id: UUID, user_id: UUID) -> Payment:
        """Post a payment to the general ledger"""
        payment = await self.get(db, payment_id)
        if not payment:
            raise NotFoundException("Payment not found")
        
        if payment.is_posted:
            raise BadRequestException("Payment has already been posted")
        
        # Get the bill
        bill = await db.get(Bill, payment.bill_id)
        if not bill:
            raise NotFoundException("Bill not found")
        
        # Create journal entry for the payment
        # This would be implemented based on your GL integration
        # await self._create_payment_journal_entry(db, payment, bill, user_id)
        
        # Update payment status
        payment.is_posted = True
        payment.posted_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()
        payment.updated_by_id = user_id
        
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        
        return payment
    
    async def _generate_payment_number(self, db: AsyncSession) -> str:
        """Generate a unique payment number"""
        # Implement your payment number generation logic
        # Example: PMT-YYYYMMDD-XXXXX
        from datetime import datetime
        
        today = datetime.utcnow().strftime("%Y%m%d")
        
        # Get the last payment number for today
        result = await db.execute(
            select(Payment.payment_number)
            .where(Payment.payment_number.like(f"PMT-{today}-%"))
            .order_by(Payment.payment_number.desc())
            .limit(1)
        )
        
        last_payment = result.scalars().first()
        
        if last_payment:
            # Increment the sequence number
            sequence = int(last_payment.split("-")[2]) + 1
        else:
            # First payment of the day
            sequence = 1
        
        return f"PMT-{today}-{sequence:05d}"


# Create instances for easy import
bill = CRUDBill()
payment = CRUDPayment()
