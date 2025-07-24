"""
CRUD operations for credit memos.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.accounts_payable.credit_memo import APCreditMemo, APCreditApplication
from app.models.accounts_payable.invoice import APInvoice
from app.schemas.accounts_payable.credit_memo import CreditMemoCreate, CreditMemoUpdate, CreditMemoApplicationRequest

class CreditMemoCRUD:
    """CRUD operations for credit memos."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(APCreditMemo)
    
    async def create(self, db: AsyncSession, *, obj_in: CreditMemoCreate) -> APCreditMemo:
        """Create a new credit memo."""
        # Generate credit memo number
        credit_memo_number = await self._generate_credit_memo_number(db)
        
        # Create credit memo
        db_obj = APCreditMemo(
            **obj_in.dict(),
            credit_memo_number=credit_memo_number,
            status="active",
            applied_amount=0,
            remaining_amount=obj_in.amount
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[APCreditMemo]:
        """Get a credit memo by ID."""
        query = select(APCreditMemo).where(APCreditMemo.id == id).options(
            selectinload(APCreditMemo.vendor),
            selectinload(APCreditMemo.original_invoice),
            selectinload(APCreditMemo.applications)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_credit_memo_number(self, db: AsyncSession, credit_memo_number: str) -> Optional[APCreditMemo]:
        """Get a credit memo by credit memo number."""
        query = select(APCreditMemo).where(APCreditMemo.credit_memo_number == credit_memo_number)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> List[APCreditMemo]:
        """Get multiple credit memos."""
        query = self.query_helper.build_query(
            filters=filters,
            sort_by=sort_by or "credit_date",
            sort_order=sort_order,
            skip=skip,
            limit=limit,
            eager_load=["vendor", "applications"]
        )
        return await self.query_helper.execute_query(db, query)
    
    async def get_paginated(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """Get paginated credit memos."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "credit_date",
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            eager_load=["vendor", "applications"]
        )
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: APCreditMemo,
        obj_in: Union[CreditMemoUpdate, Dict[str, Any]]
    ) -> APCreditMemo:
        """Update a credit memo."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Update credit memo attributes
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def apply_to_invoices(
        self,
        db: AsyncSession,
        *,
        db_obj: APCreditMemo,
        application_request: CreditMemoApplicationRequest
    ) -> APCreditMemo:
        """Apply credit memo to invoices."""
        # Check if credit memo can be applied
        if db_obj.status != "active":
            raise ValueError(f"Cannot apply credit memo with status: {db_obj.status}")
        
        total_application_amount = sum(app.amount for app in application_request.applications)
        
        # Check if there's enough remaining credit
        if total_application_amount > db_obj.remaining_amount:
            raise ValueError(f"Application amount ({total_application_amount}) exceeds remaining credit ({db_obj.remaining_amount})")
        
        # Apply to each invoice
        for app_data in application_request.applications:
            # Get invoice
            invoice = await self._get_invoice(db, app_data.invoice_id)
            if not invoice:
                raise ValueError(f"Invoice not found: {app_data.invoice_id}")
            
            # Check if invoice can receive credit
            if invoice.status not in ["approved", "partially_paid"]:
                raise ValueError(f"Cannot apply credit to invoice with status: {invoice.status}")
            
            # Check if application amount doesn't exceed invoice balance
            if app_data.amount > invoice.balance_due:
                raise ValueError(f"Application amount ({app_data.amount}) exceeds invoice balance ({invoice.balance_due})")
            
            # Create credit application
            application = APCreditApplication(
                credit_memo_id=db_obj.id,
                invoice_id=app_data.invoice_id,
                amount=app_data.amount,
                notes=app_data.notes
            )
            db.add(application)
            
            # Update invoice balance
            invoice.balance_due -= app_data.amount
            
            # Update invoice status if fully paid
            if invoice.balance_due <= 0:
                invoice.status = "paid"
            
            db.add(invoice)
        
        # Update credit memo amounts
        db_obj.applied_amount += total_application_amount
        db_obj.remaining_amount -= total_application_amount
        
        # Update credit memo status if fully applied
        if db_obj.remaining_amount <= 0:
            db_obj.status = "fully_applied"
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def void(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: APCreditMemo, 
        reason: str
    ) -> APCreditMemo:
        """Void a credit memo."""
        # Can only void active credit memos
        if db_obj.status not in ["active", "fully_applied"]:
            raise ValueError(f"Cannot void credit memo with status: {db_obj.status}")
        
        # Reverse all applications
        for application in db_obj.applications:
            invoice = await self._get_invoice(db, application.invoice_id)
            if invoice:
                # Restore invoice balance
                invoice.balance_due += application.amount
                
                # Update invoice status
                if invoice.status == "paid" and invoice.balance_due > 0:
                    if invoice.paid_amount > 0:
                        invoice.status = "partially_paid"
                    else:
                        invoice.status = "approved"
                
                db.add(invoice)
            
            # Delete application
            await db.delete(application)
        
        # Update credit memo status
        db_obj.status = "voided"
        db_obj.description = f"{db_obj.description or ''}\n\nVoid reason: {reason}".strip()
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def _generate_credit_memo_number(self, db: AsyncSession) -> str:
        """Generate a unique credit memo number."""
        # Get current year and month
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Get count of credit memos in current month
        query = select(func.count()).select_from(APCreditMemo).where(
            and_(
                func.extract('year', APCreditMemo.credit_date) == year,
                func.extract('month', APCreditMemo.credit_date) == month
            )
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        # Generate credit memo number: CM-YYYYMM-XXXX
        return f"CM-{year}{month:02d}-{count+1:04d}"
    
    async def _get_invoice(self, db: AsyncSession, invoice_id: UUID) -> Optional[APInvoice]:
        """Get an invoice by ID."""
        query = select(APInvoice).where(APInvoice.id == invoice_id)
        result = await db.execute(query)
        return result.scalars().first()

# Create an instance for dependency injection
credit_memo_crud = CreditMemoCRUD()