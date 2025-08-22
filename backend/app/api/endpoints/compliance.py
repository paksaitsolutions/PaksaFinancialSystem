"""
Compliance API endpoints.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.compliance_schemas import (
    ComplianceReportRequest,
    ComplianceReportResponse,
    CompliancePolicyRequest,
    CompliancePolicyResponse,
    ComplianceReportTypesResponse,
    ComplianceDashboardResponse
)
from app.services.compliance.compliance_service import ComplianceService
from app.models.compliance import ComplianceReportType

router = APIRouter()


def get_compliance_service(db: Session = Depends(get_db)) -> ComplianceService:
    """Get an instance of the compliance service."""
    return ComplianceService(db)


@router.post(
    "/reports",
    response_model=ComplianceReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate compliance report",
    description="Generate a new compliance report.",
    tags=["Compliance Reports"]
)
async def generate_report(
    report_request: ComplianceReportRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ComplianceReportResponse:
    """Generate a new compliance report."""
    service = get_compliance_service(db)
    
    try:
        report = service.generate_report(
            report_type=report_request.report_type,
            start_date=report_request.start_date,
            end_date=report_request.end_date,
            requested_by=current_user.id,
            filters=report_request.filters,
            description=report_request.description
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/reports/{report_id}",
    response_model=ComplianceReportResponse,
    summary="Get compliance report",
    description="Get a compliance report by ID.",
    tags=["Compliance Reports"]
)
async def get_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ComplianceReportResponse:
    """Get a compliance report by ID."""
    service = get_compliance_service(db)
    
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report


@router.get(
    "/reports",
    response_model=List[ComplianceReportResponse],
    summary="List compliance reports",
    description="List compliance reports with optional filters.",
    tags=["Compliance Reports"]
)
async def list_reports(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[ComplianceReportResponse]:
    """List compliance reports with optional filters."""
    service = get_compliance_service(db)
    
    reports = service.list_reports(
        report_type=report_type,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return reports


@router.get(
    "/report-types",
    response_model=ComplianceReportTypesResponse,
    summary="Get available report types",
    description="Get list of available compliance report types.",
    tags=["Compliance Reports"]
)
async def get_report_types(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ComplianceReportTypesResponse:
    """Get available compliance report types."""
    report_types = [
        {"code": ComplianceReportType.AUDIT_TRAIL, "name": "Audit Trail Report"},
        {"code": ComplianceReportType.ACCESS_CONTROL, "name": "Access Control Report"},
        {"code": ComplianceReportType.USER_ACTIVITY, "name": "User Activity Report"},
        {"code": ComplianceReportType.SECURITY_ASSESSMENT, "name": "Security Assessment Report"},
        {"code": ComplianceReportType.SOX_COMPLIANCE, "name": "SOX Compliance Report"},
    ]
    
    return ComplianceReportTypesResponse(report_types=report_types)


@router.post(
    "/policies",
    response_model=CompliancePolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create compliance policy",
    description="Create a new compliance policy.",
    tags=["Compliance Policies"]
)
async def create_policy(
    policy_request: CompliancePolicyRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompliancePolicyResponse:
    """Create a new compliance policy."""
    service = get_compliance_service(db)
    
    try:
        policy = service.create_policy(policy_request.dict(), current_user.id)
        return policy
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/policies",
    response_model=List[CompliancePolicyResponse],
    summary="List compliance policies",
    description="List compliance policies.",
    tags=["Compliance Policies"]
)
async def list_policies(
    active_only: bool = Query(True, description="Show only active policies"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[CompliancePolicyResponse]:
    """List compliance policies."""
    service = get_compliance_service(db)
    
    policies = service.list_policies(active_only=active_only)
    return policies


@router.get(
    "/dashboard",
    response_model=ComplianceDashboardResponse,
    summary="Get compliance dashboard",
    description="Get compliance dashboard data.",
    tags=["Compliance Dashboard"]
)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ComplianceDashboardResponse:
    """Get compliance dashboard data."""
    service = get_compliance_service(db)
    
    # Get report statistics
    all_reports = service.list_reports(limit=1000)
    total_reports = len(all_reports)
    pending_reports = len([r for r in all_reports if r.status == "pending"])
    completed_reports = len([r for r in all_reports if r.status == "completed"])
    failed_reports = len([r for r in all_reports if r.status == "failed"])
    
    # Get recent reports
    recent_reports = service.list_reports(limit=5)
    
    # Get policy count
    policies = service.list_policies(active_only=True)
    active_policies = len(policies)
    
    # Calculate compliance score (simplified)
    compliance_score = (completed_reports / max(total_reports, 1)) * 100
    
    return ComplianceDashboardResponse(
        total_reports=total_reports,
        pending_reports=pending_reports,
        completed_reports=completed_reports,
        failed_reports=failed_reports,
        recent_reports=recent_reports,
        active_policies=active_policies,
        compliance_score=compliance_score
    )