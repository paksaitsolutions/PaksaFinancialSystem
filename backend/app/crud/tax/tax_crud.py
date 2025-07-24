"""
CRUD operations for tax management.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import date
from decimal import Decimal

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.tax.tax_rate import TaxRate, TaxExemption, TaxPolicy
from app.schemas.tax.tax_schemas import (
    TaxRateCreate, TaxRateUpdate, TaxExemptionCreate, TaxExemptionUpdate,
    TaxPolicyCreate, TaxPolicyUpdate, TaxCalculationRequest, TaxCalculationResponse
)

class TaxCRUD:
    """CRUD operations for tax management."""
    
    def __init__(self):
        """Initialize with query helpers."""
        self.tax_rate_helper = QueryHelper(TaxRate)
        self.tax_exemption_helper = QueryHelper(TaxExemption)
        self.tax_policy_helper = QueryHelper(TaxPolicy)
    
    # Tax Rate CRUD
    async def create_tax_rate(self, db: AsyncSession, *, obj_in: TaxRateCreate) -> TaxRate:
        """Create a new tax rate."""
        db_obj = TaxRate(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_tax_rate(self, db: AsyncSession, id: UUID) -> Optional[TaxRate]:
        """Get a tax rate by ID."""
        query = select(TaxRate).where(TaxRate.id == id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_tax_rates(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[TaxRate]:
        """Get multiple tax rates."""
        query = self.tax_rate_helper.build_query(
            filters=filters,
            sort_by="name",
            sort_order="asc",
            skip=skip,
            limit=limit
        )
        return await self.tax_rate_helper.execute_query(db, query)
    
    async def update_tax_rate(
        self,
        db: AsyncSession,
        *,
        db_obj: TaxRate,
        obj_in: Union[TaxRateUpdate, Dict[str, Any]]
    ) -> TaxRate:
        """Update a tax rate."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    # Tax Exemption CRUD
    async def create_tax_exemption(self, db: AsyncSession, *, obj_in: TaxExemptionCreate) -> TaxExemption:
        """Create a new tax exemption."""
        db_obj = TaxExemption(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_tax_exemption(self, db: AsyncSession, id: UUID) -> Optional[TaxExemption]:
        """Get a tax exemption by ID."""
        query = select(TaxExemption).where(TaxExemption.id == id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_tax_exemptions(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[TaxExemption]:
        """Get multiple tax exemptions."""
        query = self.tax_exemption_helper.build_query(
            filters=filters,
            sort_by="certificate_number",
            sort_order="asc",
            skip=skip,
            limit=limit
        )
        return await self.tax_exemption_helper.execute_query(db, query)
    
    # Tax Policy CRUD
    async def create_tax_policy(self, db: AsyncSession, *, obj_in: TaxPolicyCreate) -> TaxPolicy:
        """Create a new tax policy."""
        db_obj = TaxPolicy(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_tax_policies(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[TaxPolicy]:
        """Get multiple tax policies."""
        query = self.tax_policy_helper.build_query(
            filters=filters,
            sort_by="priority",
            sort_order="asc",
            skip=skip,
            limit=limit,
            eager_load=["tax_rate"]
        )
        return await self.tax_policy_helper.execute_query(db, query)
    
    # Tax Calculation Engine
    async def calculate_tax(
        self, 
        db: AsyncSession, 
        *, 
        request: TaxCalculationRequest
    ) -> TaxCalculationResponse:
        """Calculate tax for a given amount and conditions."""
        # Get applicable tax rates
        tax_rates = await self._get_applicable_tax_rates(
            db, request.tax_type, request.jurisdiction
        )
        
        # Check for exemptions
        exemptions = []
        if request.entity_id and request.entity_type:
            exemptions = await self._get_applicable_exemptions(
                db, request.entity_id, request.entity_type, request.tax_type
            )
        
        # Calculate tax
        subtotal = request.amount
        tax_amount = Decimal('0')
        tax_details = []
        
        for tax_rate in tax_rates:
            # Check if this tax rate is exempted
            is_exempt = any(
                ex.tax_type == tax_rate.tax_type and ex.is_active 
                for ex in exemptions
            )
            
            if not is_exempt:
                rate_tax_amount = subtotal * tax_rate.rate
                tax_amount += rate_tax_amount
                
                tax_details.append({
                    "tax_rate_id": str(tax_rate.id),
                    "name": tax_rate.name,
                    "rate": float(tax_rate.rate),
                    "amount": float(rate_tax_amount)
                })
        
        exemptions_applied = [
            {
                "certificate_number": ex.certificate_number,
                "exemption_type": ex.exemption_type,
                "tax_type": ex.tax_type
            }
            for ex in exemptions if ex.is_active
        ]
        
        total_amount = subtotal + tax_amount
        effective_rate = tax_amount / subtotal if subtotal > 0 else Decimal('0')
        
        return TaxCalculationResponse(
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            tax_rate=effective_rate,
            tax_details=tax_details,
            exemptions_applied=exemptions_applied
        )
    
    async def _get_applicable_tax_rates(
        self, 
        db: AsyncSession, 
        tax_type: str, 
        jurisdiction: Optional[str] = None
    ) -> List[TaxRate]:
        """Get applicable tax rates for given conditions."""
        query = select(TaxRate).where(
            and_(
                TaxRate.tax_type == tax_type,
                TaxRate.is_active == True,
                TaxRate.effective_date <= func.current_date(),
                (TaxRate.expiry_date.is_(None)) | (TaxRate.expiry_date > func.current_date())
            )
        )
        
        if jurisdiction:
            query = query.where(TaxRate.jurisdiction == jurisdiction)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _get_applicable_exemptions(
        self, 
        db: AsyncSession, 
        entity_id: UUID, 
        entity_type: str, 
        tax_type: str
    ) -> List[TaxExemption]:
        """Get applicable tax exemptions for an entity."""
        query = select(TaxExemption).where(
            and_(
                TaxExemption.entity_id == entity_id,
                TaxExemption.entity_type == entity_type,
                TaxExemption.tax_type == tax_type,
                TaxExemption.is_active == True,
                (TaxExemption.expiry_date.is_(None)) | (TaxExemption.expiry_date > func.current_date())
            )
        )
        
        result = await db.execute(query)
        return result.scalars().all()

# Create an instance for dependency injection
tax_crud = TaxCRUD()