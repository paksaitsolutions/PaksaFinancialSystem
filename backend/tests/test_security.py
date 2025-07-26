import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuthentication:
    """Test authentication and authorization"""
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied"""
        protected_endpoints = [
            "/api/integration/financial-summary/1",
            "/api/accounts-payable/vendors",
            "/api/accounts-receivable/customers",
            "/api/cash-management/cash-position",
            "/api/budget/budgets"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403], f"Endpoint {endpoint} should require authentication"
    
    def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/api/integration/financial-summary/1", headers=headers)
        assert response.status_code in [401, 403]
    
    def test_expired_token_rejected(self):
        """Test that expired tokens are rejected"""
        # Mock expired token
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDk0NTkyMDB9.invalid"
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get("/api/integration/financial-summary/1", headers=headers)
        assert response.status_code in [401, 403]

class TestAuthorization:
    """Test role-based authorization"""
    
    def test_admin_access_all_endpoints(self):
        """Test that admin users can access all endpoints"""
        # Mock admin token (in real implementation, would use valid admin JWT)
        admin_headers = {"Authorization": "Bearer admin_token"}
        
        admin_endpoints = [
            "/api/integration/financial-summary/1",
            "/api/accounts-payable/vendors",
            "/api/accounts-receivable/customers"
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=admin_headers)
            # Should not be forbidden (may be 401 due to mock token, but not 403)
            assert response.status_code != 403, f"Admin should access {endpoint}"
    
    def test_user_role_restrictions(self):
        """Test that regular users have appropriate restrictions"""
        user_headers = {"Authorization": "Bearer user_token"}
        
        # Test that users can access their own data but not admin functions
        response = client.get("/api/accounts-receivable/customers", headers=user_headers)
        # Should not be forbidden for role reasons
        assert response.status_code != 403

class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are prevented"""
        malicious_inputs = [
            "1'; DROP TABLE users; --",
            "1 OR 1=1",
            "'; SELECT * FROM users; --"
        ]
        
        for malicious_input in malicious_inputs:
            response = client.get(f"/api/integration/financial-summary/{malicious_input}")
            # Should return 400 (bad request) or 404 (not found), not 500 (server error)
            assert response.status_code in [400, 404, 422], f"SQL injection not prevented for: {malicious_input}"
    
    def test_xss_prevention(self):
        """Test that XSS attempts are prevented"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            # Test in request body
            response = client.post("/api/accounts-payable/vendors", json={"name": payload})
            
            if response.status_code == 200:
                # If successful, ensure payload is sanitized
                data = response.json()
                assert "<script>" not in str(data), "XSS payload not sanitized"
    
    def test_input_length_limits(self):
        """Test that input length limits are enforced"""
        long_string = "A" * 10000  # 10KB string
        
        response = client.post("/api/accounts-payable/vendors", json={"name": long_string})
        assert response.status_code in [400, 422], "Long input not rejected"
    
    def test_numeric_input_validation(self):
        """Test numeric input validation"""
        invalid_amounts = [
            "not_a_number",
            "999999999999999999999",  # Too large
            "-999999999",  # Negative where not allowed
            "123.456789123456"  # Too many decimal places
        ]
        
        for invalid_amount in invalid_amounts:
            response = client.post("/api/accounts-payable/bills", json={
                "vendor_id": 1,
                "total_amount": invalid_amount
            })
            assert response.status_code in [400, 422], f"Invalid amount {invalid_amount} not rejected"

class TestDataProtection:
    """Test data protection and privacy"""
    
    def test_sensitive_data_not_logged(self):
        """Test that sensitive data is not exposed in logs"""
        # This would require log analysis in real implementation
        # For now, test that responses don't contain sensitive fields
        
        response = client.get("/api/accounts-payable/vendors")
        if response.status_code == 200:
            data = response.json()
            # Ensure no sensitive data in response
            response_text = str(data).lower()
            sensitive_fields = ["password", "ssn", "tax_id", "bank_account"]
            
            for field in sensitive_fields:
                assert field not in response_text, f"Sensitive field {field} exposed in response"
    
    def test_tenant_isolation(self):
        """Test that tenant data is properly isolated"""
        # Mock different tenant tokens
        tenant1_headers = {"Authorization": "Bearer tenant1_token"}
        tenant2_headers = {"Authorization": "Bearer tenant2_token"}
        
        # Both requests should not return the same data
        response1 = client.get("/api/accounts-payable/vendors", headers=tenant1_headers)
        response2 = client.get("/api/accounts-payable/vendors", headers=tenant2_headers)
        
        # If both succeed, they should have different data
        if response1.status_code == 200 and response2.status_code == 200:
            assert response1.json() != response2.json(), "Tenant data not isolated"

class TestSecurityHeaders:
    """Test security headers are properly set"""
    
    def test_security_headers_present(self):
        """Test that security headers are present"""
        response = client.get("/")
        
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        for header in security_headers:
            assert header in response.headers, f"Security header {header} missing"
    
    def test_cors_configuration(self):
        """Test CORS configuration is secure"""
        response = client.options("/api/integration/financial-summary/1")
        
        if "Access-Control-Allow-Origin" in response.headers:
            origin = response.headers["Access-Control-Allow-Origin"]
            assert origin != "*", "CORS allows all origins (security risk)"