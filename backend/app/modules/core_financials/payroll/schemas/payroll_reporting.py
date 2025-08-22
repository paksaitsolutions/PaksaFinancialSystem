"""
Payroll reporting schemas for the Payroll module.
"""
from datetime import date
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


class ReportTypeEnum(str, Enum):
    PAYROLL_SUMMARY = "PAYROLL_SUMMARY"
    EMPLOYEE_EARNINGS = "EMPLOYEE_EARNINGS"
    TAX_LIABILITY = "TAX_LIABILITY"
    BENEFITS_REPORT = "BENEFITS_REPORT"
    DEPARTMENT_COSTS = "DEPARTMENT_COSTS"
    YEAR_END_SUMMARY = "YEAR_END_SUMMARY"


class ReportFormatEnum(str, Enum):
    PDF = "PDF"
    EXCEL = "EXCEL"
    CSV = "CSV"


class PayrollReportRequest(BaseModel):
    """Request for generating payroll reports."""
    report_type: ReportTypeEnum
    start_date: date
    end_date: date
    department: Optional[str] = None
    employee_ids: Optional[List[UUID]] = None
    format: ReportFormatEnum = ReportFormatEnum.PDF


class PayrollSummaryReport(BaseModel):
    """Payroll summary report data."""
    period_start: date
    period_end: date
    total_employees: int
    total_gross_pay: Decimal
    total_net_pay: Decimal
    total_taxes: Decimal
    total_benefits: Decimal
    by_department: Dict[str, Dict[str, Any]]


class EmployeeEarningsReport(BaseModel):
    """Employee earnings report data."""
    employee_id: UUID
    employee_name: str
    employee_code: str
    department: str
    total_gross: Decimal
    total_net: Decimal
    total_taxes: Decimal
    total_benefits: Decimal
    pay_periods: List[Dict[str, Any]]


class TaxLiabilityReport(BaseModel):
    """Tax liability report data."""
    period_start: date
    period_end: date
    federal_income_tax: Decimal
    state_income_tax: Decimal
    social_security_tax: Decimal
    medicare_tax: Decimal
    unemployment_tax: Decimal
    total_tax_liability: Decimal
    by_employee: List[Dict[str, Any]]


class BenefitsReport(BaseModel):
    """Benefits report data."""
    period_start: date
    period_end: date
    total_employee_contributions: Decimal
    total_employer_contributions: Decimal
    by_benefit_type: Dict[str, Dict[str, Any]]
    by_employee: List[Dict[str, Any]]


class DepartmentCostsReport(BaseModel):
    """Department costs report data."""
    period_start: date
    period_end: date
    departments: List[Dict[str, Any]]
    total_cost: Decimal


class YearEndSummary(BaseModel):
    """Year-end summary report data."""
    year: int
    total_employees: int
    total_gross_pay: Decimal
    total_net_pay: Decimal
    total_taxes: Decimal
    total_benefits: Decimal
    quarterly_breakdown: List[Dict[str, Any]]
    top_earners: List[Dict[str, Any]]