"""
Main payroll service that orchestrates the entire payroll processing workflow.
"""
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from ..models.payroll_models import (
from ..schemas.payroll_schemas import (
from .net_pay_processor import NetPayProcessor
from .payroll_processor import PayrollProcessor
from .payroll_tax_calculator import PayrollTaxCalculator
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import logger




    Employee, PayPeriod, PayRun, Payslip, PayslipEarning, PayslipDeduction,
    PayslipTax, PayslipBenefit, PayComponent, PayComponentType, PaySchedule,
    TaxCode, BenefitPlan, BenefitEnrollment, LeaveRequest, AttendanceRecord,
    BankAccount, PayRunStatus, PayFrequency, EmploymentType
)
    PayRunCreate, PayRunUpdate, PayRunResponse, PayslipResponse,
    PayslipEarningResponse, PayslipDeductionResponse, PayslipTaxResponse,
    PayslipBenefitResponse, PayrollProcessingRequest, PayrollProcessingResult,
    PayrollCalculationResult, PayrollEarningItem, PayrollDeductionItem,
    PayrollTaxItem, PayrollBenefitItem, PayrollNetPayCalculation
)

class PayrollService:
    """
    Main service for handling all payroll-related operations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.payroll_processor = PayrollProcessor(db)
        self.tax_calculator = PayrollTaxCalculator(db)
        self.net_pay_processor = NetPayProcessor(db)
        
    def _generate_payroll_journal_entries(self, pay_run_id: UUID) -> None:
        """
        Generate journal entries for a completed pay run.
        
        This creates the necessary accounting entries for:
        - Salary and wage expenses (debit)
        - Employee deductions (credit)
        - Tax liabilities (credit)
        - Net pay payable (credit)
        - Employer payroll taxes (debit)
        
        Args:
            pay_run_id: ID of the pay run to generate journal entries for
            
        Raises:
            AppException: If there's an error generating the journal entries
        """
        from app.modules.core_financials.accounting.services import JournalEntryService
        from app.modules.core_financials.accounting.models import JournalEntryStatus
        from datetime import datetime, timezone
        
        try:
            # Get the pay run with all related data
            pay_run = (
                self.db.query(PayRun)
                .options(
                    joinedload(PayRun.pay_period),
                    joinedload(PayRun.payslips)
                    .joinedload(Payslip.employee)
                    .load_only(Employee.id, Employee.first_name, Employee.last_name),
                    joinedload(PayRun.payslips)
                    .joinedload(Payslip.earnings),
                    joinedload(PayRun.payslips)
                    .joinedload(Payslip.deductions),
                )
                .filter(PayRun.id == pay_run_id)
                .first()
            )
            
            if not pay_run:
                raise AppException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message=f"Pay run {pay_run_id} not found"
                )
                
            if pay_run.status != PayRunStatus.COMPLETED:
                raise AppException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=f"Cannot generate journal entries for pay run with status {pay_run.status}"
                )
            
            # Initialize the journal entry service
            journal_entry_service = JournalEntryService(self.db)
            
            # Create a reference for the journal entry
            reference = f"PAYROLL-{pay_run.pay_period.name if pay_run.pay_period else pay_run.id}"
            
            # Prepare journal entry data
            entry_date = datetime.now(timezone.utc).date()
            description = f"Payroll for {pay_run.pay_period.name if pay_run.pay_period else 'period'}"
            
            # Group payroll data by cost center/department if needed
            # For now, we'll create a single journal entry for the entire pay run
            
            # Initialize totals
            total_gross_pay = Decimal('0.00')
            total_taxes = Decimal('0.00')
            total_deductions = Decimal('0.00')
            total_net_pay = Decimal('0.00')
            total_employer_taxes = Decimal('0.00')
            
            # Get all payslips for this pay run
            payslips = pay_run.payslips
            
            # Calculate totals
            for payslip in payslips:
                total_gross_pay += payslip.gross_pay
                total_taxes += payslip.tax_deductions
                total_deductions += (payslip.total_deductions - payslip.tax_deductions)
                total_net_pay += payslip.net_pay
                
                # Employer taxes would be calculated separately in a real system
                # For now, we'll use a simplified approach
                # In a real system, this would include employer SS, Medicare, unemployment, etc.
                employer_ss = payslip.social_security * Decimal('0.5')  # Example: 50% employer match
                employer_medicare = payslip.health_insurance * Decimal('0.5')  # Example: 50% employer match
                total_employer_taxes += (employer_ss + employer_medicare)
            
            # Create journal entry lines
            lines = []
            
            # 1. Debit Salary/Wage Expense (total_gross_pay + total_employer_taxes)
            # In a real system, this would be split by department/cost center
            lines.append({
                'account_code': '5000',  # Salary and Wages Expense (example account code)
                'description': 'Salary and Wages',
                'debit': total_gross_pay,
                'credit': Decimal('0.00'),
            })
            
            # 2. Debit Payroll Tax Expense (employer portion)
            if total_employer_taxes > 0:
                lines.append({
                    'account_code': '6300',  # Payroll Tax Expense (example account code)
                    'description': 'Employer Payroll Taxes',
                    'debit': total_employer_taxes,
                    'credit': Decimal('0.00'),
                })
            
            # 3. Credit Employee Tax Withholdings (liability)
            if total_taxes > 0:
                lines.append({
                    'account_code': '2010',  # Employee Tax Withholdings Payable (example)
                    'description': 'Employee Tax Withholdings',
                    'debit': Decimal('0.00'),
                    'credit': total_taxes,
                })
            
            # 4. Credit Other Deductions (liability)
            if total_deductions > 0:
                lines.append({
                    'account_code': '2020',  # Employee Deductions Payable (example)
                    'description': 'Employee Deductions',
                    'debit': Decimal('0.00'),
                    'credit': total_deductions,
                })
            
            # 5. Credit Employer Tax Liabilities
            if total_employer_taxes > 0:
                lines.append({
                    'account_code': '2030',  # Employer Tax Liabilities (example)
                    'description': 'Employer Payroll Tax Liabilities',
                    'debit': Decimal('0.00'),
                    'credit': total_employer_taxes,
                })
            
            # 6. Credit Net Pay Payable (liability)
            if total_net_pay > 0:
                lines.append({
                    'account_code': '2040',  # Net Pay Payable (example)
                    'description': 'Net Pay to Employees',
                    'debit': Decimal('0.00'),
                    'credit': total_net_pay,
                })
            
            # Create the journal entry
            journal_entry_data = {
                'entry_date': entry_date,
                'reference': reference,
                'description': description,
                'status': JournalEntryStatus.POSTED,
                'lines': lines,
                'metadata': {
                    'pay_run_id': str(pay_run_id),
                    'pay_period_id': str(pay_run.pay_period_id) if pay_run.pay_period_id else None,
                    'employee_count': len(payslips),
                    'total_gross_pay': float(total_gross_pay),
                    'total_net_pay': float(total_net_pay),
                }
            }
            
            # Save the journal entry
            journal_entry = journal_entry_service.create_journal_entry(journal_entry_data)
            
            # Update the pay run with the journal entry reference
            pay_run.journal_entry_id = journal_entry.id
            self.db.commit()
            
            logger.info(f"Generated payroll journal entry {journal_entry.entry_number} for pay run {pay_run_id}")
            
        except Exception as e:
            logger.error(f"Error generating payroll journal entries: {str(e)}", exc_info=True)
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to generate payroll journal entries: {str(e)}"
            )
    
    def _get_pay_run_response(self, pay_run: PayRun) -> PayRunResponse:
        return PayRunResponse(
            id=pay_run.id,
            pay_period_id=pay_run.pay_period_id,
            company_id=pay_run.company_id,
            status=pay_run.status,
            process_taxes=pay_run.process_taxes,
            process_benefits=pay_run.process_benefits,
            is_dry_run=pay_run.is_dry_run,
            created_by=pay_run.created_by,
            processed_by=pay_run.processed_by,
            created_at=pay_run.created_at,
            processed_at=pay_run.processed_at,
            completed_at=pay_run.completed_at,
            error_message=pay_run.error_message,
            payslip_count=len(pay_run.payslips) if hasattr(pay_run, 'payslips') else 0,
            total_gross_pay=sum(p.gross_pay for p in pay_run.payslips) if hasattr(pay_run, 'payslips') else Decimal('0.00'),
            total_net_pay=sum(p.net_pay for p in pay_run.payslips) if hasattr(pay_run, 'payslips') else Decimal('0.00'),
            total_taxes=sum(p.total_tax for p in pay_run.payslips) if hasattr(pay_run, 'payslips') else Decimal('0.00'),
            total_deductions=sum(p.total_deductions for p in pay_run.payslips) if hasattr(pay_run, 'payslips') else Decimal('0.00')
        )
    
    def process_payroll(
        self,
        pay_period_id: UUID,
        company_id: UUID,
        processed_by: UUID,
        employee_ids: Optional[List[UUID]] = None,
        process_taxes: bool = True,
        process_benefits: bool = True,
        dry_run: bool = False
    ) -> PayRunResponse:
        """Process Payroll."""
        """
        Process payroll for a specific pay period.
        
        This is the main entry point for processing payroll. It will:
        1. Initialize a new pay run
        2. Process the pay run (calculate payslips for all eligible employees)
        3. Return the pay run details with processing results
        
        Args:
            pay_period_id: ID of the pay period to process
            company_id: ID of the company
            processed_by: ID of the user processing the payroll
            employee_ids: Optional list of employee IDs to process (all eligible if None)
            process_taxes: Whether to calculate taxes
            process_benefits: Whether to process benefits
            dry_run: If True, validate but don't save to database
            
        Returns:
            PayRunResponse with processing results
            
        Raises:
            AppException: If there's an error during processing
        """
        try:
            logger.info(f"Starting payroll processing for pay period {pay_period_id}")
            
            # Step 1: Initialize the pay run
            logger.debug("Initializing pay run...")
            pay_run = self.payroll_processor.initialize_pay_run(
                pay_period_id=pay_period_id,
                created_by=processed_by,
                company_id=company_id,
                process_taxes=process_taxes,
                process_benefits=process_benefits,
                dry_run=dry_run
            )
            
            # If this is a dry run, we're done
            if dry_run:
                logger.info("Dry run completed successfully")
                return self._get_pay_run_response(pay_run)
            
            try:
                # Step 2: Process the pay run (calculate payslips, taxes, benefits, etc.)
                logger.debug("Processing pay run...")
                pay_run = self.payroll_processor.process_pay_run(
                    pay_run_id=pay_run.id,
                    processed_by=processed_by,
                    employee_ids=employee_ids,
                    recalculate=False
                )
                
                # Step 3: Generate payroll journal entries
                logger.debug("Generating payroll journal entries...")
                self._generate_payroll_journal_entries(pay_run.id)
                
                # Step 4: Update pay run status to completed
                pay_run.status = PayRunStatus.COMPLETED
                pay_run.completed_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Payroll processing completed for pay run {pay_run.id}")
                
            except Exception as e:
                # Update pay run status to failed
                pay_run.status = PayRunStatus.FAILED
                pay_run.error_message = str(e)
                self.db.commit()
                logger.error(f"Error processing payroll: {str(e)}", exc_info=True)
                raise
            
            # Get the pay run details with all related data
            return self.get_pay_run(pay_run.id)
            
        except Exception as e:
            logger.error(f"Error in process_payroll: {str(e)}", exc_info=True)
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Failed to process payroll: {str(e)}"
            )
    
    def get_pay_run(self, pay_run_id: UUID) -> PayRunResponse:
        """
        Get pay run details by ID with all related data.
        
        Args:
            pay_run_id: ID of the pay run to retrieve
            
        Returns:
            PayRunResponse with pay run details including payslips and totals
            
        Raises:
            AppException: If pay run is not found
        """
        pay_run = (
            self.db.query(PayRun)
            .options(
                joinedload(PayRun.pay_period),
                joinedload(PayRun.payslips)
                .joinedload(Payslip.employee)
                .load_only(Employee.id, Employee.first_name, Employee.last_name, Employee.employee_number),
                joinedload(PayRun.payslips)
                .joinedload(Payslip.earnings),
                joinedload(PayRun.payslips)
                .joinedload(Payslip.deductions),
                joinedload(PayRun.payslips)
                .joinedload(Payslip.taxes),
                joinedload(PayRun.payslips)
                .joinedload(Payslip.benefits)
            )
            .filter(PayRun.id == pay_run_id)
            .first()
        )
        
        if not pay_run:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"Pay run {pay_run_id} not found"
            )
            
        return self._get_pay_run_response(pay_run)
        
    def _generate_payroll_journal_entries(self, pay_run_id: UUID) -> None:
        """
        Generate journal entries for a processed pay run.
        
        This creates the necessary accounting entries for the payroll run,
        including salary expenses, tax liabilities, and net pay.
        
        Args:
            pay_run_id: ID of the pay run to generate entries for
            
        Raises:
            AppException: If there's an error generating the entries
        """
        try:
            # Get the pay run with all related data
            pay_run = (
                self.db.query(PayRun)
                .options(
                    joinedload(PayRun.payslips)
                    .joinedload(Payslip.earnings),
                    joinedload(PayRun.payslips)
                    .joinedload(Payslip.deductions),
                    joinedload(PayRun.payslips)
                    .joinedload(Payslip.taxes),
                    joinedload(PayRun.payslips)
                    .joinedload(Payslip.benefits)
                )
                .filter(PayRun.id == pay_run_id)
                .first()
            )
            
            if not pay_run:
                raise AppException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message=f"Pay run {pay_run_id} not found"
                )
                
            # This is a placeholder - actual implementation will:
            # 1. Create a journal entry for the pay run
            # 2. Add debit entries for salary/wage expenses
            # 3. Add credit entries for tax liabilities, benefit contributions, and net pay
            # 4. Post the journal entry to the general ledger
            
            logger.info(f"Generated journal entries for pay run {pay_run_id}")
            
        except Exception as e:
            logger.error(f"Error generating payroll journal entries: {str(e)}", exc_info=True)
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to generate payroll journal entries: {str(e)}"
            )
            # This is a placeholder - actual implementation will:
            # 1. Create a journal entry for the pay run
            # 2. Add debit entries for salary/wage expenses
            # 3. Add credit entries for tax liabilities, benefit contributions, and net pay
            # 4. Post the journal entry to the general ledger
            
            # For now, just log that we would generate journal entries here
            logger.info(f"Would generate journal entries for pay run {pay_run_id}")
            
            # Return None since we're not actually generating entries yet
            return None
    
    def get_payslip(self, payslip_id: UUID) -> PayslipResponse:
        """
        Get details of a specific payslip.
        
        Args:
            payslip_id: ID of the payslip
            
        Returns:
            PayslipResponse with payslip details
        """
        payslip = self.db.query(Payslip).get(payslip_id)
        if not payslip:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"Payslip {payslip_id} not found"
            )
        
        # Get earnings
        earnings = (
            self.db.query(PayslipEarning)
            .filter(PayslipEarning.payslip_id == payslip_id)
            .all()
        )
        
        # Get deductions
        deductions = (
            self.db.query(PayslipDeduction)
            .filter(PayslipDeduction.payslip_id == payslip_id)
            .all()
        )
        
        # Get taxes
        taxes = (
            self.db.query(PayslipTax)
            .filter(PayslipTax.payslip_id == payslip_id)
            .all()
        )
        
        # Get benefits
        benefits = (
            self.db.query(PayslipBenefit)
            .filter(PayslipBenefit.payslip_id == payslip_id)
            .all()
        )
        
        return PayslipResponse(
            id=payslip.id,
            pay_run_id=payslip.pay_run_id,
            employee_id=payslip.employee_id,
            pay_period_id=payslip.pay_period_id,
            company_id=payslip.company_id,
            status=payslip.status,
            payment_method=payslip.payment_method,
            bank_account_id=payslip.bank_account_id,
            currency=payslip.currency,
            gross_pay=payslip.gross_pay,
            tax_withheld=payslip.tax_withheld,
            benefit_contributions=payslip.benefit_contributions,
            other_deductions=payslip.other_deductions,
            net_pay=payslip.net_pay,
            payment_date=payslip.payment_date,
            processed_at=payslip.processed_at,
            created_at=payslip.created_at,
            updated_at=payslip.updated_at,
            created_by=payslip.created_by,
            updated_by=payslip.updated_by,
            earnings=[
                PayslipEarningResponse(
                    id=e.id,
                    payslip_id=e.payslip_id,
                    type=e.type,
                    name=e.name,
                    amount=e.amount,
                    ytd_amount=e.ytd_amount,
                    is_taxable=e.is_taxable,
                    is_pensionable=e.is_pensionable,
                    gl_account_code=e.gl_account_code,
                    created_at=e.created_at,
                    updated_at=e.updated_at
                )
                for e in earnings
            ],
            deductions=[
                PayslipDeductionResponse(
                    id=d.id,
                    payslip_id=d.payslip_id,
                    type=d.type,
                    name=d.name,
                    amount=d.amount,
                    ytd_amount=d.ytd_amount,
                    is_pre_tax=d.is_pre_tax,
                    gl_account_code=d.gl_account_code,
                    created_at=d.created_at,
                    updated_at=d.updated_at
                )
                for d in deductions
            ],
            taxes=[
                PayslipTaxResponse(
                    id=t.id,
                    payslip_id=t.payslip_id,
                    code=t.code,
                    name=t.name,
                    amount=t.amount,
                    ytd_amount=t.ytd_amount,
                    is_employer_tax=t.is_employer_tax,
                    gl_account_code=t.gl_account_code,
                    created_at=t.created_at,
                    updated_at=t.updated_at
                )
                for t in taxes
            ],
            benefits=[
                PayslipBenefitResponse(
                    id=b.id,
                    payslip_id=b.payslip_id,
                    benefit_plan_id=b.benefit_plan_id,
                    name=b.name,
                    employee_contribution=b.employee_contribution,
                    employer_contribution=b.employer_contribution,
                    is_pre_tax=b.is_pre_tax,
                    gl_account_code=b.gl_account_code,
                    created_at=b.created_at,
                    updated_at=b.updated_at
                )
                for b in benefits
            ]
        )
    
    def process_payments(
        self,
        pay_run_id: UUID,
        processed_by: UUID,
        payment_date: Optional[date] = None,
        dry_run: bool = False
    ) -> List[Dict]:
        """Process Payments."""
        """
        Process payments for all payslips in a pay run.
        
        Args:
            pay_run_id: ID of the pay run to process
            processed_by: ID of the user processing the payments
            payment_date: Date to record for payments (defaults to today)
            dry_run: If True, validate but don't process payments
            
        Returns:
            List of payment results
        """
        return self.net_pay_processor.process_payments(
            pay_run_id=pay_run_id,
            processed_by=processed_by,
            payment_date=payment_date,
            dry_run=dry_run
        )
    
    def get_employee_pay_history(
        self,
        employee_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 12,
        offset: int = 0
    ) -> Tuple[List[PayslipResponse], int]:
        """Get Employee Pay History."""
        """
        Get pay history for an employee.
        
        Args:
            employee_id: ID of the employee
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            Tuple of (payslips, total_count)
        """
        query = self.db.query(Payslip).filter(
            Payslip.employee_id == employee_id
        )
        
        # Apply date filters
        if start_date:
            query = query.join(PayPeriod).filter(PayPeriod.end_date >= start_date)
        if end_date:
            query = query.join(PayPeriod).filter(PayPeriod.start_date <= end_date)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        payslips = (
            query.order_by(PayPeriod.end_date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        # Convert to response models
        return [
            self.get_payslip(payslip.id) for payslip in payslips
        ], total
