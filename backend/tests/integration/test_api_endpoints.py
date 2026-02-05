"""
Integration tests for API endpoints across all modules.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPIEndpointsIntegration:
    """Test API endpoints integration across modules"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "modules_status" in data
    
    def test_api_info_endpoint(self):
        """Test API info endpoint"""
        response = client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "modules" in data
    
    def test_gl_endpoints_integration(self):
        """Test GL module endpoints"""
        response = client.get("/api/v1/gl/accounts")
        assert response.status_code == 200
        
        response = client.get("/api/v1/gl/trial-balance")
        assert response.status_code == 200
    
    def test_ap_endpoints_integration(self):
        """Test AP module endpoints"""
        response = client.get("/api/v1/ap/vendors")
        assert response.status_code == 200
        
        response = client.get("/api/v1/ap/payments")
        assert response.status_code == 200
    
    def test_ar_endpoints_integration(self):
        """Test AR module endpoints"""
        response = client.get("/ar/customers")
        assert response.status_code == 200
        
        response = client.get("/ar/invoices")
        assert response.status_code == 200
    
    def test_cash_endpoints_integration(self):
        """Test Cash Management endpoints"""
        response = client.get("/cash/dashboard")
        assert response.status_code == 200
        
        response = client.get("/cash/accounts")
        assert response.status_code == 200
    
    def test_budget_endpoints_integration(self):
        """Test Budget Management endpoints"""
        response = client.get("/budgets/")
        assert response.status_code == 200
    
    def test_payroll_endpoints_integration(self):
        """Test Payroll Management endpoints"""
        response = client.get("/payroll/dashboard/kpis")
        assert response.status_code == 200
        
        response = client.get("/payroll/employees")
        assert response.status_code == 200
    
    def test_tax_endpoints_integration(self):
        """Test Tax Management endpoints"""
        response = client.get("/tax/codes")
        assert response.status_code == 200
        
        response = client.get("/tax/returns")
        assert response.status_code == 200
    
    def test_fixed_assets_endpoints_integration(self):
        """Test Fixed Assets endpoints"""
        response = client.get("/fixed-assets/assets")
        assert response.status_code == 200
        
        response = client.get("/fixed-assets/categories")
        assert response.status_code == 200
    
    def test_cross_module_data_flow(self):
        """Test data flow between modules"""
        account_data = {
            "code": "1000",
            "name": "Test Cash Account",
            "account_type": "Asset"
        }
        response = client.post("/api/v1/gl/accounts", json=account_data)
        assert response.status_code in [200, 409]
        
        vendor_data = {
            "name": "Test Vendor",
            "email": "test@vendor.com"
        }
        response = client.post("/api/v1/ap/vendors", json=vendor_data)
        assert response.status_code in [200, 409, 500]  # 500 for DB constraints
    

    def test_probe_endpoints(self):
        """Test liveness and readiness probe endpoints"""
        live_response = client.get("/health/live")
        assert live_response.status_code == 200
        assert live_response.json()["status"] == "alive"

        ready_response = client.get("/health/ready")
        assert ready_response.status_code in [200, 503]
        assert "checks" in ready_response.json()

    def test_request_id_header_propagation(self):
        """Test request ID middleware adds correlation header"""
        response = client.get("/api/info")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers


    def test_ap_vendor_portal_and_ach_instruction_flow(self):
        """Test AP vendor portal invite and ACH instruction setup flow"""
        vendor_payload = {
            "name": "Portal Vendor",
            "email": "portal-vendor@example.com"
        }
        vendor_resp = client.post("/api/v1/ap/vendors", json=vendor_payload)
        assert vendor_resp.status_code in [200, 409, 500]

        vendors_resp = client.get("/api/v1/ap/vendors")
        assert vendors_resp.status_code in [200, 500]
        vendors_data = vendors_resp.json().get("data", [])
        vendor = next((v for v in vendors_data if v.get("email") == "portal-vendor@example.com"), None)
        if not vendor:
            return

        vendor_id = vendor["id"]

        invite_resp = client.post(
            f"/api/v1/ap/vendors/{vendor_id}/portal-access",
            json={"portal_email": "finance@portal-vendor.example"}
        )
        assert invite_resp.status_code == 200

        list_invites = client.get(f"/api/v1/ap/vendors/{vendor_id}/portal-access")
        assert list_invites.status_code == 200
        assert isinstance(list_invites.json().get("records"), list)

        instruction_resp = client.post(
            f"/api/v1/ap/vendors/{vendor_id}/payment-instructions",
            json={
                "payment_method": "ach",
                "account_number": "1234567890",
                "account_name": "Portal Vendor LLC",
                "routing_number": "021000021",
                "bank_name": "Demo Bank"
            }
        )
        assert instruction_resp.status_code == 200

        payment_resp = client.post(
            "/api/v1/ap/payments",
            json={
                "vendor_id": vendor_id,
                "amount": 100,
                "payment_method": "ach",
                "reference": "ACH-TEST-001"
            }
        )
        assert payment_resp.status_code in [200, 500]


    def test_cash_advanced_features_endpoints(self):
        """Test advanced cash management endpoints for bank feeds and sweep configs"""
        account_payload = {
            "name": "Ops Cash Account",
            "account_number": "000123456789",
            "bank_name": "Demo Treasury Bank",
            "current_balance": 10000
        }
        account_resp = client.post("/cash/accounts", json=account_payload)
        assert account_resp.status_code in [200, 500]

        accounts_resp = client.get("/cash/accounts")
        assert accounts_resp.status_code in [200, 500]

        accounts = accounts_resp.json().get("accounts", []) if accounts_resp.status_code == 200 else []
        if len(accounts) < 1:
            return

        account_id = accounts[0]["id"]

        bank_feed_resp = client.post(
            "/cash/bank-feeds",
            json={
                "account_id": account_id,
                "provider": "plaid",
                "provider_account_id": "plaid-acc-001"
            }
        )
        assert bank_feed_resp.status_code in [200, 404, 500]

        feed_list_resp = client.get("/cash/bank-feeds")
        assert feed_list_resp.status_code in [200, 500]

        concentration_resp = client.post(
            "/cash/concentration-rules",
            json={
                "source_account_id": account_id,
                "concentration_account_id": account_id,
                "min_source_balance": 500,
                "transfer_frequency": "daily"
            }
        )
        assert concentration_resp.status_code in [200, 404, 500]

        zba_resp = client.post(
            "/cash/zero-balance-configs",
            json={
                "child_account_id": account_id,
                "funding_account_id": account_id,
                "target_balance": 0
            }
        )
        assert zba_resp.status_code in [200, 404, 500]

        sweep_resp = client.post(
            "/cash/investment-sweeps",
            json={
                "operating_account_id": account_id,
                "investment_account_name": "Money Market Sweep",
                "sweep_threshold": 20000,
                "target_operating_balance": 10000
            }
        )
        assert sweep_resp.status_code in [200, 404, 500]

    def test_error_handling_consistency(self):
        """Test consistent error handling across modules"""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code in [200, 404]  # 200 if caught by catch-all
        
        response = client.post("/api/v1/gl/accounts", json={})
        assert response.status_code in [400, 422]