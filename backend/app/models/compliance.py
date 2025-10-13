"""
Compliance reporting models.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class ComplianceReportType(str, Enum):
    SOX_COMPLIANCE = "sox_compliance"
    AUDIT_TRAIL = "audit_trail"
    ACCESS_CONTROL = "access_control"
    DATA_RETENTION = "data_retention"
    SECURITY_ASSESSMENT = "security_assessment"
    USER_ACTIVITY = "user_activity"
    FINANCIAL_CONTROLS = "financial_controls"


class ComplianceReportStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ComplianceReport(BaseModel):
    """
    Compliance report generation and tracking.
    """
    __tablename__ = "compliance_reports"
    
    # Report identification
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)
    report_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Report parameters
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    filters = Column(JSON, nullable=True)
    
    # Report status
    status = Column(String(20), nullable=False, default=ComplianceReportStatus.PENDING)
    generated_at = Column(DateTime, nullable=True)
    
    # Report content
    report_data = Column(JSON, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(String(20), nullable=True)
    
    # Metadata
    requested_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    requester = relationship("User")
    
    def __repr__(self) -> str:
        return f"<ComplianceReport(number='{self.report_number}', type='{self.report_type}')>"


class CompliancePolicy(BaseModel):
    """
    Compliance policies and requirements.
    """
    __tablename__ = "compliance_policies"
    
    # Policy identification
    policy_name = Column(String(200), nullable=False)
    policy_code = Column(String(50), unique=True, nullable=False)
    
    # Policy details
    description = Column(Text, nullable=True)
    requirements = Column(JSON, nullable=True)
    compliance_framework = Column(String(100), nullable=True)  # SOX, PCI-DSS, etc.
    
    # Policy status
    is_active = Column(Boolean, nullable=False, default=True)
    effective_date = Column(DateTime, nullable=False)
    review_date = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<CompliancePolicy(code='{self.policy_code}', name='{self.policy_name}')>"