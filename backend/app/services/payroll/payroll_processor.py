"""
Payroll processor service that handles the core payroll processing logic.
"""
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from ..models.payroll_models import (
from ..schemas.payroll_schemas import (
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from sqlalchemy import and_, or_, func, select
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import logger




    Employee, PayPeriod, PayRun, Payslip, PayslipEarning, PayslipDeduction,
    PayslipTax, PayslipBenefit, PayComponent, PayComponentType, PaySchedule,
    TaxCode, BenefitPlan, BenefitEnrollment, LeaveRequest, AttendanceRecord,
    BankAccount, PayRunStatus, PayFrequency, EmploymentType, PayRunStatus
)
    PayRunCreate, PayRunUpdate, PayRunResponse, PayslipResponse,
    PayslipEarningResponse, PayslipDeductionResponse, PayslipTaxResponse,
    PayslipBenefitResponse, PayrollProcessingRequest, PayrollProcessingResult,
    PayrollCalculationResult, PayrollEarningItem, PayrollDeductionItem,
    PayrollTaxItem, PayrollBenefitItem, PayrollNetPayCalculation
)

class PayrollProcessor:
    """
    Core payroll processing service that handles the payroll calculation logic.
    """
    
    def __init__(self, db: Session):
        """  Init  ."""
        """Initialize the payroll processor with a database session."""
        self.db = db
    
    def initialize_pay_run(
        self,
        pay_period_id: UUID,
        created_by: UUID,
        company_id: UUID,
        process_taxes: bool = True,
        process_benefits: bool = True,
        dry_run: bool = False
    ) -> PayRun:
        """Initialize Pay Run."""
        """
        Initialize a new pay run for the specified pay period.
        
        Args:
            pay_period_id: ID of the pay period to process
            created_by: ID of the user creating the pay run
            company_id: ID of the company
            process_taxes: Whether to calculate taxes
            process_benefits: Whether to process benefits
            dry_run: If True, validate but don't save to database
            
        Returns:
            The created PayRun object
            
        Raises:
            AppException: If pay period is not found or already processed
        """
        # Get the pay period
        pay_period = self.db.query(PayPeriod).filter(
            PayPeriod.id == pay_period_id,
            PayPeriod.company_id == company_id
        ).first()
        
        if not pay_period:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"Pay period {pay_period_id} not found"
            )
            
        # Check if pay period is already processed
        existing_run = self.db.query(PayRun).filter(
            PayRun.pay_period_id == pay_period_id,
            PayRun.status.in_([PayRunStatus.PROCESSING, PayRunStatus.COMPLETED])
        ).first()
        
        if existing_run:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Pay period {pay_period_id} already has a pay run in progress or completed"
            )
        
        # Create the pay run
        pay_run = PayRun(
            pay_period_id=pay_period_id,
            company_id=company_id,
            status=PayRunStatus.DRAFT if dry_run else PayRunStatus.PROCESSING,
            process_taxes=process_taxes,
            process_benefits=process_benefits,
            created_by=created_by,
            processed_at=datetime.utcnow() if not dry_run else None,
            is_dry_run=dry_run
        )
        
        if not dry_run:
            self.db.add(pay_run)
            self.db.commit()
            self.db.refresh(pay_run)
        
        return pay_run
    
    def process_pay_run(
        self,
        pay_run_id: UUID,
        processed_by: UUID,
        employee_ids: Optional[List[UUID]] = None,
        recalculate: bool = False
    ) -> PayRun:
        """Process Pay Run."""
        """
        Process a pay run by calculating payslips for all eligible employees.
        
        Args:
            pay_run_id: ID of the pay run to process
            processed_by: ID of the user processing the pay run
            employee_ids: Optional list of employee IDs to process (all eligible if None)
            recalculate: If True, recalculate existing payslips
            
        Returns:
            The updated PayRun object
            
        Raises:
            AppException: If pay run is not found or already completed
        """
        # Get the pay run with related data
        pay_run = self.db.query(PayRun).filter(
            PayRun.id == pay_run_id
        ).options(
            joinedload(PayRun.pay_period)
        ).first()
        
        if not pay_run:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"Pay run {pay_run_id} not found"
            )
            
        if pay_run.status == PayRunStatus.COMPLETED and not recalculate:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Pay run {pay_run_id} is already completed"
            )
        
        try:
            # Update pay run status to processing
            pay_run.status = PayRunStatus.PROCESSING
            pay_run.processed_by = processed_by
            pay_run.processed_at = datetime.utcnow()
            self.db.commit()
            
            # This is a placeholder - actual implementation will process each employee
            
            # Update pay run status to completed
            pay_run.status = PayRunStatus.COMPLETED
            pay_run.completed_at = datetime.utcnow()
            self.db.commit()
            
            return pay_run
            
        except Exception as e:
            # Update pay run status to failed
            pay_run.status = PayRunStatus.FAILED
            pay_run.error_message = str(e)
            self.db.commit()
            
            logger.error(f"Error processing pay run {pay_run_id}: {str(e)}", exc_info=True)
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to process pay run: {str(e)}"
            )
    
    def _get_eligible_employees(
        self,
        company_id: UUID,
        pay_period: PayPeriod,
        employee_ids: Optional[List[UUID]] = None
    ) -> List[Employee]:
        """ Get Eligible Employees."""
        """
        Get list of employees eligible for payroll processing.
        
        Args:
            company_id: ID of the company
            pay_period: The pay period
            employee_ids: Optional list of employee IDs to filter by
            
        Returns:
            List of eligible Employee objects
        """
        query = self.db.query(Employee).filter(
            Employee.company_id == company_id,
            Employee.is_active == True,
            Employee.hire_date <= pay_period.end_date,
            or_(
                Employee.termination_date.is_(None),
                Employee.termination_date >= pay_period.start_date
            )
        )
        
        if employee_ids:
            query = query.filter(Employee.id.in_(employee_ids))
            
        return query.all()
    
    def _calculate_employee_pay(
        self,
        employee: Employee,
        pay_period: PayPeriod,
        pay_run: PayRun
    ) -> Dict:
        """ Calculate Employee Pay."""
        """
        Calculate pay for a single employee for the pay period.
        
        Args:
            employee: The employee
            pay_period: The pay period
            pay_run: The pay run
            
        Returns:
            Dictionary containing pay calculation results
        """
        # This is a placeholder - actual implementation will calculate:
        # - Regular hours and pay
        # - Overtime hours and pay
        # - Bonuses and other earnings
        # - Deductions (pre-tax and post-tax)
        # - Tax calculations
        # - Net pay
        
        return {
            "employee_id": employee.id,
            "regular_hours": Decimal("80.00"),
            "overtime_hours": Decimal("0.00"),
            "regular_pay": employee.base_salary / 26 if employee.pay_frequency == PayFrequency.BI_WEEKLY else employee.base_salary / 12,
            "overtime_pay": Decimal("0.00"),
            "gross_pay": employee.base_salary / 26 if employee.pay_frequency == PayFrequency.BI_WEEKLY else employee.base_salary / 12,
            "deductions": [],
            "taxes": [],
            "benefits": [],
            "net_pay": Decimal("0.00")
        }
