"""
Net pay calculation and payment processing for payroll.
"""
from datetime import date, datetime
from typing import Dict, List, Optional, Union

from ..models.payroll_models import (
from ..schemas.payroll_schemas import (
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.config import settings
from app.core.logging import logger




    Employee, Payslip, PayRun, BankAccount, PaymentMethod, 
    PayrollDisbursement, PayrollDeduction
)
    NetPayCalculation, PaymentDisbursement, PayrollDeductionItem
)

class NetPayProcessor:
    """Handles net pay calculation and payment processing."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        """Initialize the net pay processor with a database session."""
        self.db = db
    
    def calculate_net_pay(
        """Calculate Net Pay."""
        self,
        gross_pay: Decimal,
        pre_tax_deductions: List[PayrollDeductionItem],
        taxes: List[Dict],
        post_tax_deductions: List[PayrollDeductionItem],
        benefits: List[Dict]
    ) -> NetPayCalculation:
        """Calculate Net Pay."""
        """
        Calculate net pay from gross pay and deductions.
        
        Args:
            gross_pay: Gross pay amount
            pre_tax_deductions: List of pre-tax deductions
            taxes: List of tax amounts
            post_tax_deductions: List of post-tax deductions
            benefits: List of benefit contributions
            
        Returns:
            NetPayCalculation with all calculated amounts
        """
        # Calculate totals
        total_pre_tax_deductions = sum(d.amount for d in pre_tax_deductions)
        total_taxes = sum(t.get('amount', 0) for t in taxes if not t.get('is_employer_tax', False))
        total_post_tax_deductions = sum(d.amount for d in post_tax_deductions)
        
        # Calculate benefit contributions
        total_employee_benefits = sum(
            b.get('employee_contribution', 0) 
            for b in benefits
            if not b.get('is_employer_paid', True)
        )
        
        # Calculate net pay
        net_pay = (
            gross_pay 
            - total_pre_tax_deductions 
            - total_taxes 
            - total_post_tax_deductions
            - total_employee_benefits
        ).quantize(Decimal("0.01"), ROUND_HALF_UP)
        
        # Calculate employer costs
        employer_taxes = sum(
            t.get('amount', 0) 
            for t in taxes 
            if t.get('is_employer_tax', False)
        )
        
        employer_benefits = sum(
            b.get('employer_contribution', 0)
            for b in benefits
        )
        
        total_employer_cost = (
            gross_pay 
            + employer_taxes 
            + employer_benefits
        ).quantize(Decimal("0.01"), ROUND_HALF_UP)
        
        return NetPayCalculation(
            gross_pay=gross_pay,
            total_pre_tax_deductions=total_pre_tax_deductions,
            taxable_income=max(Decimal("0.00"), gross_pay - total_pre_tax_deductions),
            total_taxes=total_taxes,
            total_post_tax_deductions=total_post_tax_deductions,
            total_employee_benefits=total_employee_benefits,
            net_pay=net_pay,
            employer_taxes=employer_taxes,
            employer_benefits=employer_benefits,
            total_employer_cost=total_employer_cost
        )
    
    def process_payments(
        """Process Payments."""
        self,
        pay_run_id: UUID,
        processed_by: UUID,
        payment_date: Optional[date] = None,
        dry_run: bool = False
    ) -> List[PaymentDisbursement]:
        """Process Payments."""
        """
        Process payments for all payslips in a pay run.
        
        Args:
            pay_run_id: ID of the pay run to process
            processed_by: ID of the user processing the payments
            payment_date: Date to record for payments (defaults to today)
            dry_run: If True, validate but don't process payments
            
        Returns:
            List of payment disbursements
        """
        if payment_date is None:
            payment_date = date.today()
        
        # Get the pay run and associated payslips
        pay_run = self.db.query(PayRun).get(pay_run_id)
        if not pay_run:
            raise ValueError(f"Pay run {pay_run_id} not found")
        
        if pay_run.status != "APPROVED":
            raise ValueError(f"Pay run {pay_run_id} is not approved for payment")
        
        payslips = (
            self.db.query(Payslip)
            .filter(
                Payslip.pay_run_id == pay_run_id,
                Payslip.status == "APPROVED"
            )
            .all()
        )
        
        if not payslips:
            logger.warning(f"No approved payslips found for pay run {pay_run_id}")
            return []
        
        # Process each payslip
        disbursements = []
        
        for payslip in payslips:
            try:
                disbursement = self._process_employee_payment(
                    payslip=payslip,
                    payment_date=payment_date,
                    processed_by=processed_by,
                    dry_run=dry_run
                )
                disbursements.append(disbursement)
                
            except Exception as e:
                logger.error(
                    f"Error processing payment for employee {payslip.employee_id} "
                    f"in pay run {pay_run_id}: {str(e)}",
                    exc_info=True
                )
                # Continue with next payslip on error
                continue
        
        # Update pay run status if not a dry run
        if not dry_run and disbursements:
            pay_run.status = "PAID"
            pay_run.payment_date = payment_date
            pay_run.updated_by = processed_by
            pay_run.updated_at = datetime.utcnow()
            self.db.commit()
        
        return disbursements
    
    def _process_employee_payment(
        """ Process Employee Payment."""
        self,
        payslip: Payslip,
        payment_date: date,
        processed_by: UUID,
        dry_run: bool = False
    ) -> PaymentDisbursement:
        """ Process Employee Payment."""
        """
        Process payment for a single employee's payslip.
        
        Args:
            payslip: The payslip to process
            payment_date: Date of payment
            processed_by: ID of the user processing the payment
            dry_run: If True, validate but don't process payment
            
        Returns:
            PaymentDisbursement with payment details
        """
        employee = payslip.employee
        payment_method = self._get_payment_method(employee, payslip.payment_method)
        
        # Create payment record
        payment = PayrollDisbursement(
            payslip_id=payslip.id,
            employee_id=employee.id,
            company_id=payslip.company_id,
            payment_method_id=payment_method.id if payment_method else None,
            bank_account_id=payslip.bank_account_id,
            amount=payslip.net_pay,
            payment_date=payment_date,
            status="PENDING" if not dry_run else "DRY_RUN",
            reference=f"PAY-{payslip.pay_run_id[:8]}-{employee.employee_number}",
            currency=payslip.currency,
            created_by=processed_by,
            updated_by=processed_by
        )
        
        if not dry_run:
            self.db.add(payment)
            self.db.flush()
        
        # Process payment based on payment method
        try:
            if dry_run:
                payment_status = "PROCESSED_DRY_RUN"
                external_reference = "DRY_RUN_REFERENCE"
                notes = "Dry run - no actual payment processed"
            else:
                # In a real implementation, this would integrate with a payment processor
                # For now, we'll simulate a successful payment
                payment_status = "PROCESSED"
                external_reference = f"PAY-{payment.id.hex[:8].upper()}"
                notes = "Payment processed successfully"
                
                # Update payment status
                payment.status = payment_status
                payment.external_reference = external_reference
                payment.processed_at = datetime.utcnow()
                
                # Update payslip status
                payslip.status = "PAID"
                payslip.payment_date = payment_date
                payslip.updated_by = processed_by
                payslip.updated_at = datetime.utcnow()
                
                self.db.commit()
            
            return PaymentDisbursement(
                employee_id=employee.id,
                employee_name=f"{employee.first_name} {employee.last_name}",
                employee_number=employee.employee_number,
                payment_method=payment_method.name if payment_method else "UNKNOWN",
                amount=payslip.net_pay,
                currency=payslip.currency,
                status=payment_status,
                reference=payment.reference,
                external_reference=external_reference,
                notes=notes
            )
            
        except Exception as e:
            if not dry_run:
                self.db.rollback()
                payment.status = "FAILED"
                payment.notes = f"Payment failed: {str(e)}"
                self.db.commit()
            
            logger.error(
                f"Error processing payment for employee {employee.id}: {str(e)}",
                exc_info=True
            )
            
            return PaymentDisbursement(
                employee_id=employee.id,
                employee_name=f"{employee.first_name} {employee.last_name}",
                employee_number=employee.employee_number,
                payment_method=payment_method.name if payment_method else "UNKNOWN",
                amount=payslip.net_pay,
                currency=payslip.currency,
                status="FAILED",
                reference=payment.reference if 'payment' in locals() else "",
                external_reference="",
                notes=f"Payment failed: {str(e)}"
            )
    
    def _get_payment_method(
        """ Get Payment Method."""
        self,
        employee: Employee,
        method_code: Optional[str] = None
    ) -> Optional[PaymentMethod]:
        """ Get Payment Method."""
        """
        Get the payment method for an employee.
        
        Args:
            employee: The employee
            method_code: Optional payment method code to override employee's default
            
        Returns:
            PaymentMethod or None if not found
        """
        code = method_code or employee.default_payment_method
        if not code:
            return None
            
        return (
            self.db.query(PaymentMethod)
            .filter(
                PaymentMethod.code == code,
                PaymentMethod.is_active == True
            )
            .first()
        )
