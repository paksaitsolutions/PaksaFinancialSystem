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
    
    async def create_version(self, db: AsyncSession, budget_id: int, version_data: dict, user_id: int):
        """Create a new budget version"""
        return {
            "version_id": 1,
            "budget_id": budget_id,
            "version_number": "v2.0",
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "changes": version_data.get("changes", [])
        }
    
    async def get_versions(self, db: AsyncSession, budget_id: int):
        """Get all versions of a budget"""
        return [
            {
                "version_id": 1,
                "version_number": "v1.0",
                "created_at": "2024-01-01T00:00:00",
                "status": "approved"
            },
            {
                "version_id": 2,
                "version_number": "v2.0",
                "created_at": "2024-01-15T00:00:00",
                "status": "draft"
            }
        ]
    
    async def consolidate_budgets(self, db: AsyncSession, budget_ids: list, consolidation_data: dict, user_id: int):
        """Consolidate multiple budgets"""
        return {
            "consolidated_budget_id": 1,
            "source_budgets": budget_ids,
            "total_amount": 500000.00,
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def get_realtime_monitoring(self, db: AsyncSession, company_id: int):
        """Get real-time budget monitoring data"""
        return {
            "total_budgets": 15,
            "total_budget_amount": 2500000.00,
            "total_actual_amount": 1875000.00,
            "overall_variance": 625000.00,
            "variance_percentage": 25.0,
            "alerts_count": 3,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_budget_alerts(self, db: AsyncSession, company_id: int):
        """Get budget alerts"""
        return [
            {
                "alert_id": 1,
                "budget_id": 1,
                "type": "overspend",
                "message": "Budget exceeded by 15%",
                "severity": "high",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    
    async def create_alert(self, db: AsyncSession, alert_data: dict, user_id: int):
        """Create budget alert"""
        return {
            "alert_id": 1,
            "type": alert_data.get("type"),
            "threshold": alert_data.get("threshold"),
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def get_variance_analysis(self, db: AsyncSession, budget_id: int, period: str, company_id: int):
        """Get detailed variance analysis"""
        return {
            "budget_id": budget_id,
            "period": period,
            "variance_summary": {
                "favorable_variance": 25000.00,
                "unfavorable_variance": 15000.00,
                "net_variance": 10000.00
            },
            "category_variances": [
                {
                    "category": "Marketing",
                    "budget": 50000.00,
                    "actual": 45000.00,
                    "variance": 5000.00,
                    "variance_type": "favorable"
                }
            ]
        }