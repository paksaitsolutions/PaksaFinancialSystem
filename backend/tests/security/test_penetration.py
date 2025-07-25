import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core.security.input_validation import sanitize_sql_input
import requests

client = TestClient(app)

class TestPenetrationSecurity:
    """Penetration testing for security vulnerabilities"""
    
    def test_sql_injection_attempts(self):
        """Test SQL injection attack vectors"""
        sql_payloads = [
            "'; DROP TABLE accounts; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker'); --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1#"
        ]
        
        for payload in sql_payloads:
            response = client.get(f"/api/v1/accounts/{payload}")
            assert response.status_code in [400, 422, 404]  # Should be blocked
    
    def test_xss_attack_vectors(self):
        """Test XSS attack prevention"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        for payload in xss_payloads:
            data = {"name": payload, "description": payload}
            response = client.post("/api/v1/accounts/", json=data)
            # Should either be sanitized or rejected
            assert response.status_code in [400, 422] or "script" not in str(response.content)
    
    def test_csrf_protection(self):
        """Test CSRF protection mechanisms"""
        # Attempt POST without CSRF token
        response = client.post("/api/v1/accounts/", json={"name": "test"})
        assert response.status_code == 403  # Should be blocked
        
        # Attempt with invalid CSRF token
        headers = {"X-CSRF-Token": "invalid_token"}
        response = client.post("/api/v1/accounts/", json={"name": "test"}, headers=headers)
        assert response.status_code == 403
    
    def test_rate_limiting_bypass_attempts(self):
        """Test rate limiting bypass attempts"""
        # Rapid fire requests
        for i in range(150):  # Exceed 100/minute limit
            response = client.get("/api/v1/health")
            if response.status_code == 429:
                break
        
        assert response.status_code == 429  # Should be rate limited
    
    def test_jwt_token_manipulation(self):
        """Test JWT token manipulation attempts"""
        malicious_tokens = [
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4ifQ.invalid",
            "Bearer malicious_token",
            "null",
            "",
            "../../etc/passwd"
        ]
        
        for token in malicious_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/protected-endpoint", headers=headers)
            assert response.status_code == 401  # Should be unauthorized
    
    def test_directory_traversal(self):
        """Test directory traversal attempts"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd"
        ]
        
        for payload in traversal_payloads:
            response = client.get(f"/api/v1/files/{payload}")
            assert response.status_code in [400, 404, 403]  # Should be blocked

class TestInputSanitization:
    """Test input sanitization functions"""
    
    def test_sql_sanitization(self):
        """Test SQL input sanitization"""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "admin'--",
            "' OR 1=1 --"
        ]
        
        for input_val in dangerous_inputs:
            sanitized = sanitize_sql_input(input_val)
            assert "DROP" not in sanitized
            assert "--" not in sanitized
            assert "'" not in sanitized
    
    def test_html_escaping(self):
        """Test HTML escaping"""
        from app.core.security.input_validation import SecureBaseModel
        
        class TestModel(SecureBaseModel):
            content: str
        
        dangerous_html = "<script>alert('xss')</script>"
        model = TestModel(content=dangerous_html)
        assert "&lt;script&gt;" in model.content
        assert "<script>" not in model.content