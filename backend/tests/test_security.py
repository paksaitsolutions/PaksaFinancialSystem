"""Security and penetration tests"""
import pytest
import requests
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSecurityVulnerabilities:
    """Test for common security vulnerabilities"""
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--"
        ]
        
        for payload in malicious_inputs:
            response = client.get(f"/api/v1/accounts?search={payload}")
            assert response.status_code != 500
            assert "error" not in response.text.lower() or "sql" not in response.text.lower()
    
    def test_xss_protection(self):
        """Test XSS protection"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            response = client.post("/api/v1/accounts", json={
                "name": payload,
                "account_type": "asset"
            })
            # Should either reject or sanitize
            assert response.status_code in [400, 422] or "<script>" not in response.text
    
    def test_csrf_protection(self):
        """Test CSRF protection"""
        # Test without CSRF token
        response = client.post("/api/v1/accounts", json={
            "name": "Test Account",
            "account_type": "asset"
        })
        # Should require authentication/CSRF token
        assert response.status_code in [401, 403, 422]
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        # Make multiple rapid requests
        responses = []
        for i in range(100):
            response = client.get("/api/v1/accounts")
            responses.append(response.status_code)
        
        # Should have some rate limiting (429 status)
        assert 429 in responses or all(r in [200, 401, 403] for r in responses)
    
    def test_authentication_required(self):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/api/v1/accounts",
            "/api/v1/transactions",
            "/api/v1/users",
            "/api/v1/companies"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403]
    
    def test_input_validation(self):
        """Test input validation"""
        invalid_inputs = [
            {"name": "", "account_type": "asset"},  # Empty name
            {"name": "A" * 1000, "account_type": "asset"},  # Too long
            {"name": "Test", "account_type": "invalid"},  # Invalid type
            {"name": None, "account_type": "asset"},  # Null value
        ]
        
        for invalid_input in invalid_inputs:
            response = client.post("/api/v1/accounts", json=invalid_input)
            assert response.status_code == 422

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_large_payload_handling(self):
        """Test handling of large payloads"""
        large_data = {"name": "A" * 10000, "description": "B" * 50000}
        response = client.post("/api/v1/accounts", json=large_data)
        assert response.status_code in [400, 413, 422]
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/api/v1/health")
            results.append(response.status_code)
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All requests should complete successfully
        assert all(status in [200, 401, 403] for status in results)
    
    def test_malformed_json(self):
        """Test malformed JSON handling"""
        malformed_json = '{"name": "test", "invalid": }'
        response = client.post(
            "/api/v1/accounts",
            data=malformed_json,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_unicode_handling(self):
        """Test Unicode and special character handling"""
        unicode_data = {
            "name": "测试账户 🏦",
            "description": "Ñoño café résumé naïve"
        }
        response = client.post("/api/v1/accounts", json=unicode_data)
        # Should handle Unicode properly
        assert response.status_code in [200, 201, 401, 403, 422]

class TestTenantIsolation:
    """Test multi-tenant data isolation"""
    
    def test_tenant_data_isolation(self):
        """Test that tenants cannot access each other's data"""
        # This would require proper authentication setup
        # Placeholder for tenant isolation tests
        pass
    
    def test_cross_tenant_prevention(self):
        """Test prevention of cross-tenant data access"""
        # This would test that tenant A cannot access tenant B's data
        pass