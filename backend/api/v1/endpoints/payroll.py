"""
Payroll API endpoints.
"""
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.security import get_current_active_user
from app.models.user_models import User
from app.schemas.common_schemas import MessageResponse, PaginatedResponse

from app.modules.core_financials.payroll.schemas.payroll_schemas import (
    PayRunResponse, PayslipResponse, PayrollProcessingRequest,
    PayrollProcessingResult, PayrollPaymentDisbursement
)
from app.modules.core_financials.payroll.services.payroll_service import PayrollService

router = APIRouter()

@router.post("/process", response_model=PayRunResponse)
def process_payroll(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    payroll_data: PayrollProcessingRequest
) -> PayRunResponse:
    """
    Process payroll for a specific pay period.
    
    This endpoint initiates the payroll processing for the specified pay period.
    It will calculate earnings, deductions, taxes, and net pay for all eligible employees.
    """
    if not current_user.is_superuser and not current_user.has_permission("payroll:process"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to process payroll"
        )
    
    service = PayrollService(db)
    return service.process_payroll(
        pay_period_id=payroll_data.pay_period_id,
        company_id=payroll_data.company_id,
        processed_by=current_user.id,
        employee_ids=payroll_data.employee_ids,
        process_taxes=payroll_data.process_taxes,
        process_benefits=payroll_data.process_benefits,
        dry_run=payroll_data.dry_run
    )

@router.get("/runs/{pay_run_id}", response_model=PayRunResponse)
def get_pay_run(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    pay_run_id: UUID
) -> PayRunResponse:
    """
    Get details of a specific pay run.
    
    Returns comprehensive information about a pay run including totals and status.
    """
    if not current_user.has_permission("payroll:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view pay run details"
        )
    
    service = PayrollService(db)
    return service.get_pay_run(pay_run_id=pay_run_id)

@router.get("/payslips/{payslip_id}", response_model=PayslipResponse)
def get_payslip(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    payslip_id: UUID
) -> PayslipResponse:
    """
    Get details of a specific payslip.
    
    Returns detailed information about an employee's payslip including
    earnings, deductions, taxes, and benefits.
    """
    service = PayrollService(db)
    payslip = service.get_payslip(payslip_id=payslip_id)
    
    # Check if user has permission to view this payslip
    if not current_user.is_superuser and (
        not current_user.has_permission("payroll:read") or 
        str(current_user.employee_id) != str(payslip.employee_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payslip"
        )
    
    return payslip

@router.post("/runs/{pay_run_id}/payments/process", response_model=List[PayrollPaymentDisbursement])
def process_payments(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    pay_run_id: UUID,
    payment_date: Optional[date] = None,
    dry_run: bool = False
) -> List[PayrollPaymentDisbursement]:
    """
    Process payments for a pay run.
    
    This endpoint initiates the payment processing for all payslips in a pay run.
    It will process payments according to each employee's payment method.
    """
    if not current_user.is_superuser and not current_user.has_permission("payroll:process"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to process payments"
        )
    
    service = PayrollService(db)
    return service.process_payments(
        pay_run_id=pay_run_id,
        processed_by=current_user.id,
        payment_date=payment_date,
        dry_run=dry_run
    )

@router.get("/employees/{employee_id}/payslips", response_model=PaginatedResponse[PayslipResponse])
def get_employee_pay_history(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    employee_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    limit: int = 12
) -> PaginatedResponse[PayslipResponse]:
    """
    Get pay history for an employee.
    
    Returns a paginated list of payslips for the specified employee.
    """
    # Check if user has permission to view this employee's pay history
    if not current_user.is_superuser and (
        not current_user.has_permission("payroll:read") or 
        str(current_user.employee_id) != str(employee_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this employee's pay history"
        )
    
    service = PayrollService(db)
    offset = (page - 1) * limit
    payslips, total = service.get_employee_pay_history(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    return PaginatedResponse[
        PayslipResponse
    ](
        items=payslips,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )

@router.post("/runs/{pay_run_id}/approve", response_model=MessageResponse)
def approve_pay_run(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    pay_run_id: UUID
) -> MessageResponse:
    """
    Approve a pay run for payment processing.
    
    This endpoint marks a pay run as approved, allowing payments to be processed.
    """
    if not current_user.is_superuser and not current_user.has_permission("payroll:approve"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to approve pay runs"
        )
    
    service = PayrollService(db)
    pay_run = service.get_pay_run(pay_run_id=pay_run_id)
    
    # In a real implementation, we would update the pay run status to APPROVED
    # and possibly trigger notifications or workflow steps
    
    return MessageResponse(
        message=f"Pay run {pay_run_id} approved successfully"
    )

@router.post("/runs/{pay_run_id}/reject", response_model=MessageResponse)
def reject_pay_run(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    pay_run_id: UUID,
    reason: str
) -> MessageResponse:
    """
    Reject a pay run.
    
    This endpoint marks a pay run as rejected, preventing it from being processed.
    A reason for rejection must be provided.
    """
    if not current_user.is_superuser and not current_user.has_permission("payroll:approve"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to reject pay runs"
        )
    
    if not reason or len(reason.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a detailed reason for rejection (minimum 10 characters)"
        )
    
    service = PayrollService(db)
    pay_run = service.get_pay_run(pay_run_id=pay_run_id)
    
    # In a real implementation, we would update the pay run status to REJECTED,
    # log the rejection reason, and possibly notify relevant parties
    
    return MessageResponse(
        message=f"Pay run {pay_run_id} rejected successfully"
    )

@router.post("/runs/{pay_run_id}/export/{format}", response_model=MessageResponse)
def export_pay_run(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
    pay_run_id: UUID,
    format: str
) -> MessageResponse:
    """
    Export pay run data in the specified format.
    
    Supported formats: csv, excel, pdf
    """
    if not current_user.has_permission("payroll:export"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to export pay run data"
        )
    
    if format.lower() not in ["csv", "excel", "pdf"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported export format. Supported formats: csv, excel, pdf"
        )
    
    # In a real implementation, we would generate and return the export file
    # For now, we'll just return a success message
    
    return MessageResponse(
        message=f"Pay run {pay_run_id} exported successfully in {format.upper()} format"
    )
