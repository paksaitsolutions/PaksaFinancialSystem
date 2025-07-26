import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from decimal import Decimal

from app.main import app
from app.modules.integration.cross_module_service import CrossModuleIntegrationService
from app.modules.integration.workflow_integration_service import WorkflowIntegrationService

client = TestClient(app)

class TestCrossModuleIntegration:
    """Test cross-module integration functionality"""
    
    @pytest.mark.asyncio
    async def test_ap_to_cash_sync(self, db_session: AsyncSession):
        """Test AP payment sync to cash management"""
        service = CrossModuleIntegrationService()
        
        # Mock AP payment data
        payment_id = 1
        result = await service.sync_ap_to_cash_management(db_session, payment_id)
        
        assert result is not None
        assert "bank_transaction_id" in result
        assert result["sync_status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_ar_to_cash_sync(self, db_session: AsyncSession):
        """Test AR payment sync to cash management"""
        service = CrossModuleIntegrationService()
        
        payment_id = 1
        result = await service.sync_ar_to_cash_management(db_session, payment_id)
        
        assert result is not None
        assert "bank_transaction_id" in result
        assert result["sync_status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_integrated_financial_summary(self, db_session: AsyncSession):
        """Test integrated financial summary"""
        service = CrossModuleIntegrationService()
        
        company_id = 1
        result = await service.get_integrated_financial_summary(db_session, company_id)
        
        assert result is not None
        assert "financial_summary" in result
        assert "accounts_payable" in result["financial_summary"]
        assert "accounts_receivable" in result["financial_summary"]
        assert "cash_management" in result["financial_summary"]
        assert "budget_management" in result["financial_summary"]

class TestWorkflowIntegration:
    """Test integrated workflow functionality"""
    
    @pytest.mark.asyncio
    async def test_purchase_to_payment_workflow(self, db_session: AsyncSession):
        """Test complete purchase-to-payment workflow"""
        service = WorkflowIntegrationService()
        
        purchase_data = {
            "bill_number": "TEST-001",
            "bill_date": "2024-01-15",
            "due_date": "2024-02-15",
            "total_amount": 500.00,
            "bank_account_id": 1,
            "vendor_data": {
                "name": "Test Vendor",
                "email": "vendor@test.com"
            }
        }
        
        result = await service.process_purchase_to_payment_workflow(db_session, purchase_data, 1)
        
        assert result is not None
        assert "workflow_id" in result
        assert result["status"] in ["completed", "pending_approval"]
        assert len(result["workflow_results"]) > 0
    
    @pytest.mark.asyncio
    async def test_invoice_to_cash_workflow(self, db_session: AsyncSession):
        """Test complete invoice-to-cash workflow"""
        service = WorkflowIntegrationService()
        
        invoice_data = {
            "customer_id": 1,
            "total_amount": 1000.00,
            "invoice_date": "2024-01-15"
        }
        
        result = await service.process_invoice_to_cash_workflow(db_session, invoice_data, 1)
        
        assert result is not None
        assert "workflow_id" in result
        assert "invoice_id" in result

class TestIntegrationAPI:
    """Test integration API endpoints"""
    
    def test_financial_summary_endpoint(self):
        """Test financial summary API endpoint"""
        response = client.get("/api/integration/financial-summary/1")
        assert response.status_code == 200
        
        data = response.json()
        assert "financial_summary" in data
        assert "integration_status" in data
    
    def test_executive_dashboard_endpoint(self):
        """Test executive dashboard API endpoint"""
        response = client.get(
            "/api/integration/reports/executive-dashboard/1",
            params={
                "period_start": "2024-01-01",
                "period_end": "2024-01-31"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "executive_summary" in data
        assert "module_summaries" in data
    
    def test_cash_flow_statement_endpoint(self):
        """Test cash flow statement API endpoint"""
        response = client.get(
            "/api/integration/reports/cash-flow-statement/1",
            params={
                "period_start": "2024-01-01",
                "period_end": "2024-01-31"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "cash_flow_statement" in data
    
    def test_purchase_to_payment_workflow_endpoint(self):
        """Test purchase-to-payment workflow API endpoint"""
        workflow_data = {
            "bill_number": "API-TEST-001",
            "total_amount": 750.00,
            "bill_date": "2024-01-15",
            "due_date": "2024-02-15",
            "bank_account_id": 1,
            "vendor_data": {
                "name": "API Test Vendor",
                "email": "apitest@vendor.com"
            }
        }
        
        response = client.post("/api/integration/workflows/purchase-to-payment", json=workflow_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "workflow_id" in data
        assert "workflow_results" in data

@pytest.fixture
async def db_session():
    """Mock database session for testing"""
    # In real implementation, would return actual test database session
    return None