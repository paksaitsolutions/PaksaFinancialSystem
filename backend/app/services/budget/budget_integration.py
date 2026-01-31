from datetime import datetime
from typing import List, Optional

from ..models import Budget, BudgetLine, BudgetAllocation
from ..schemas import BudgetCreate, BudgetUpdate, BudgetStatus
from .ap import APService
from .ar import ARService
from .budget import BudgetService
from .gl import GLService
from .payroll import PayrollService
from .procurement import ProcurementService
from fastapi import HTTPException
from sqlalchemy.orm import Session


class BudgetIntegrationService:
    def __init__(
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

    def check_budget_availability(
        self,
        account_id: int,
        amount: float,
        department_id: Optional[int] = None,
        project_id: Optional[int] = None,
        date: Optional[datetime] = None
    ) -> bool:
        """Check Budget Availability."""
        """
        Check if the requested amount is available in the budget for the given account, department, and project.
        """
        if not date:
            date = datetime.now()

        # Get active budgets for the given date
        active_budgets = self.budget_service.get_active_budgets(date)

        # Calculate total available budget for the account
        total_available = 0
        for budget in active_budgets:
            # Get budget lines for the account
            lines = [line for line in budget.lines if line.account_id == account_id]
            if not lines:
                continue

            # Calculate available amount based on department/project allocations
            available_amount = lines[0].amount
            if department_id or project_id:
                allocations = [alloc for alloc in budget.allocations 
                             if (alloc.department_id == department_id or alloc.project_id == project_id)]
                if allocations:
                    available_amount = sum(alloc.amount for alloc in allocations)

            total_available += available_amount

        return total_available >= amount

    def allocate_budget(
        self,
        budget_id: int,
        amount: float,
        account_id: int,
        department_id: Optional[int] = None,
        project_id: Optional[int] = None,
        description: str = ""
    ) -> BudgetAllocation:
        """Allocate Budget."""
        """
        Create a budget allocation for a transaction.
        """
        allocation = BudgetAllocation(
            budget_id=budget_id,
            amount=amount,
            account_id=account_id,
            department_id=department_id,
            project_id=project_id,
            description=description
        )
        self.db.add(allocation)
        self.db.commit()
        self.db.refresh(allocation)
        return allocation

    def update_gl_entry_budget_allocation(
        self,
        gl_entry_id: int,
        budget_id: int,
        amount: float,
        department_id: Optional[int] = None,
        project_id: Optional[int] = None
    ):
        """Update Gl Entry Budget Allocation."""
        """
        Update GL entry with budget allocation information.
        """
        gl_entry = self.gl_service.get_gl_entry(gl_entry_id)
        if not gl_entry:
            raise HTTPException(status_code=404, detail="GL Entry not found")

        allocation = self.allocate_budget(
            budget_id=budget_id,
            amount=amount,
            account_id=gl_entry.account_id,
            department_id=department_id,
            project_id=project_id
        )

        gl_entry.budget_allocation_id = allocation.id
        self.db.commit()
        return gl_entry

    def update_ap_invoice_budget_allocation(
        self,
        invoice_id: int,
        budget_id: int,
        amount: float,
        department_id: Optional[int] = None,
        project_id: Optional[int] = None
    ):
        """Update Ap Invoice Budget Allocation."""
        """
        Update AP invoice with budget allocation information.
        """
        invoice = self.ap_service.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="AP Invoice not found")

        allocation = self.allocate_budget(
            budget_id=budget_id,
            amount=amount,
            account_id=invoice.account_id,
            department_id=department_id,
            project_id=project_id
        )

        invoice.budget_allocation_id = allocation.id
        self.db.commit()
        return invoice

    def update_ar_invoice_budget_allocation(
        self,
        invoice_id: int,
        budget_id: int,
        amount: float,
        department_id: Optional[int] = None,
        project_id: Optional[int] = None
    ):
        """Update Ar Invoice Budget Allocation."""
        """
        Update AR invoice with budget allocation information.
        """
        invoice = self.ar_service.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="AR Invoice not found")

        allocation = self.allocate_budget(
            budget_id=budget_id,
            amount=amount,
            account_id=invoice.account_id,
            department_id=department_id,
            project_id=project_id
        )

        invoice.budget_allocation_id = allocation.id
        self.db.commit()
        return invoice

    def update_purchase_order_budget_allocation(
        self,
        po_id: int,
        budget_id: int,
        amount: float,
        department_id: Optional[int] = None,
        project_id: Optional[int] = None
    ):
        """Update Purchase Order Budget Allocation."""
        """
        Update Purchase Order with budget allocation information.
        """
        po = self.procurement_service.get_purchase_order(po_id)
        if not po:
            raise HTTPException(status_code=404, detail="Purchase Order not found")

        allocation = self.allocate_budget(
            budget_id=budget_id,
            amount=amount,
            account_id=po.account_id,
            department_id=department_id,
            project_id=project_id
        )

        po.budget_allocation_id = allocation.id
        self.db.commit()
        return po

    def update_payroll_entry_budget_allocation(
        self,
        payroll_id: int,
        budget_id: int,
        amount: float,
        department_id: Optional[int] = None,
        project_id: Optional[int] = None
    ):
        """Update Payroll Entry Budget Allocation."""
        """
        Update Payroll entry with budget allocation information.
        """
        payroll = self.payroll_service.get_payroll(payroll_id)
        if not payroll:
            raise HTTPException(status_code=404, detail="Payroll entry not found")

        allocation = self.allocate_budget(
            budget_id=budget_id,
            amount=amount,
            account_id=payroll.account_id,
            department_id=department_id,
            project_id=project_id
        )

        payroll.budget_allocation_id = allocation.id
        self.db.commit()
        return payroll

    def get_budget_spending_report(
        self,
        account_id: int,
        department_id: Optional[int] = None,
        project_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        """Get Budget Spending Report."""
        """
        Get budget spending report for a specific account, department, and project.
        """
        # Get active budgets
        active_budgets = self.budget_service.get_active_budgets(
            start_date or datetime.now()
        )

        # Get related allocations
        allocations = self.db.query(BudgetAllocation).filter(
            BudgetAllocation.account_id == account_id,
            BudgetAllocation.department_id == department_id if department_id else True,
            BudgetAllocation.project_id == project_id if project_id else True,
            BudgetAllocation.created_at.between(start_date, end_date) if start_date and end_date else True
        ).all()

        # Calculate spending vs budget
        total_budget = sum(
            line.amount for budget in active_budgets 
            for line in budget.lines 
            if line.account_id == account_id
        )

        total_spent = sum(allocation.amount for allocation in allocations)

        return {
            "account_id": account_id,
            "department_id": department_id,
            "project_id": project_id,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining_budget": total_budget - total_spent,
            "percentage_spent": (total_spent / total_budget) * 100 if total_budget > 0 else 0
        }
