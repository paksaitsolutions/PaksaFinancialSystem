"""
CRUD operations for 1099 reporting.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime, date

from sqlalchemy import select, and_, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.accounts_payable.form_1099 import Form1099, Form1099Transaction
from app.models.accounts_payable.payment import APPayment
from app.models.accounts_payable.vendor import Vendor
from app.schemas.accounts_payable.form_1099 import Form1099Create, Form1099Update, Form1099GenerateRequest

class Form1099CRUD:
    """CRUD operations for 1099 forms."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(Form1099)
    
    async def create(self, db: AsyncSession, *, obj_in: Form1099Create) -> Form1099:
        """Create a new 1099 form."""
        # Calculate total amount
        total_amount = (
            obj_in.box_1_rents + obj_in.box_2_royalties + obj_in.box_3_other_income +
            obj_in.box_5_fishing_boat_proceeds + obj_in.box_6_medical_health_payments +
            obj_in.box_7_nonemployee_compensation + obj_in.box_8_substitute_payments +
            obj_in.box_9_payer_direct_sales + obj_in.box_10_crop_insurance +
            obj_in.box_13_state_income + obj_in.box_14_gross_proceeds
        )
        
        # Create 1099 form
        db_obj = Form1099(
            **obj_in.dict(),
            status="draft",
            total_amount=total_amount
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[Form1099]:
        """Get a 1099 form by ID."""
        query = select(Form1099).where(Form1099.id == id).options(
            selectinload(Form1099.vendor),
            selectinload(Form1099.transactions)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_vendor_and_year(self, db: AsyncSession, vendor_id: UUID, tax_year: int) -> Optional[Form1099]:
        """Get a 1099 form by vendor and tax year."""
        query = select(Form1099).where(
            and_(
                Form1099.vendor_id == vendor_id,
                Form1099.tax_year == tax_year
            )
        )
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
    ) -> List[Form1099]:
        """Get multiple 1099 forms."""
        query = self.query_helper.build_query(
            filters=filters,
            sort_by=sort_by or "tax_year",
            sort_order=sort_order,
            skip=skip,
            limit=limit,
            eager_load=["vendor", "transactions"]
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
        """Get paginated 1099 forms."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "tax_year",
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            eager_load=["vendor", "transactions"]
        )
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Form1099,
        obj_in: Union[Form1099Update, Dict[str, Any]]
    ) -> Form1099:
        """Update a 1099 form."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Update form attributes
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        # Recalculate total amount
        db_obj.total_amount = (
            db_obj.box_1_rents + db_obj.box_2_royalties + db_obj.box_3_other_income +
            db_obj.box_5_fishing_boat_proceeds + db_obj.box_6_medical_health_payments +
            db_obj.box_7_nonemployee_compensation + db_obj.box_8_substitute_payments +
            db_obj.box_9_payer_direct_sales + db_obj.box_10_crop_insurance +
            db_obj.box_13_state_income + db_obj.box_14_gross_proceeds
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def generate_forms(
        self,
        db: AsyncSession,
        *,
        request: Form1099GenerateRequest
    ) -> List[Form1099]:
        """Generate 1099 forms for a tax year."""
        # Get vendors with 1099 flag
        vendor_query = select(Vendor).where(Vendor.is_1099 == True)
        if request.vendor_ids:
            vendor_query = vendor_query.where(Vendor.id.in_(request.vendor_ids))
        
        vendor_result = await db.execute(vendor_query)
        vendors = vendor_result.scalars().all()
        
        generated_forms = []
        
        for vendor in vendors:
            # Get payments for the tax year
            payment_query = select(APPayment).where(
                and_(
                    APPayment.vendor_id == vendor.id,
                    APPayment.status == "completed",
                    extract('year', APPayment.payment_date) == request.tax_year
                )
            )
            payment_result = await db.execute(payment_query)
            payments = payment_result.scalars().all()
            
            # Calculate total payments
            total_payments = sum(payment.amount for payment in payments)
            
            # Only create form if total exceeds minimum
            if total_payments >= request.minimum_amount:
                # Check if form already exists
                existing_form = await self.get_by_vendor_and_year(db, vendor.id, request.tax_year)
                
                if not existing_form:
                    # Create new form
                    form_data = Form1099Create(
                        vendor_id=vendor.id,
                        tax_year=request.tax_year,
                        box_7_nonemployee_compensation=total_payments  # Default to box 7
                    )
                    form = await self.create(db, obj_in=form_data)
                    
                    # Create transactions
                    for payment in payments:
                        transaction = Form1099Transaction(
                            form_1099_id=form.id,
                            payment_id=payment.id,
                            amount=payment.amount,
                            box_number=7,  # Default to box 7
                            description=f"Payment {payment.payment_number}"
                        )
                        db.add(transaction)
                    
                    await db.commit()
                    generated_forms.append(form)
        
        return generated_forms
    
    async def file_form(self, db: AsyncSession, *, db_obj: Form1099) -> Form1099:
        """Mark a 1099 form as filed."""
        if db_obj.status != "ready":
            raise ValueError(f"Cannot file form with status: {db_obj.status}")
        
        db_obj.status = "filed"
        db_obj.filed_date = date.today()
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def void_form(self, db: AsyncSession, *, db_obj: Form1099, reason: str) -> Form1099:
        """Void a 1099 form."""
        db_obj.status = "voided"
        db_obj.void = True
        db_obj.notes = f"{db_obj.notes or ''}\n\nVoid reason: {reason}".strip()
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_summary(self, db: AsyncSession, tax_year: int) -> Dict[str, Any]:
        """Get 1099 summary for a tax year."""
        # Get all forms for the year
        forms_query = select(Form1099).where(Form1099.tax_year == tax_year)
        forms_result = await db.execute(forms_query)
        forms = forms_result.scalars().all()
        
        # Calculate summary
        total_forms = len(forms)
        total_amount = sum(form.total_amount for form in forms)
        
        forms_by_status = {}
        forms_by_type = {}
        
        for form in forms:
            # Count by status
            status = form.status
            forms_by_status[status] = forms_by_status.get(status, 0) + 1
            
            # Count by type
            form_type = form.form_type
            forms_by_type[form_type] = forms_by_type.get(form_type, 0) + 1
        
        return {
            "tax_year": tax_year,
            "total_forms": total_forms,
            "total_amount": total_amount,
            "forms_by_status": forms_by_status,
            "forms_by_type": forms_by_type
        }

# Create an instance for dependency injection
form_1099_crud = Form1099CRUD()