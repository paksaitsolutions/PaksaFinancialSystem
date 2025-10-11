"""
Tests for consolidated reporting across all modules
"""
import pytest
from datetime import date
from app.services.consolidated_reporting_service import ConsolidatedReportingService
from app.models import *

class TestConsolidatedReporting:
    
    def test_module_activity_report(self, db_session, sample_company):
        service = ConsolidatedReportingService(db_session)
        
        report = service.generate_module_activity_report(
            company_id=sample_company.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        
        assert "modules" in report
        assert "accounts_payable" in report["modules"]
        assert "accounts_receivable" in report["modules"]
        assert "payroll" in report["modules"]
        assert "cash_management" in report["modules"]
    
    def test_account_activity_summary(self, db_session, sample_company):
        service = ConsolidatedReportingService(db_session)
        
        summary = service.generate_account_activity_summary(
            company_id=sample_company.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            account_types=["Asset", "Liability"]
        )
        
        assert "account_summary" in summary
        assert summary["account_types_included"] == ["Asset", "Liability"]
    
    def test_integration_health_report(self, db_session, sample_company):
        service = ConsolidatedReportingService(db_session)
        
        health = service.generate_integration_health_report(sample_company.id)
        
        assert "integration_health" in health
        assert "health_score" in health["integration_health"]
        assert "recommendations" in health
        assert isinstance(health["integration_health"]["health_score"], float)