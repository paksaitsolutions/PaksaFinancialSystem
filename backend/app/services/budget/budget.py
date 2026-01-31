from datetime import datetime
from typing import List, Optional, Dict, Any

from ..core.exceptions import BudgetException
from ..models.account import Account
from ..models.budget import (
from ..models.department import Department
from ..models.project import Project
from ..schemas.budget import (
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session


    Budget,
    BudgetLine,
    BudgetAllocation,
    BudgetApproval,
    BudgetRule
)
    BudgetCreate,
    BudgetUpdate,
    BudgetApprovalCreate,
    BudgetResponse,
    BudgetListResponse
)

class BudgetService:
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db

    def create_budget(self, budget_data: BudgetCreate, current_user: str) -> BudgetResponse:
        """Create Budget."""
        try:
            # Validate dates
            if budget_data.start_date >= budget_data.end_date:
                raise BudgetException("Start date must be before end date")

            # Create budget
            budget = Budget(
                name=budget_data.name,
                description=budget_data.description,
                budget_type=budget_data.budget_type,
                status=BudgetStatus.DRAFT,
                start_date=budget_data.start_date,
                end_date=budget_data.end_date,
                total_amount=budget_data.total_amount,
                created_by=current_user
            )

            # Validate and create lines
            total_line_amount = 0
            lines = []
            for line_data in budget_data.lines:
                # Validate account exists
                account = self.db.query(Account).filter(Account.id == line_data.account_id).first()
                if not account:
                    raise BudgetException(f"Account {line_data.account_id} not found")

                # Validate department if provided
                if line_data.department_id:
                    department = self.db.query(Department).filter(Department.id == line_data.department_id).first()
                    if not department:
                        raise BudgetException(f"Department {line_data.department_id} not found")

                # Validate project if provided
                if line_data.project_id:
                    project = self.db.query(Project).filter(Project.id == line_data.project_id).first()
                    if not project:
                        raise BudgetException(f"Project {line_data.project_id} not found")

                line = BudgetLine(**line_data.dict())
                lines.append(line)
                total_line_amount += line.amount

            # Validate total amount matches lines
            if abs(budget.total_amount - total_line_amount) > 0.01:  # Allow small floating point difference
                raise BudgetException("Total amount does not match sum of budget lines")

            budget.lines = lines

            # Create allocations
            allocations = []
            total_allocation_amount = 0
            for alloc_data in budget_data.allocations:
                # Validate department or project
                if not alloc_data.department_id and not alloc_data.project_id:
                    raise BudgetException("Allocation must specify either department or project")

                if alloc_data.department_id:
                    department = self.db.query(Department).filter(Department.id == alloc_data.department_id).first()
                    if not department:
                        raise BudgetException(f"Department {alloc_data.department_id} not found")

                if alloc_data.project_id:
                    project = self.db.query(Project).filter(Project.id == alloc_data.project_id).first()
                    if not project:
                        raise BudgetException(f"Project {alloc_data.project_id} not found")

                # Calculate amount if percentage provided
                if alloc_data.percentage is not None:
                    alloc_data.amount = budget.total_amount * (alloc_data.percentage / 100)

                allocation = BudgetAllocation(**alloc_data.dict())
                allocations.append(allocation)
                total_allocation_amount += allocation.amount

            # Validate allocations match total
            if abs(budget.total_amount - total_allocation_amount) > 0.01:
                raise BudgetException("Total allocation amount does not match budget total")

            budget.allocations = allocations

            # Create rules
            rules = []
            for rule_data in budget_data.rules:
                rule = BudgetRule(**rule_data.dict())
                rules.append(rule)

            budget.rules = rules

            self.db.add(budget)
            self.db.commit()
            self.db.refresh(budget)
            
            return budget

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def get_budget(self, budget_id: int) -> Optional[BudgetResponse]:
        """Get Budget."""
        budget = self.db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget

    def list_budgets(self, skip: int = 0, limit: int = 100) -> BudgetListResponse:
        """List Budgets."""
        total = self.db.query(func.count(Budget.id)).scalar()
        budgets = self.db.query(Budget).offset(skip).limit(limit).all()
        return BudgetListResponse(budgets=budgets, total=total, page=skip // limit + 1, limit=limit)

    def update_budget(self, budget_id: int, budget_data: BudgetUpdate, current_user: str) -> BudgetResponse:
        """Update Budget."""
        budget = self.db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        if budget.status != BudgetStatus.DRAFT:
            raise BudgetException("Cannot update non-draft budget")

        # Update basic fields
        for field, value in budget_data.dict(exclude_unset=True).items():
            setattr(budget, field, value)

        budget.updated_by = current_user

        # Update lines if provided
        if budget_data.lines is not None:
            budget.lines = []
            total_line_amount = 0
            for line_data in budget_data.lines:
                line = BudgetLine(**line_data.dict())
                budget.lines.append(line)
                total_line_amount += line.amount

            if abs(budget.total_amount - total_line_amount) > 0.01:
                raise BudgetException("Total amount does not match sum of budget lines")

        # Update allocations if provided
        if budget_data.allocations is not None:
            budget.allocations = []
            total_allocation_amount = 0
            for alloc_data in budget_data.allocations:
                allocation = BudgetAllocation(**alloc_data.dict())
                budget.allocations.append(allocation)
                total_allocation_amount += allocation.amount

            if abs(budget.total_amount - total_allocation_amount) > 0.01:
                raise BudgetException("Total allocation amount does not match budget total")

        # Update rules if provided
        if budget_data.rules is not None:
            budget.rules = []
            for rule_data in budget_data.rules:
                rule = BudgetRule(**rule_data.dict())
                budget.rules.append(rule)

        self.db.commit()
        self.db.refresh(budget)
        return budget

    def approve_budget(self, budget_id: int, approval_data: BudgetApprovalCreate, current_user: str) -> BudgetResponse:
        """Approve Budget."""
        budget = self.db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        if budget.status != BudgetStatus.DRAFT:
            raise BudgetException("Cannot approve non-draft budget")

        # Check if already approved
        existing_approval = self.db.query(BudgetApproval).filter(
            BudgetApproval.budget_id == budget_id,
            BudgetApproval.approver_id == current_user
        ).first()

        if existing_approval:
            raise BudgetException("Budget already approved by this user")

        # Create approval
        approval = BudgetApproval(
            budget_id=budget_id,
            approver_id=current_user,
            notes=approval_data.notes
        )
        self.db.add(approval)

        # Check if all required approvals are met
        required_approvals = self._get_required_approvals(budget)
        current_approvals = self.db.query(BudgetApproval).filter(
            BudgetApproval.budget_id == budget_id
        ).count()

        if current_approvals >= required_approvals:
            budget.status = BudgetStatus.APPROVED

        self.db.commit()
        self.db.refresh(budget)
        return budget

    def reject_budget(self, budget_id: int, current_user: str, notes: str) -> BudgetResponse:
        """Reject Budget."""
        budget = self.db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        if budget.status != BudgetStatus.DRAFT:
            raise BudgetException("Cannot reject non-draft budget")

        budget.status = BudgetStatus.REJECTED
        approval = BudgetApproval(
            budget_id=budget_id,
            approver_id=current_user,
            notes=notes
        )
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def archive_budget(self, budget_id: int, current_user: str) -> BudgetResponse:
        """Archive Budget."""
        budget = self.db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        if budget.status not in [BudgetStatus.APPROVED, BudgetStatus.REJECTED]:
            raise BudgetException("Cannot archive budget that is not approved or rejected")

        budget.status = BudgetStatus.ARCHIVED
        budget.updated_by = current_user
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def _get_required_approvals(self, budget: Budget) -> int:
        """ Get Required Approvals."""
        """Determine required number of approvals based on budget rules"""
        required_approvals = 1  # Default minimum
        for rule in budget.rules:
            if rule.rule_type == "approval_threshold":
                threshold = rule.rule_data.get("threshold", 0)
                if budget.total_amount >= threshold:
                    required_approvals = rule.rule_data.get("required_approvals", required_approvals)
        return required_approvals
