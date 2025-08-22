"""
Payroll processing service for the Payroll module.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status

from app.models.employee import Employee
from app.models.payslip import Payslip
from app.models.pay_period import PayPeriod
from app.modules.core_financials.payroll.schemas.payroll_processing import (
    PayrollRunCreate, PayrollRunUpdate, PayrollCalculationRequest,
    PayslipCreate, PayrollSummary
)


class PayrollProcessingService:
    """Service for payroll processing operations."""
    
    @staticmethod
    def create_payroll_run(db: Session, payroll_data: PayrollRunCreate) -> Dict[str, Any]:
        """Create a new payroll run."""
        # Check if payroll run already exists for this period
        existing_run = db.query(PayPeriod).filter(
            and_(
                PayPeriod.start_date == payroll_data.pay_period_start,
                PayPeriod.end_date == payroll_data.pay_period_end
            )
        ).first()
        
        if existing_run:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payroll run already exists for this period"
            )
        
        # Create new payroll run
        payroll_run = PayPeriod(
            start_date=payroll_data.pay_period_start,
            end_date=payroll_data.pay_period_end,
            pay_date=payroll_data.pay_date,
            description=payroll_data.description,
            status="DRAFT"
        )
        
        db.add(payroll_run)
        db.commit()
        db.refresh(payroll_run)
        
        return {
            "id": payroll_run.id,
            "pay_period_start": payroll_run.start_date,
            "pay_period_end": payroll_run.end_date,
            "pay_date": payroll_run.pay_date,
            "description": payroll_run.description,
            "status": payroll_run.status,
            "total_gross_pay": Decimal("0.00"),
            "total_net_pay": Decimal("0.00"),
            "total_deductions": Decimal("0.00"),
            "employee_count": 0,
            "created_at": payroll_run.created_at,
            "updated_at": payroll_run.updated_at
        }
    
    @staticmethod
    def get_payroll_runs(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get payroll runs with optional filtering."""
        query = db.query(PayPeriod)
        
        if status:
            query = query.filter(PayPeriod.status == status)
        
        total = query.count()
        runs = query.offset(skip).limit(limit).all()
        
        # Calculate totals for each run
        result_runs = []
        for run in runs:
            payslips = db.query(Payslip).filter(Payslip.pay_period_id == run.id).all()
            
            total_gross = sum(p.gross_pay for p in payslips)
            total_net = sum(p.net_pay for p in payslips)
            total_deductions = sum(p.total_deductions for p in payslips)
            
            result_runs.append({
                "id": run.id,
                "pay_period_start": run.start_date,
                "pay_period_end": run.end_date,
                "pay_date": run.pay_date,
                "description": run.description,
                "status": run.status,
                "total_gross_pay": total_gross,
                "total_net_pay": total_net,
                "total_deductions": total_deductions,
                "employee_count": len(payslips),
                "created_at": run.created_at,
                "updated_at": run.updated_at
            })
        
        return {
            "items": result_runs,
            "total": total
        }
    
    @staticmethod
    def calculate_payroll(
        db: Session,
        payroll_run_id: UUID,
        calculation_request: PayrollCalculationRequest
    ) -> List[Dict[str, Any]]:
        """Calculate payroll for specified employees."""
        payroll_run = db.query(PayPeriod).filter(PayPeriod.id == payroll_run_id).first()
        if not payroll_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll run not found"
            )
        
        employees = db.query(Employee).filter(
            Employee.id.in_(calculation_request.employee_ids)
        ).all()
        
        if not employees:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No employees found"
            )
        
        calculated_payslips = []
        
        for employee in employees:
            # Basic salary calculation
            basic_salary = employee.base_salary
            
            # Calculate overtime (simplified - 1.5x rate for hours over 40)
            overtime_pay = Decimal("0.00")
            if calculation_request.include_overtime:
                # This would typically come from time tracking data
                overtime_hours = Decimal("0.00")  # Placeholder
                hourly_rate = basic_salary / Decimal("160")  # Assuming 160 hours/month
                overtime_pay = overtime_hours * hourly_rate * Decimal("1.5")
            
            # Calculate bonus (simplified)
            bonus = Decimal("0.00")
            if calculation_request.include_bonus:
                # This would typically come from performance data
                bonus = basic_salary * Decimal("0.05")  # 5% bonus placeholder
            
            # Calculate allowances (simplified)
            allowances = basic_salary * Decimal("0.10")  # 10% allowances placeholder
            
            # Calculate gross pay
            gross_pay = basic_salary + overtime_pay + bonus + allowances
            
            # Calculate taxes using tax calculation engine
            from app.modules.core_financials.payroll.services.tax_calculation_service import TaxCalculationService
            from app.modules.core_financials.payroll.schemas.tax_calculation import TaxCalculationRequest, FilingStatusEnum
            
            tax_request = TaxCalculationRequest(
                employee_id=employee.id,
                gross_pay=gross_pay,
                pay_period="monthly",
                filing_status=FilingStatusEnum.SINGLE,
                allowances=0,
                additional_withholding=Decimal("0.00"),
                state="CA",
                year=2024
            )
            
            tax_result = TaxCalculationService.calculate_taxes(tax_request)
            tax_deductions = tax_result.total_tax
            other_deductions = gross_pay * Decimal("0.02")  # 2% other deductions
            total_deductions = tax_deductions + other_deductions
            
            # Calculate net pay
            net_pay = gross_pay - total_deductions
            
            calculated_payslips.append({
                "employee_id": employee.id,
                "employee_name": employee.full_name,
                "employee_code": employee.employee_id,
                "basic_salary": basic_salary,
                "overtime_pay": overtime_pay,
                "bonus": bonus,
                "allowances": allowances,
                "gross_pay": gross_pay,
                "tax_deductions": tax_deductions,
                "deductions": other_deductions,
                "total_deductions": total_deductions,
                "net_pay": net_pay
            })
        
        return calculated_payslips
    
    @staticmethod
    def process_payroll(
        db: Session,
        payroll_run_id: UUID,
        payslips_data: List[PayslipCreate]
    ) -> Dict[str, Any]:
        """Process payroll and create payslips."""
        payroll_run = db.query(PayPeriod).filter(PayPeriod.id == payroll_run_id).first()
        if not payroll_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll run not found"
            )
        
        # Delete existing payslips for this run
        db.query(Payslip).filter(Payslip.pay_period_id == payroll_run_id).delete()
        
        # Create new payslips
        created_payslips = []
        for payslip_data in payslips_data:
            payslip = Payslip(
                employee_id=payslip_data.employee_id,
                pay_period_id=payroll_run_id,
                gross_pay=payslip_data.gross_pay,
                basic_salary=payslip_data.basic_salary,
                overtime_pay=payslip_data.overtime_pay,
                bonus=payslip_data.bonus,
                allowances=payslip_data.allowances,
                deductions=payslip_data.deductions,
                tax_deductions=payslip_data.tax_deductions,
                total_deductions=payslip_data.deductions + payslip_data.tax_deductions,
                net_pay=payslip_data.net_pay
            )
            db.add(payslip)
            created_payslips.append(payslip)
        
        # Update payroll run status
        payroll_run.status = "PROCESSING"
        
        db.commit()
        
        # Calculate summary
        total_gross = sum(p.gross_pay for p in created_payslips)
        total_net = sum(p.net_pay for p in created_payslips)
        total_deductions = sum(p.total_deductions for p in created_payslips)
        
        return {
            "payroll_run_id": payroll_run_id,
            "processed_count": len(created_payslips),
            "total_gross_pay": total_gross,
            "total_net_pay": total_net,
            "total_deductions": total_deductions,
            "status": payroll_run.status
        }
    
    @staticmethod
    def approve_payroll(db: Session, payroll_run_id: UUID) -> Dict[str, Any]:
        """Approve a payroll run."""
        payroll_run = db.query(PayPeriod).filter(PayPeriod.id == payroll_run_id).first()
        if not payroll_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll run not found"
            )
        
        if payroll_run.status != "PROCESSING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payroll run must be in PROCESSING status to approve"
            )
        
        payroll_run.status = "APPROVED"
        db.commit()
        
        return {
            "payroll_run_id": payroll_run_id,
            "status": payroll_run.status,
            "message": "Payroll run approved successfully"
        }
    
    @staticmethod
    def get_payroll_summary(db: Session, payroll_run_id: UUID) -> PayrollSummary:
        """Get payroll summary for a specific run."""
        payslips = db.query(Payslip).filter(Payslip.pay_period_id == payroll_run_id).all()
        
        if not payslips:
            return PayrollSummary(
                total_employees=0,
                total_gross_pay=Decimal("0.00"),
                total_net_pay=Decimal("0.00"),
                total_deductions=Decimal("0.00"),
                total_tax_deductions=Decimal("0.00"),
                average_gross_pay=Decimal("0.00"),
                average_net_pay=Decimal("0.00")
            )
        
        total_employees = len(payslips)
        total_gross = sum(p.gross_pay for p in payslips)
        total_net = sum(p.net_pay for p in payslips)
        total_deductions = sum(p.total_deductions for p in payslips)
        total_tax = sum(p.tax_deductions for p in payslips)
        
        return PayrollSummary(
            total_employees=total_employees,
            total_gross_pay=total_gross,
            total_net_pay=total_net,
            total_deductions=total_deductions,
            total_tax_deductions=total_tax,
            average_gross_pay=total_gross / total_employees,
            average_net_pay=total_net / total_employees
        )