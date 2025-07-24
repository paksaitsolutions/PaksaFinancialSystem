from typing import Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.crud.base import CRUDBase
from .models import Budget, BudgetLineItem
from .schemas import BudgetCreate, BudgetUpdate, BudgetVsActual

class BudgetService(CRUDBase[Budget, BudgetCreate, BudgetUpdate]):
    def __init__(self):
        super().__init__(Budget)
    
    async def approve_budget(self, db: AsyncSession, budget_id: int, notes: str = None) -> Optional[Budget]:
        budget = await self.get(db, budget_id)
        if not budget:
            return None
        
        budget.status = "APPROVED"
        budget.approved_at = datetime.utcnow()
        budget.approval_notes = notes
        
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
        return budget
    
    async def reject_budget(self, db: AsyncSession, budget_id: int, reason: str) -> Optional[Budget]:
        budget = await self.get(db, budget_id)
        if not budget:
            return None
        
        budget.status = "REJECTED"
        budget.rejected_at = datetime.utcnow()
        budget.rejection_reason = reason
        
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
        return budget
    
    async def submit_for_approval(self, db: AsyncSession, budget_id: int) -> Optional[Budget]:
        budget = await self.get(db, budget_id)
        if not budget:
            return None
        
        budget.status = "PENDING_APPROVAL"
        budget.submitted_at = datetime.utcnow()
        
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
        return budget
    
    async def get_budget_vs_actual(self, db: AsyncSession, budget_id: int, period: str) -> BudgetVsActual:
        budget = await self.get(db, budget_id)
        if not budget:
            raise ValueError("Budget not found")
        
        # Mock actual amounts - in real implementation, this would query actual transactions
        actual_amount = budget.amount * Decimal('0.85')  # 85% of budget
        variance = budget.amount - actual_amount
        variance_percent = (variance / budget.amount) * 100 if budget.amount > 0 else 0
        
        line_items = []
        for line_item in budget.line_items:
            actual_line_amount = line_item.amount * Decimal('0.85')
            line_variance = line_item.amount - actual_line_amount
            
            line_items.append({
                "category": line_item.category,
                "budgetAmount": float(line_item.amount),
                "actualAmount": float(actual_line_amount),
                "variance": float(line_variance)
            })
        
        return BudgetVsActual(
            budgetId=str(budget_id),
            period=period,
            budgetAmount=float(budget.amount),
            actualAmount=float(actual_amount),
            variance=float(variance),
            variancePercent=float(variance_percent),
            lineItems=line_items
        )