"""
Enhanced reports models with multi-tenant support.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class ReportType(str, Enum):
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"
    TAX_SUMMARY = "tax_summary"
    AGING_REPORT = "aging_report"
    AUDIT_LOG = "audit_log"
    CONSOLIDATED = "consolidated"


class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class ReportStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class CompanyReport(BaseModel):
    """
    Company-specific financial and operational reports.
    """
    __tablename__ = "company_reports"
    
    # Company and report identification
    company_id = Column(GUID(), nullable=False, index=True)
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)
    
    # Report parameters
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    filters = Column(JSON, nullable=True)
    
    # Report generation
    status = Column(String(20), nullable=False, default=ReportStatus.PENDING)
    generated_at = Column(DateTime, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_format = Column(String(10), nullable=True)
    
    # Report data
    report_data = Column(JSON, nullable=True)
    
    # Metadata
    generated_by = Column(GUID(), nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<CompanyReport(company_id={self.company_id}, type='{self.report_type}')>"


class ReportTemplate(BaseModel):
    """
    Company-specific report templates.
    """
    __tablename__ = "report_templates"
    
    # Company and template identification
    company_id = Column(GUID(), nullable=False, index=True)
    template_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)
    
    # Template configuration
    template_config = Column(JSON, nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self) -> str:
        return f"<ReportTemplate(company_id={self.company_id}, name='{self.template_name}')>"


class ReportSchedule(BaseModel):
    """
    Scheduled report generation for companies.
    """
    __tablename__ = "report_schedules"
    
    # Company and schedule identification
    company_id = Column(GUID(), nullable=False, index=True)
    schedule_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)
    
    # Schedule configuration
    cron_expression = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Report parameters
    report_config = Column(JSON, nullable=True)
    email_recipients = Column(JSON, nullable=True)
    
    # Status
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<ReportSchedule(company_id={self.company_id}, name='{self.schedule_name}')>"