"""
Budget GL Integration Service
"""
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Budget, BudgetLineItem, JournalEntry, JournalEntryLine, ChartOfAccounts
from app.services.base import BaseService

class BudgetGLService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Budget)
    
    def update_budget_actuals(self, budget: Budget) -> None:
        """Update budget actual amounts from GL data"""
        
        # Get actual amounts from GL for budget accounts
        actual_amount = self.db.query(
            func.sum(JournalEntryLine.debit_amount - JournalEntryLine.credit_amount)
        ).join(JournalEntry).filter(
            JournalEntryLine.account_id == budget.account_id,
            JournalEntry.entry_date.between(
                f"{budget.budget_year}-01-01",
                f"{budget.budget_year}-12-31"
            ),
            JournalEntry.status == 'posted'
        ).scalar() or Decimal('0')
        
        # Update budget with actual amounts
        budget.actual_amount = actual_amount
        budget.variance = budget.budgeted_amount - actual_amount
        
        # Update line items
        for line_item in budget.line_items:
            line_actual = self.db.query(
                func.sum(JournalEntryLine.debit_amount - JournalEntryLine.credit_amount)
            ).join(JournalEntry).filter(
                JournalEntryLine.account_id == line_item.account_id,
                JournalEntry.entry_date.between(
                    f"{budget.budget_year}-01-01",
                    f"{budget.budget_year}-12-31"
                ),
                JournalEntry.status == 'posted'
            ).scalar() or Decimal('0')
            
            line_item.actual_amount = line_actual
            line_item.variance = line_item.budgeted_amount - line_actual
    
    def generate_budget_vs_actual_report(self, company_id: UUID, budget_year: int) -> dict:
        """Generate budget vs actual report from GL data"""
        
        budgets = self.db.query(Budget).filter(
            Budget.company_id == company_id,
            Budget.budget_year == budget_year
        ).all()
        
        report_data = {
            "budget_year": budget_year,
            "total_budgeted": Decimal('0'),
            "total_actual": Decimal('0'),
            "total_variance": Decimal('0'),
            "accounts": []
        }
        
        for budget in budgets:
            self.update_budget_actuals(budget)
            
            report_data["accounts"].append({
                "account_code": budget.account.account_code,
                "account_name": budget.account.account_name,
                "budgeted_amount": float(budget.budgeted_amount),
                "actual_amount": float(budget.actual_amount),
                "variance": float(budget.variance),
                "variance_percent": float((budget.variance / budget.budgeted_amount * 100) if budget.budgeted_amount else 0)
            })
            
            report_data["total_budgeted"] += budget.budgeted_amount
            report_data["total_actual"] += budget.actual_amount
            report_data["total_variance"] += budget.variance
        
        report_data["total_budgeted"] = float(report_data["total_budgeted"])
        report_data["total_actual"] = float(report_data["total_actual"])
        report_data["total_variance"] = float(report_data["total_variance"])
        
        return report_data