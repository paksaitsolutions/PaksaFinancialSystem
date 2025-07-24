"""
Schemas for compliance operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class ComplianceReportRequest(BaseModel):
    """Schema for compliance report generation request."""
    report_type: str = Field(..., description="Type of compliance report")
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    description: Optional[str] = Field(None, description="Report description")


class ComplianceReportResponse(BaseModel):
    """Schema for compliance report response."""
    id: UUID = Field(..., description="Report ID")
    report_name: str = Field(..., description="Report name")
    report_type: str = Field(..., description="Report type")
    report_number: str = Field(..., description="Report number")
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    status: str = Field(..., description="Report status")
    generated_at: Optional[datetime] = Field(None, description="Generation timestamp")
    report_data: Optional[Dict[str, Any]] = Field(None, description="Report data")
    file_path: Optional[str] = Field(None, description="File path")
    file_size: Optional[str] = Field(None, description="File size")
    requested_by: UUID = Field(..., description="Requester user ID")
    description: Optional[str] = Field(None, description="Report description")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True


class CompliancePolicyRequest(BaseModel):
    """Schema for compliance policy creation request."""
    policy_name: str = Field(..., description="Policy name")
    policy_code: str = Field(..., description="Policy code")
    description: Optional[str] = Field(None, description="Policy description")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Policy requirements")
    compliance_framework: Optional[str] = Field(None, description="Compliance framework")
    effective_date: datetime = Field(..., description="Effective date")
    review_date: Optional[datetime] = Field(None, description="Review date")


class CompliancePolicyResponse(BaseModel):
    """Schema for compliance policy response."""
    id: UUID = Field(..., description="Policy ID")
    policy_name: str = Field(..., description="Policy name")
    policy_code: str = Field(..., description="Policy code")
    description: Optional[str] = Field(None, description="Policy description")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Policy requirements")
    compliance_framework: Optional[str] = Field(None, description="Compliance framework")
    is_active: bool = Field(..., description="Whether policy is active")
    effective_date: datetime = Field(..., description="Effective date")
    review_date: Optional[datetime] = Field(None, description="Review date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class ComplianceReportTypesResponse(BaseModel):
    """Schema for available compliance report types."""
    report_types: List[Dict[str, str]] = Field(..., description="Available report types")


class ComplianceDashboardResponse(BaseModel):
    """Schema for compliance dashboard data."""
    total_reports: int = Field(..., description="Total number of reports")
    pending_reports: int = Field(..., description="Number of pending reports")
    completed_reports: int = Field(..., description="Number of completed reports")
    failed_reports: int = Field(..., description="Number of failed reports")
    recent_reports: List[ComplianceReportResponse] = Field(..., description="Recent reports")
    active_policies: int = Field(..., description="Number of active policies")
    compliance_score: float = Field(..., description="Overall compliance score")