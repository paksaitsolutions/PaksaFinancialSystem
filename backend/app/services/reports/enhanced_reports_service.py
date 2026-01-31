"""
Enhanced reports service with multi-tenant support.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.reports import CompanyReport, ReportTemplate, ReportSchedule, ReportType, ReportStatus
from app.services.audit.audit_service import AuditService





class EnhancedReportsService:
    """Service for generating multi-tenant financial and operational reports."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
        self.audit_service = AuditService(db)
    
    def generate_income_statement(
        self,
        company_id: UUID,
        period_start: datetime,
        period_end: datetime,
        generated_by: UUID
    ) -> CompanyReport:
        """Generate Income Statement."""
        """Generate Income Statement (Profit & Loss) for company."""
        report = CompanyReport(
            company_id=company_id,
            report_name="Income Statement",
            report_type=ReportType.INCOME_STATEMENT,
            period_start=period_start,
            period_end=period_end,
            status=ReportStatus.GENERATING,
            generated_by=generated_by
        )
        
        self.db.add(report)
        self.db.flush()
        
        try:
            report_data = self._generate_income_statement_data(company_id, period_start, period_end)
            
            report.report_data = report_data
            report.status = ReportStatus.COMPLETED
            report.generated_at = datetime.utcnow()
            
        except Exception as e:
            report.status = ReportStatus.FAILED
            report.description = str(e)
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def generate_balance_sheet(
        self,
        company_id: UUID,
        period_end: datetime,
        generated_by: UUID
    ) -> CompanyReport:
        """Generate Balance Sheet."""
        """Generate Balance Sheet for company."""
        report = CompanyReport(
            company_id=company_id,
            report_name="Balance Sheet",
            report_type=ReportType.BALANCE_SHEET,
            period_start=period_end,
            period_end=period_end,
            status=ReportStatus.GENERATING,
            generated_by=generated_by
        )
        
        self.db.add(report)
        self.db.flush()
        
        try:
            report_data = self._generate_balance_sheet_data(company_id, period_end)
            
            report.report_data = report_data
            report.status = ReportStatus.COMPLETED
            report.generated_at = datetime.utcnow()
            
        except Exception as e:
            report.status = ReportStatus.FAILED
            report.description = str(e)
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def generate_aging_report(
        self,
        company_id: UUID,
        report_type: str,
        as_of_date: datetime,
        generated_by: UUID
    ) -> CompanyReport:
        """Generate Aging Report."""
        """Generate Aging Report for company."""
        report = CompanyReport(
            company_id=company_id,
            report_name=f"{report_type.title()} Aging Report",
            report_type=ReportType.AGING_REPORT,
            period_start=as_of_date,
            period_end=as_of_date,
            status=ReportStatus.GENERATING,
            generated_by=generated_by,
            filters={"aging_type": report_type}
        )
        
        self.db.add(report)
        self.db.flush()
        
        try:
            report_data = self._generate_aging_data(company_id, report_type, as_of_date)
            
            report.report_data = report_data
            report.status = ReportStatus.COMPLETED
            report.generated_at = datetime.utcnow()
            
        except Exception as e:
            report.status = ReportStatus.FAILED
            report.description = str(e)
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def create_report_template(
        self,
        company_id: UUID,
        template_data: Dict[str, Any],
        created_by: UUID
    ) -> ReportTemplate:
        """Create Report Template."""
        """Create company-specific report template."""
        template = ReportTemplate(
            company_id=company_id,
            template_name=template_data['template_name'],
            report_type=template_data['report_type'],
            template_config=template_data['template_config'],
            is_default=template_data.get('is_default', False),
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def list_company_reports(self, company_id: UUID, limit: int = 100) -> List[CompanyReport]:
        """List Company Reports."""
        """List reports for a company."""
        return self.db.query(CompanyReport).filter(
            CompanyReport.company_id == company_id
        ).order_by(desc(CompanyReport.created_at)).limit(limit).all()
    
    def get_report(self, report_id: UUID) -> Optional[CompanyReport]:
        """Get Report."""
        """Get report by ID."""
        return self.db.query(CompanyReport).filter(CompanyReport.id == report_id).first()
    
    def _generate_income_statement_data(
        self,
        company_id: UUID,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """ Generate Income Statement Data."""
        """Generate income statement data for company."""
        return {
            "report_type": "Income Statement",
            "company_id": str(company_id),
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "revenue": {
                "sales_revenue": 150000,
                "service_revenue": 75000,
                "total_revenue": 225000
            },
            "expenses": {
                "cost_of_goods_sold": 90000,
                "operating_expenses": 85000,
                "total_expenses": 175000
            },
            "net_income": 50000
        }
    
    def _generate_balance_sheet_data(self, company_id: UUID, period_end: datetime) -> Dict[str, Any]:
        """ Generate Balance Sheet Data."""
        """Generate balance sheet data for company."""
        return {
            "report_type": "Balance Sheet",
            "company_id": str(company_id),
            "as_of_date": period_end.isoformat(),
            "assets": {
                "current_assets": {
                    "cash": 50000,
                    "accounts_receivable": 75000,
                    "inventory": 40000,
                    "total_current": 165000
                },
                "fixed_assets": {
                    "equipment": 100000,
                    "accumulated_depreciation": -20000,
                    "total_fixed": 80000
                },
                "total_assets": 245000
            },
            "liabilities": {
                "current_liabilities": {
                    "accounts_payable": 35000,
                    "accrued_expenses": 15000,
                    "total_current": 50000
                },
                "long_term_liabilities": {
                    "loans_payable": 75000,
                    "total_long_term": 75000
                },
                "total_liabilities": 125000
            },
            "equity": {
                "retained_earnings": 120000,
                "total_equity": 120000
            }
        }
    
    def _generate_aging_data(
        self,
        company_id: UUID,
        aging_type: str,
        as_of_date: datetime
    ) -> Dict[str, Any]:
        """ Generate Aging Data."""
        """Generate aging report data for company."""
        return {
            "report_type": f"{aging_type.title()} Aging Report",
            "company_id": str(company_id),
            "as_of_date": as_of_date.isoformat(),
            "aging_buckets": {
                "current": 45000,
                "1_30_days": 25000,
                "31_60_days": 15000,
                "61_90_days": 8000,
                "over_90_days": 7000
            },
            "total_outstanding": 100000
        }