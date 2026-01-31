from datetime import datetime, timedelta
from typing import List, Dict, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Budget, BudgetLine, BudgetAllocation
from app.services.ap import APService
from app.services.ar import ARService
from app.services.budget import BudgetService
from app.services.gl import GLService
from app.services.payroll import PayrollService
from app.services.procurement import ProcurementService


class BudgetAnalyticsService:
    def __init__(
        """  Init  ."""
        self,
        db: Session,
        budget_service: BudgetService,
        gl_service: GLService,
        ap_service: APService,
        ar_service: ARService,
        procurement_service: ProcurementService,
        payroll_service: PayrollService
    ):
        """  Init  ."""
        self.db = db
        self.budget_service = budget_service
        self.gl_service = gl_service
        self.ap_service = ap_service
        self.ar_service = ar_service
        self.procurement_service = procurement_service
        self.payroll_service = payroll_service

    def get_budget_performance(self, department_id: Optional[int] = None, project_id: Optional[int] = None) -> Dict:
        """Get Budget Performance."""
        """
        Get budget performance metrics.
        """
        # Get active budgets
        active_budgets = self.budget_service.get_active_budgets()
        
        # Calculate budgeted vs actual
        budgeted_amount = 0
        actual_amount = 0
        
        for budget in active_budgets:
            if (department_id and budget.department_id != department_id) or \
               (project_id and budget.project_id != project_id):
                continue
                
            # Calculate budgeted amount
            budgeted_amount += sum(line.amount for line in budget.lines)
            
            # Calculate actual spending
            allocations = self.db.query(BudgetAllocation).filter(
                BudgetAllocation.budget_id == budget.id
            ).all()
            
            actual_amount += sum(alloc.amount for alloc in allocations)
        
        return {
            "budgeted_amount": budgeted_amount,
            "actual_amount": actual_amount,
            "variance": budgeted_amount - actual_amount,
            "variance_percentage": ((actual_amount - budgeted_amount) / budgeted_amount * 100) if budgeted_amount > 0 else 0
        }

    def get_departmental_budget_analysis(self) -> List[Dict]:
        """Get Departmental Budget Analysis."""
        """
        Get budget analysis by department.
        """
        result = []
        
        # Get all departments with budgets
        departments = self.db.query(
            Budget.department_id,
            func.sum(BudgetLine.amount).label('total_budget')
        ).join(
            BudgetLine,
            Budget.id == BudgetLine.budget_id
        ).group_by(
            Budget.department_id
        ).all()
        
        for dept_id, total_budget in departments:
            # Get actual spending
            actual_spending = self.db.query(
                func.sum(BudgetAllocation.amount).label('total_spent')
            ).filter(
                BudgetAllocation.department_id == dept_id
            ).scalar()
            
            result.append({
                "department_id": dept_id,
                "total_budget": total_budget,
                "total_spent": actual_spending or 0,
                "variance": total_budget - (actual_spending or 0),
                "variance_percentage": ((actual_spending or 0) - total_budget) / total_budget * 100 if total_budget > 0 else 0
            })
        
        return result

    def get_project_budget_analysis(self) -> List[Dict]:
        """Get Project Budget Analysis."""
        """
        Get budget analysis by project.
        """
        result = []
        
        # Get all projects with budgets
        projects = self.db.query(
            Budget.project_id,
            func.sum(BudgetLine.amount).label('total_budget')
        ).join(
            BudgetLine,
            Budget.id == BudgetLine.budget_id
        ).group_by(
            Budget.project_id
        ).all()
        
        for proj_id, total_budget in projects:
            # Get actual spending
            actual_spending = self.db.query(
                func.sum(BudgetAllocation.amount).label('total_spent')
            ).filter(
                BudgetAllocation.project_id == proj_id
            ).scalar()
            
            result.append({
                "project_id": proj_id,
                "total_budget": total_budget,
                "total_spent": actual_spending or 0,
                "variance": total_budget - (actual_spending or 0),
                "variance_percentage": ((actual_spending or 0) - total_budget) / total_budget * 100 if total_budget > 0 else 0
            })
        
        return result

    def get_budget_trend_analysis(self, period: str = 'month', months: int = 12) -> List[Dict]:
        """Get Budget Trend Analysis."""
        """
        Get budget trend analysis over time.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months*30)
        
        result = []
        
        current_date = start_date
        while current_date <= end_date:
            # Get budgeted amount for period
            budgeted_amount = self.db.query(
                func.sum(BudgetLine.amount)
            ).join(
                Budget,
                Budget.id == BudgetLine.budget_id
            ).filter(
                Budget.start_date <= current_date,
                Budget.end_date >= current_date
            ).scalar()
            
            # Get actual spending for period
            actual_amount = self.db.query(
                func.sum(BudgetAllocation.amount)
            ).filter(
                BudgetAllocation.created_at >= current_date,
                BudgetAllocation.created_at < current_date + timedelta(days=30)
            ).scalar()
            
            result.append({
                "period": current_date.strftime('%Y-%m'),
                "budgeted_amount": budgeted_amount or 0,
                "actual_amount": actual_amount or 0,
                "variance": (budgeted_amount or 0) - (actual_amount or 0),
                "variance_percentage": ((actual_amount or 0) - (budgeted_amount or 0)) / (budgeted_amount or 1) * 100
            })
            
            current_date += timedelta(days=30)
        
        return result

    def get_budget_allocation_analysis(self, account_id: int) -> Dict:
        """Get Budget Allocation Analysis."""
        """
        Get budget allocation analysis for a specific account.
        """
        # Get total budgeted amount
        total_budgeted = self.db.query(
            func.sum(BudgetLine.amount)
        ).join(
            Budget,
            Budget.id == BudgetLine.budget_id
        ).filter(
            BudgetLine.account_id == account_id
        ).scalar()
        
        # Get department-wise allocation
        dept_allocations = self.db.query(
            BudgetAllocation.department_id,
            func.sum(BudgetAllocation.amount).label('amount')
        ).filter(
            BudgetAllocation.account_id == account_id
        ).group_by(
            BudgetAllocation.department_id
        ).all()
        
        # Get project-wise allocation
        proj_allocations = self.db.query(
            BudgetAllocation.project_id,
            func.sum(BudgetAllocation.amount).label('amount')
        ).filter(
            BudgetAllocation.account_id == account_id
        ).group_by(
            BudgetAllocation.project_id
        ).all()
        
        return {
            "total_budgeted": total_budgeted or 0,
            "department_allocations": [
                {
                    "department_id": dept_id,
                    "amount": amount,
                    "percentage": (amount / (total_budgeted or 1)) * 100
                }
                for dept_id, amount in dept_allocations
            ],
            "project_allocations": [
                {
                    "project_id": proj_id,
                    "amount": amount,
                    "percentage": (amount / (total_budgeted or 1)) * 100
                }
                for proj_id, amount in proj_allocations
            ]
        }

    def get_budget_variance_analysis(self) -> Dict:
        """Get Budget Variance Analysis."""
        """
        Get detailed budget variance analysis.
        """
        # Get all active budgets
        active_budgets = self.budget_service.get_active_budgets()
        
        result = {
            "overall": {
                "budgeted": 0,
                "actual": 0,
                "variance": 0,
                "variance_percentage": 0
            },
            "by_department": {},
            "by_project": {},
            "by_account": {}
        }
        
        for budget in active_budgets:
            # Calculate budgeted amount
            budgeted = sum(line.amount for line in budget.lines)
            
            # Calculate actual spending
            allocations = self.db.query(BudgetAllocation).filter(
                BudgetAllocation.budget_id == budget.id
            ).all()
            actual = sum(alloc.amount for alloc in allocations)
            
            # Update overall totals
            result["overall"]["budgeted"] += budgeted
            result["overall"]["actual"] += actual
            result["overall"]["variance"] = result["overall"]["budgeted"] - result["overall"]["actual"]
            result["overall"]["variance_percentage"] = \
                (result["overall"]["actual"] - result["overall"]["budgeted"]) / result["overall"]["budgeted"] * 100 \
                if result["overall"]["budgeted"] > 0 else 0
            
            # Update department totals
            if budget.department_id not in result["by_department"]:
                result["by_department"][budget.department_id] = {
                    "budgeted": 0,
                    "actual": 0,
                    "variance": 0,
                    "variance_percentage": 0
                }
            
            result["by_department"][budget.department_id]["budgeted"] += budgeted
            result["by_department"][budget.department_id]["actual"] += actual
            result["by_department"][budget.department_id]["variance"] = \
                result["by_department"][budget.department_id]["budgeted"] - \
                result["by_department"][budget.department_id]["actual"]
            result["by_department"][budget.department_id]["variance_percentage"] = \
                (result["by_department"][budget.department_id]["actual"] - 
                 result["by_department"][budget.department_id]["budgeted"]) / \
                result["by_department"][budget.department_id]["budgeted"] * 100 \
                if result["by_department"][budget.department_id]["budgeted"] > 0 else 0
            
            # Update project totals
            if budget.project_id not in result["by_project"]:
                result["by_project"][budget.project_id] = {
                    "budgeted": 0,
                    "actual": 0,
                    "variance": 0,
                    "variance_percentage": 0
                }
            
            result["by_project"][budget.project_id]["budgeted"] += budgeted
            result["by_project"][budget.project_id]["actual"] += actual
            result["by_project"][budget.project_id]["variance"] = \
                result["by_project"][budget.project_id]["budgeted"] - \
                result["by_project"][budget.project_id]["actual"]
            result["by_project"][budget.project_id]["variance_percentage"] = \
                (result["by_project"][budget.project_id]["actual"] - 
                 result["by_project"][budget.project_id]["budgeted"]) / \
                result["by_project"][budget.project_id]["budgeted"] * 100 \
                if result["by_project"][budget.project_id]["budgeted"] > 0 else 0
            
            # Update account totals
            for line in budget.lines:
                if line.account_id not in result["by_account"]:
                    result["by_account"][line.account_id] = {
                        "budgeted": 0,
                        "actual": 0,
                        "variance": 0,
                        "variance_percentage": 0
                    }
                
                result["by_account"][line.account_id]["budgeted"] += line.amount
                result["by_account"][line.account_id]["actual"] += \
                    sum(alloc.amount for alloc in allocations 
                        if alloc.account_id == line.account_id)
                result["by_account"][line.account_id]["variance"] = \
                    result["by_account"][line.account_id]["budgeted"] - \
                    result["by_account"][line.account_id]["actual"]
                result["by_account"][line.account_id]["variance_percentage"] = \
                    (result["by_account"][line.account_id]["actual"] - 
                     result["by_account"][line.account_id]["budgeted"]) / \
                    result["by_account"][line.account_id]["budgeted"] * 100 \
                    if result["by_account"][line.account_id]["budgeted"] > 0 else 0
        
        return result
