"""
Benefits management service for the Payroll module.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status

from app.models.employee import Employee
from app.models.benefits import BenefitPlan, EmployeeBenefit
from app.modules.core_financials.payroll.schemas.benefits import (
    BenefitPlanCreate, BenefitPlanUpdate, EmployeeBenefitEnrollment,
    BenefitsSummary
)


class BenefitsService:
    """Service for benefits management operations."""
    
    @staticmethod
    def create_benefit_plan(db: Session, plan_data: BenefitPlanCreate) -> Dict[str, Any]:
        """Create a new benefit plan."""
        # Check if plan with same name already exists
        existing_plan = db.query(BenefitPlan).filter(
            BenefitPlan.name == plan_data.name
        ).first()
        
        if existing_plan:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Benefit plan with this name already exists"
            )
        
        benefit_plan = BenefitPlan(
            name=plan_data.name,
            benefit_type=plan_data.benefit_type,
            description=plan_data.description,
            provider=plan_data.provider,
            employee_cost=plan_data.employee_cost,
            employer_cost=plan_data.employer_cost,
            deduction_type=plan_data.deduction_type,
            is_active=plan_data.is_active
        )
        
        db.add(benefit_plan)
        db.commit()
        db.refresh(benefit_plan)
        
        return {
            "id": benefit_plan.id,
            "name": benefit_plan.name,
            "benefit_type": benefit_plan.benefit_type,
            "description": benefit_plan.description,
            "provider": benefit_plan.provider,
            "employee_cost": benefit_plan.employee_cost,
            "employer_cost": benefit_plan.employer_cost,
            "deduction_type": benefit_plan.deduction_type,
            "is_active": benefit_plan.is_active,
            "enrolled_count": 0,
            "created_at": benefit_plan.created_at,
            "updated_at": benefit_plan.updated_at
        }
    
    @staticmethod
    def get_benefit_plans(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        benefit_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get benefit plans with optional filtering."""
        query = db.query(BenefitPlan)
        
        if benefit_type:
            query = query.filter(BenefitPlan.benefit_type == benefit_type)
        
        if is_active is not None:
            query = query.filter(BenefitPlan.is_active == is_active)
        
        total = query.count()
        plans = query.offset(skip).limit(limit).all()
        
        # Get enrollment counts for each plan
        result_plans = []
        for plan in plans:
            enrolled_count = db.query(EmployeeBenefit).filter(
                and_(
                    EmployeeBenefit.benefit_plan_id == plan.id,
                    EmployeeBenefit.is_active == True
                )
            ).count()
            
            result_plans.append({
                "id": plan.id,
                "name": plan.name,
                "benefit_type": plan.benefit_type,
                "description": plan.description,
                "provider": plan.provider,
                "employee_cost": plan.employee_cost,
                "employer_cost": plan.employer_cost,
                "deduction_type": plan.deduction_type,
                "is_active": plan.is_active,
                "enrolled_count": enrolled_count,
                "created_at": plan.created_at,
                "updated_at": plan.updated_at
            })
        
        return {
            "items": result_plans,
            "total": total
        }
    
    @staticmethod
    def get_benefit_plan_by_id(db: Session, plan_id: UUID) -> Dict[str, Any]:
        """Get a benefit plan by ID."""
        plan = db.query(BenefitPlan).filter(BenefitPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Benefit plan not found"
            )
        
        enrolled_count = db.query(EmployeeBenefit).filter(
            and_(
                EmployeeBenefit.benefit_plan_id == plan_id,
                EmployeeBenefit.is_active == True
            )
        ).count()
        
        return {
            "id": plan.id,
            "name": plan.name,
            "benefit_type": plan.benefit_type,
            "description": plan.description,
            "provider": plan.provider,
            "employee_cost": plan.employee_cost,
            "employer_cost": plan.employer_cost,
            "deduction_type": plan.deduction_type,
            "is_active": plan.is_active,
            "enrolled_count": enrolled_count,
            "created_at": plan.created_at,
            "updated_at": plan.updated_at
        }
    
    @staticmethod
    def update_benefit_plan(
        db: Session,
        plan_id: UUID,
        plan_data: BenefitPlanUpdate
    ) -> Dict[str, Any]:
        """Update a benefit plan."""
        plan = db.query(BenefitPlan).filter(BenefitPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Benefit plan not found"
            )
        
        # Check for name conflicts if updating name
        if plan_data.name and plan_data.name != plan.name:
            existing_plan = db.query(BenefitPlan).filter(
                and_(
                    BenefitPlan.name == plan_data.name,
                    BenefitPlan.id != plan_id
                )
            ).first()
            
            if existing_plan:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Benefit plan with this name already exists"
                )
        
        # Update plan data
        update_data = plan_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(plan, key, value)
        
        db.commit()
        db.refresh(plan)
        
        return BenefitsService.get_benefit_plan_by_id(db, plan_id)
    
    @staticmethod
    def delete_benefit_plan(db: Session, plan_id: UUID) -> None:
        """Delete a benefit plan."""
        plan = db.query(BenefitPlan).filter(BenefitPlan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Benefit plan not found"
            )
        
        # Check if plan has active enrollments
        active_enrollments = db.query(EmployeeBenefit).filter(
            and_(
                EmployeeBenefit.benefit_plan_id == plan_id,
                EmployeeBenefit.is_active == True
            )
        ).count()
        
        if active_enrollments > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete benefit plan with active enrollments"
            )
        
        db.delete(plan)
        db.commit()
    
    @staticmethod
    def enroll_employee(
        db: Session,
        enrollment_data: EmployeeBenefitEnrollment
    ) -> Dict[str, Any]:
        """Enroll an employee in a benefit plan."""
        # Verify employee exists
        employee = db.query(Employee).filter(
            Employee.id == enrollment_data.employee_id
        ).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Verify benefit plan exists
        plan = db.query(BenefitPlan).filter(
            BenefitPlan.id == enrollment_data.benefit_plan_id
        ).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Benefit plan not found"
            )
        
        # Check if employee is already enrolled in this plan
        existing_enrollment = db.query(EmployeeBenefit).filter(
            and_(
                EmployeeBenefit.employee_id == enrollment_data.employee_id,
                EmployeeBenefit.benefit_plan_id == enrollment_data.benefit_plan_id,
                EmployeeBenefit.is_active == True
            )
        ).first()
        
        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee is already enrolled in this benefit plan"
            )
        
        # Create enrollment
        enrollment = EmployeeBenefit(
            employee_id=enrollment_data.employee_id,
            benefit_plan_id=enrollment_data.benefit_plan_id,
            enrollment_date=enrollment_data.enrollment_date,
            effective_date=enrollment_data.effective_date,
            end_date=enrollment_data.end_date,
            employee_contribution=enrollment_data.employee_contribution,
            employer_contribution=enrollment_data.employer_contribution,
            is_active=enrollment_data.is_active
        )
        
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        
        return {
            "id": enrollment.id,
            "employee_id": enrollment.employee_id,
            "employee_name": employee.full_name,
            "benefit_plan_id": enrollment.benefit_plan_id,
            "benefit_plan_name": plan.name,
            "benefit_type": plan.benefit_type,
            "enrollment_date": enrollment.enrollment_date,
            "effective_date": enrollment.effective_date,
            "end_date": enrollment.end_date,
            "employee_contribution": enrollment.employee_contribution,
            "employer_contribution": enrollment.employer_contribution,
            "deduction_type": plan.deduction_type,
            "is_active": enrollment.is_active
        }
    
    @staticmethod
    def get_employee_benefits(
        db: Session,
        employee_id: UUID,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get benefits for a specific employee."""
        query = db.query(EmployeeBenefit, BenefitPlan, Employee).join(
            BenefitPlan, EmployeeBenefit.benefit_plan_id == BenefitPlan.id
        ).join(
            Employee, EmployeeBenefit.employee_id == Employee.id
        ).filter(EmployeeBenefit.employee_id == employee_id)
        
        if is_active is not None:
            query = query.filter(EmployeeBenefit.is_active == is_active)
        
        results = query.all()
        
        benefits = []
        for enrollment, plan, employee in results:
            benefits.append({
                "id": enrollment.id,
                "employee_id": enrollment.employee_id,
                "employee_name": employee.full_name,
                "benefit_plan_id": enrollment.benefit_plan_id,
                "benefit_plan_name": plan.name,
                "benefit_type": plan.benefit_type,
                "enrollment_date": enrollment.enrollment_date,
                "effective_date": enrollment.effective_date,
                "end_date": enrollment.end_date,
                "employee_contribution": enrollment.employee_contribution,
                "employer_contribution": enrollment.employer_contribution,
                "deduction_type": plan.deduction_type,
                "is_active": enrollment.is_active
            })
        
        return benefits
    
    @staticmethod
    def terminate_enrollment(
        db: Session,
        enrollment_id: UUID,
        end_date: date
    ) -> Dict[str, Any]:
        """Terminate an employee's benefit enrollment."""
        enrollment = db.query(EmployeeBenefit).filter(
            EmployeeBenefit.id == enrollment_id
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Benefit enrollment not found"
            )
        
        enrollment.end_date = end_date
        enrollment.is_active = False
        
        db.commit()
        db.refresh(enrollment)
        
        return {"message": "Benefit enrollment terminated successfully"}
    
    @staticmethod
    def get_benefits_summary(db: Session) -> BenefitsSummary:
        """Get benefits summary statistics."""
        total_plans = db.query(BenefitPlan).count()
        active_plans = db.query(BenefitPlan).filter(BenefitPlan.is_active == True).count()
        total_enrollments = db.query(EmployeeBenefit).filter(
            EmployeeBenefit.is_active == True
        ).count()
        
        # Calculate total costs
        employee_cost_sum = db.query(func.sum(EmployeeBenefit.employee_contribution)).filter(
            EmployeeBenefit.is_active == True
        ).scalar() or Decimal("0.00")
        
        employer_cost_sum = db.query(func.sum(EmployeeBenefit.employer_contribution)).filter(
            EmployeeBenefit.is_active == True
        ).scalar() or Decimal("0.00")
        
        # Get breakdown by benefit type
        by_type_query = db.query(
            BenefitPlan.benefit_type,
            func.count(EmployeeBenefit.id).label('count')
        ).join(
            EmployeeBenefit, BenefitPlan.id == EmployeeBenefit.benefit_plan_id
        ).filter(
            EmployeeBenefit.is_active == True
        ).group_by(BenefitPlan.benefit_type).all()
        
        by_type = {benefit_type: count for benefit_type, count in by_type_query}
        
        return BenefitsSummary(
            total_plans=total_plans,
            active_plans=active_plans,
            total_enrollments=total_enrollments,
            total_employee_cost=employee_cost_sum,
            total_employer_cost=employer_cost_sum,
            by_type=by_type
        )