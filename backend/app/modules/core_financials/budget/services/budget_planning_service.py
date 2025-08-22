from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime
from decimal import Decimal
from ..enhanced_models import Budget, BudgetLineItem, BudgetTemplate

class BudgetPlanningService:
    """Service for budget planning operations"""
    
    async def create_budget_version(self, db: AsyncSession, budget_id: int, version_data: dict, user_id: int):
        """Create a new budget version with real database persistence"""
        # Get original budget
        original_query = select(Budget).options(
            selectinload(Budget.line_items)
        ).where(Budget.id == budget_id)
        
        result = await db.execute(original_query)
        original_budget = result.scalar_one_or_none()
        
        if not original_budget:
            return None
        
        # Generate new version number
        version_parts = original_budget.version_number.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        new_version = f"{major}.{minor + 1}"
        
        # Mark current version as not current
        original_budget.is_current_version = False
        
        # Create new version
        new_budget = Budget(
            budget_code=f"{original_budget.budget_code}-{new_version}",
            name=version_data.get("name", original_budget.name),
            description=version_data.get("description", original_budget.description),
            budget_type=original_budget.budget_type,
            status="draft",
            period_type=original_budget.period_type,
            total_amount=Decimal(str(version_data.get("total_amount", original_budget.total_amount))),
            start_date=original_budget.start_date,
            end_date=original_budget.end_date,
            fiscal_year=original_budget.fiscal_year,
            version_number=new_version,
            parent_budget_id=budget_id,
            is_current_version=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(new_budget)
        await db.flush()
        
        # Copy line items
        for original_line in original_budget.line_items:
            new_line = BudgetLineItem(
                budget_id=new_budget.id,
                line_number=original_line.line_number,
                category=original_line.category,
                subcategory=original_line.subcategory,
                description=original_line.description,
                budgeted_amount=original_line.budgeted_amount,
                gl_account_id=original_line.gl_account_id,
                notes=original_line.notes
            )
            db.add(new_line)
        
        await db.commit()
        await db.refresh(new_budget)
        
        return {
            "version_id": new_budget.id,
            "budget_id": budget_id,
            "version_number": new_version,
            "status": "draft",
            "created_by": user_id,
            "created_at": new_budget.created_at.isoformat()
        }
    
    async def approve_budget(self, db: AsyncSession, budget_id: int, approval_data: dict, user_id: int):
        """Approve budget with real workflow"""
        query = select(Budget).where(Budget.id == budget_id)
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            return None
        
        budget.status = "approved"
        budget.approved_at = datetime.utcnow()
        budget.approved_by = user_id
        budget.approval_notes = approval_data.get("notes")
        budget.updated_by = user_id
        budget.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "budget_id": budget_id,
            "status": "approved",
            "approved_by": user_id,
            "approved_at": budget.approved_at.isoformat(),
            "notes": approval_data.get("notes")
        }
    
    async def compare_budget_versions(self, db: AsyncSession, budget_id_1: int, budget_id_2: int):
        """Compare two budget versions"""
        query = select(Budget).options(
            selectinload(Budget.line_items)
        ).where(Budget.id.in_([budget_id_1, budget_id_2]))
        
        result = await db.execute(query)
        budgets = result.scalars().all()
        
        if len(budgets) != 2:
            return {"error": "One or both budgets not found"}
        
        budget_1, budget_2 = budgets[0], budgets[1]
        
        # Compare totals
        total_difference = float(budget_2.total_amount - budget_1.total_amount)
        total_percentage = (total_difference / float(budget_1.total_amount)) * 100 if budget_1.total_amount > 0 else 0
        
        return {
            "budget_1": {
                "id": budget_1.id,
                "version": budget_1.version_number,
                "total_amount": float(budget_1.total_amount)
            },
            "budget_2": {
                "id": budget_2.id,
                "version": budget_2.version_number,
                "total_amount": float(budget_2.total_amount)
            },
            "summary": {
                "total_difference": total_difference,
                "total_percentage_change": total_percentage
            }
        }
    
    async def consolidate_budgets(self, db: AsyncSession, budget_ids: list, consolidation_data: dict, user_id: int):
        """Consolidate multiple budgets into one"""
        # Get source budgets
        query = select(Budget).options(
            selectinload(Budget.line_items)
        ).where(Budget.id.in_(budget_ids))
        
        result = await db.execute(query)
        source_budgets = result.scalars().all()
        
        if len(source_budgets) != len(budget_ids):
            return {"error": "Some budgets not found"}
        
        # Calculate consolidated totals
        total_amount = sum(float(budget.total_amount) for budget in source_budgets)
        
        # Generate consolidated budget code
        budget_count = await db.scalar(select(func.count(Budget.id)))
        consolidated_code = f"CONS-{datetime.now().strftime('%Y%m%d')}-{budget_count + 1:03d}"
        
        # Create consolidated budget
        consolidated_budget = Budget(
            budget_code=consolidated_code,
            name=consolidation_data.get("name", "Consolidated Budget"),
            description=consolidation_data.get("description", "Consolidated from multiple budgets"),
            budget_type="master",
            status="draft",
            period_type=source_budgets[0].period_type,
            total_amount=Decimal(str(total_amount)),
            start_date=min(budget.start_date for budget in source_budgets),
            end_date=max(budget.end_date for budget in source_budgets),
            fiscal_year=source_budgets[0].fiscal_year,
            version_number="1.0",
            is_consolidated=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(consolidated_budget)
        await db.commit()
        await db.refresh(consolidated_budget)
        
        return {
            "consolidated_budget_id": consolidated_budget.id,
            "consolidated_code": consolidated_code,
            "source_budgets": budget_ids,
            "total_amount": total_amount,
            "created_by": user_id,
            "created_at": consolidated_budget.created_at.isoformat()
        }