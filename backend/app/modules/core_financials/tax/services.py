from typing import List, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.crud.base import CRUDBase
from .models import TaxJurisdiction, TaxRate, TaxTransaction, TaxExemption, TaxReturn
from .schemas import (
    TaxJurisdictionCreate, TaxRateCreate, TaxTransactionCreate, 
    TaxExemptionCreate, TaxReturnCreate
)

class TaxJurisdictionService(CRUDBase[TaxJurisdiction, TaxJurisdictionCreate, None]):
    def __init__(self):
        super().__init__(TaxJurisdiction)
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[TaxJurisdiction]:
        result = await db.execute(select(TaxJurisdiction).where(TaxJurisdiction.code == code))
        return result.scalar_one_or_none()
    
    async def get_by_level(self, db: AsyncSession, level: str) -> List[TaxJurisdiction]:
        result = await db.execute(
            select(TaxJurisdiction)
            .where(and_(TaxJurisdiction.level == level, TaxJurisdiction.is_active == True))
        )
        return result.scalars().all()

class TaxRateService(CRUDBase[TaxRate, TaxRateCreate, None]):
    def __init__(self):
        super().__init__(TaxRate)
    
    async def get_active_rates(self, db: AsyncSession, tax_type: str = None) -> List[TaxRate]:
        query = select(TaxRate).where(TaxRate.is_active == True)
        
        if tax_type:
            query = query.where(TaxRate.tax_type == tax_type)
        
        # Filter by effective date
        today = date.today()
        query = query.where(
            and_(
                TaxRate.effective_date <= today,
                (TaxRate.expiry_date.is_(None) | (TaxRate.expiry_date >= today))
            )
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_rate_for_jurisdiction(
        self, 
        db: AsyncSession, 
        jurisdiction_id: int, 
        tax_type: str,
        effective_date: date = None
    ) -> Optional[TaxRate]:
        if not effective_date:
            effective_date = date.today()
        
        result = await db.execute(
            select(TaxRate).where(
                and_(
                    TaxRate.jurisdiction_id == jurisdiction_id,
                    TaxRate.tax_type == tax_type,
                    TaxRate.effective_date <= effective_date,
                    (TaxRate.expiry_date.is_(None) | (TaxRate.expiry_date >= effective_date)),
                    TaxRate.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

class TaxTransactionService(CRUDBase[TaxTransaction, TaxTransactionCreate, None]):
    def __init__(self):
        super().__init__(TaxTransaction)
    
    async def create_transaction(self, db: AsyncSession, transaction_data: TaxTransactionCreate) -> TaxTransaction:
        # Create main transaction
        transaction = TaxTransaction(
            transaction_date=transaction_data.transaction_date,
            document_number=transaction_data.document_number,
            reference_number=transaction_data.reference_number,
            tax_rate_id=transaction_data.tax_rate_id,
            taxable_amount=transaction_data.taxable_amount,
            tax_amount=transaction_data.tax_amount,
            total_amount=transaction_data.total_amount,
            status=transaction_data.status
        )
        
        db.add(transaction)
        await db.flush()
        
        # Create components if provided
        for component_data in transaction_data.components:
            from .models import TaxTransactionComponent
            component = TaxTransactionComponent(
                transaction_id=transaction.id,
                tax_component=component_data.tax_component,
                component_rate=component_data.component_rate,
                component_amount=component_data.component_amount
            )
            db.add(component)
        
        await db.commit()
        await db.refresh(transaction)
        return transaction
    
    async def calculate_tax(
        self, 
        db: AsyncSession, 
        taxable_amount: Decimal, 
        tax_rate_id: int
    ) -> Decimal:
        # Get tax rate
        tax_rate = await self.get_tax_rate(db, tax_rate_id)
        if not tax_rate:
            raise ValueError("Tax rate not found")
        
        return taxable_amount * tax_rate.rate
    
    async def get_tax_rate(self, db: AsyncSession, tax_rate_id: int) -> Optional[TaxRate]:
        result = await db.execute(select(TaxRate).where(TaxRate.id == tax_rate_id))
        return result.scalar_one_or_none()

class TaxExemptionService(CRUDBase[TaxExemption, TaxExemptionCreate, None]):
    def __init__(self):
        super().__init__(TaxExemption)
    
    async def get_active_exemptions(self, db: AsyncSession) -> List[TaxExemption]:
        today = date.today()
        result = await db.execute(
            select(TaxExemption).where(
                and_(
                    TaxExemption.effective_date <= today,
                    (TaxExemption.expiry_date.is_(None) | (TaxExemption.expiry_date >= today)),
                    TaxExemption.is_active == True
                )
            )
        )
        return result.scalars().all()

class TaxReturnService(CRUDBase[TaxReturn, TaxReturnCreate, None]):
    def __init__(self):
        super().__init__(TaxReturn)
    
    async def generate_return_number(self, db: AsyncSession, tax_type: str, period_year: int) -> str:
        # Get count of returns for this type and year
        result = await db.execute(
            select(TaxReturn).where(
                and_(
                    TaxReturn.tax_type == tax_type,
                    TaxReturn.period_start >= date(period_year, 1, 1),
                    TaxReturn.period_start < date(period_year + 1, 1, 1)
                )
            )
        )
        count = len(result.scalars().all())
        return f"TR-{tax_type.upper()}-{period_year}-{count + 1:04d}"
    
    async def get_returns_by_period(
        self, 
        db: AsyncSession, 
        start_date: date, 
        end_date: date
    ) -> List[TaxReturn]:
        result = await db.execute(
            select(TaxReturn).where(
                and_(
                    TaxReturn.period_start >= start_date,
                    TaxReturn.period_end <= end_date
                )
            ).order_by(TaxReturn.due_date)
        )
        return result.scalars().all()