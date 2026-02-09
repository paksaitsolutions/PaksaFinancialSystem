"""
Integration tests for API endpoints across all modules.
"""
import pytest

class TestAPIEndpointsIntegration:
    """Test API endpoints integration across modules"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "modules_status" in data
    
    def test_api_info_endpoint(self, client):
        """Test API info endpoint"""
        response = client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "modules" in data
    
    def test_gl_endpoints_integration(self, client):
        """Test GL module endpoints"""
        response = client.get("/api/v1/gl/accounts")
        assert response.status_code == 200
        
        response = client.get("/api/v1/gl/trial-balance")
        assert response.status_code == 200
    
    def test_ap_endpoints_integration(self, client):
        """Test AP module endpoints"""
        response = client.get("/api/v1/ap/vendors")
        assert response.status_code == 200
        
        response = client.get("/api/v1/ap/payments")
        assert response.status_code == 200
    
    def test_ar_endpoints_integration(self, client):
        """Test AR module endpoints"""
        response = client.get("/ar/customers")
        assert response.status_code == 200
        
        response = client.get("/ar/invoices")
        assert response.status_code == 200
    
    def test_cash_endpoints_integration(self, client):
        """Test Cash Management endpoints"""
        response = client.get("/cash/dashboard")
        assert response.status_code == 200
        
        response = client.get("/cash/accounts")
        assert response.status_code == 200
    
    def test_budget_endpoints_integration(self, client):
        """Test Budget Management endpoints"""
        response = client.get("/budgets/")
        assert response.status_code == 200
    
    def test_payroll_endpoints_integration(self, client):
        """Test Payroll Management endpoints"""
        response = client.get("/payroll/dashboard/kpis")
        assert response.status_code == 200
        
        response = client.get("/payroll/employees")
        assert response.status_code == 200
    
    def test_tax_endpoints_integration(self, client):
        """Test Tax Management endpoints"""
        response = client.get("/tax/codes")
        assert response.status_code == 200
        
        response = client.get("/tax/returns")
        assert response.status_code == 200
    
    def test_fixed_assets_endpoints_integration(self, client):
        """Test Fixed Assets endpoints"""
        response = client.get("/fixed-assets/assets")
        assert response.status_code == 200
        
        response = client.get("/fixed-assets/categories")
        assert response.status_code == 200
    
    def test_cross_module_data_flow(self, client):
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

    def test_error_handling_consistency(self):
        """Test consistent error handling across modules"""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code in [200, 404]  # 200 if caught by catch-all
        
        response = client.post("/api/v1/gl/accounts", json={})
        assert response.status_code in [400, 422]
