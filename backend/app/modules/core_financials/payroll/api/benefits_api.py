"""
Benefits management API endpoints for the Payroll module.
"""
from typing import Optional, List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.core_financials.payroll.schemas.benefits import (
    BenefitPlanCreate, BenefitPlanUpdate, BenefitPlanResponse,
    EmployeeBenefitEnrollment, EmployeeBenefitResponse, BenefitsSummary
)
from app.modules.core_financials.payroll.services.benefits_service import BenefitsService

router = APIRouter(prefix="/benefits", tags=["benefits"])


@router.post("/plans", response_model=BenefitPlanResponse, status_code=status.HTTP_201_CREATED)
def create_benefit_plan(
    plan: BenefitPlanCreate,
    db: Session = Depends(get_db)
):
    """Create a new benefit plan."""
    return BenefitsService.create_benefit_plan(db=db, plan_data=plan)


@router.get("/plans")
def get_benefit_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    benefit_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get benefit plans with optional filtering."""
    return BenefitsService.get_benefit_plans(
        db=db,
        skip=skip,
        limit=limit,
        benefit_type=benefit_type,
        is_active=is_active
    )


@router.get("/plans/{plan_id}", response_model=BenefitPlanResponse)
def get_benefit_plan(plan_id: UUID, db: Session = Depends(get_db)):
    """Get a specific benefit plan."""
    return BenefitsService.get_benefit_plan_by_id(db=db, plan_id=plan_id)


@router.put("/plans/{plan_id}", response_model=BenefitPlanResponse)
def update_benefit_plan(
    plan_id: UUID,
    plan: BenefitPlanUpdate,
    db: Session = Depends(get_db)
):
    """Update a benefit plan."""
    return BenefitsService.update_benefit_plan(
        db=db,
        plan_id=plan_id,
        plan_data=plan
    )


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_benefit_plan(plan_id: UUID, db: Session = Depends(get_db)):
    """Delete a benefit plan."""
    BenefitsService.delete_benefit_plan(db=db, plan_id=plan_id)
    return None


@router.post("/enrollments", response_model=EmployeeBenefitResponse, status_code=status.HTTP_201_CREATED)
def enroll_employee(
    enrollment: EmployeeBenefitEnrollment,
    db: Session = Depends(get_db)
):
    """Enroll an employee in a benefit plan."""
    return BenefitsService.enroll_employee(db=db, enrollment_data=enrollment)


@router.get("/employees/{employee_id}/benefits")
def get_employee_benefits(
    employee_id: UUID,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get benefits for a specific employee."""
    return BenefitsService.get_employee_benefits(
        db=db,
        employee_id=employee_id,
        is_active=is_active
    )


@router.put("/enrollments/{enrollment_id}/terminate")
def terminate_enrollment(
    enrollment_id: UUID,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Terminate an employee's benefit enrollment."""
    return BenefitsService.terminate_enrollment(
        db=db,
        enrollment_id=enrollment_id,
        end_date=end_date
    )


@router.get("/summary", response_model=BenefitsSummary)
def get_benefits_summary(db: Session = Depends(get_db)):
    """Get benefits summary statistics."""
    return BenefitsService.get_benefits_summary(db=db)


@router.get("/types")
def get_benefit_types():
    """Get available benefit types."""
    from app.modules.core_financials.payroll.schemas.benefits import BenefitTypeEnum
    return [{"value": item.value, "label": item.value.replace("_", " ").title()} for item in BenefitTypeEnum]


@router.get("/deduction-types")
def get_deduction_types():
    """Get available deduction types."""
    from app.modules.core_financials.payroll.schemas.benefits import DeductionTypeEnum
    return [{"value": item.value, "label": item.value.replace("_", " ").title()} for item in DeductionTypeEnum]