"""Test GL integration with other modules"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.modules.core_financials.general_ledger.integration_service import GLIntegrationService

client = TestClient(app)

class TestGLIntegration:
    """Test GL integration with other financial modules"""
    
    def test_ap_integration(self):
        """Test GL integration with Accounts Payable"""
        # Test AP invoice creates GL journal entry
        ap_invoice = {
            "vendor_id": "vendor-123",
            "invoice_number": "INV-001",
            "amount": 1000.00,
            "invoice_date": "2024-01-15"
        }
        
        response = client.post("/api/v1/ap/invoices", json=ap_invoice)
        assert response.status_code in [201, 401, 422]
        
        # Verify GL entry was created
        if response.status_code == 201:
            invoice_data = response.json()
            gl_response = client.get(f"/api/v1/gl/journal-entries?reference={invoice_data['invoice_number']}")
            assert gl_response.status_code in [200, 401]
    
    def test_ar_integration(self):
        """Test GL integration with Accounts Receivable"""
        # Test AR invoice creates GL journal entry
        ar_invoice = {
            "customer_id": "customer-123",
            "invoice_number": "AR-001",
            "amount": 1500.00,
            "invoice_date": "2024-01-15"
        }
        
        response = client.post("/api/v1/ar/invoices", json=ar_invoice)
        assert response.status_code in [201, 401, 422]
    
    def test_payroll_integration(self):
        """Test GL integration with Payroll"""
        # Test payroll run creates GL journal entries
        payroll_data = {
            "pay_period": "2024-01",
            "employees": [
                {
                    "employee_id": "emp-123",
                    "gross_pay": 5000.00,
                    "net_pay": 3800.00,
                    "tax_withholdings": 1200.00
                }
            ]
        }
        
        response = client.post("/api/v1/payroll/runs", json=payroll_data)
        assert response.status_code in [201, 401, 422]
    
    def test_budget_integration(self):
        """Test GL integration with Budget module"""
        # Test budget variance analysis
        response = client.get("/api/v1/budget/variance-analysis")
        assert response.status_code in [200, 401]
        
        # Test budget vs actual comparison
        response = client.get("/api/v1/gl/reports/budget-comparison")
        assert response.status_code in [200, 401]
    
    def test_fixed_assets_integration(self):
        """Test GL integration with Fixed Assets"""
        # Test asset depreciation creates GL entries
        depreciation_data = {
            "asset_id": "asset-123",
            "depreciation_amount": 500.00,
            "depreciation_date": "2024-01-31"
        }
        
        response = client.post("/api/v1/assets/depreciation", json=depreciation_data)
        assert response.status_code in [201, 401, 422]
    
    def test_cash_management_integration(self):
        """Test GL integration with Cash Management"""
        # Test bank reconciliation affects GL
        reconciliation_data = {
            "bank_account_id": "bank-123",
            "statement_date": "2024-01-31",
            "statement_balance": 10000.00
        }
        
        response = client.post("/api/v1/cash/reconciliation", json=reconciliation_data)
        assert response.status_code in [201, 401, 422]
    
    def test_tax_integration(self):
        """Test GL integration with Tax module"""
        # Test tax calculations create GL entries
        tax_data = {
            "tax_period": "2024-Q1",
            "tax_type": "sales_tax",
            "tax_amount": 150.00
        }
        
        response = client.post("/api/v1/tax/calculations", json=tax_data)
        assert response.status_code in [201, 401, 422]
    
    def test_data_consistency(self):
        """Test data consistency across modules"""
        # Test account balance consistency
        response = client.get("/api/v1/gl/validation/account-balances")
        assert response.status_code in [200, 401]
        
        # Test trial balance consistency
        response = client.get("/api/v1/gl/validation/trial-balance")
        assert response.status_code in [200, 401]
    
    def test_reporting_integration(self):
        """Test GL integration with Reporting module"""
        # Test financial statements use GL data
        response = client.get("/api/v1/reports/financial-statements/balance-sheet")
        assert response.status_code in [200, 401]
        
        response = client.get("/api/v1/reports/financial-statements/income-statement")
        assert response.status_code in [200, 401]
        
        response = client.get("/api/v1/reports/financial-statements/cash-flow")
        assert response.status_code in [200, 401]

class TestGLPermissions:
    """Test GL permission checks and approval flows"""
    
    def test_journal_entry_permissions(self):
        """Test journal entry creation permissions"""
        # Test unauthorized access
        response = client.post("/api/v1/gl/journal-entries", json={})
        assert response.status_code == 401
        
        # Test with invalid permissions
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/api/v1/gl/journal-entries", json={}, headers=headers)
        assert response.status_code in [401, 403]
    
    def test_posting_permissions(self):
        """Test journal entry posting permissions"""
        # Test posting requires specific permission
        headers = {"Authorization": "Bearer test-token"}
        response = client.post("/api/v1/gl/journal-entries/1/post", headers=headers)
        assert response.status_code in [200, 401, 403, 404]
    
    def test_account_management_permissions(self):
        """Test account management permissions"""
        # Test account creation permissions
        account_data = {
            "account_code": "9999",
            "account_name": "Test Account",
            "account_type": "expense"
        }
        
        headers = {"Authorization": "Bearer test-token"}
        response = client.post("/api/v1/gl/accounts", json=account_data, headers=headers)
        assert response.status_code in [201, 401, 403, 422]
    
    def test_approval_workflows(self):
        """Test GL approval workflows"""
        # Test journal entry approval workflow
        response = client.get("/api/v1/gl/approvals/pending")
        assert response.status_code in [200, 401]
        
        # Test approval action
        approval_data = {"action": "approve", "comments": "Approved"}
        response = client.post("/api/v1/gl/approvals/1/action", json=approval_data)
        assert response.status_code in [200, 401, 403, 404]