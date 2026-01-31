from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget, BudgetLineItem


class BudgetService:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def get_budgets(self) -> List[Budget]:
        result = await self.db.execute(
            select(Budget).where(Budget.tenant_id == self.tenant_id)
        )
        return result.scalars().all()
    
    async def create_budget(self, budget_data: dict) -> Budget:
        budget = Budget(
            tenant_id=self.tenant_id,
            budget_name=budget_data['budget_name'],
            budget_year=budget_data['budget_year'],
            budget_period=budget_data.get('budget_period', 'annual'),
            total_amount=budget_data.get('total_amount', 0)
        )
        
        for item_data in budget_data.get('line_items', []):
            line_item = BudgetLineItem(
                tenant_id=self.tenant_id,
                account_id=item_data['account_id'],
                account_name=item_data['account_name'],
                budgeted_amount=item_data['budgeted_amount']
            )
            budget.line_items.append(line_item)
        
        self.db.add(budget)
        await self.db.commit()
        await self.db.refresh(budget)
        return budget