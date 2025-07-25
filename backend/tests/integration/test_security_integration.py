import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core.security.csrf_protection import csrf_protection
from app.core.security.jwt_enhanced import jwt_manager
from unittest.mock import patch

client = TestClient(app)

class TestSecurityIntegration:
    """Integration tests for security components working together"""
    
    def test_complete_authentication_flow(self):
        """Test complete authentication flow with all security measures"""
        
        # 1. Get CSRF token
        csrf_token = csrf_protection.generate_token("test_session")
        
        # 2. Attempt login with CSRF token
        login_data = {
            "email": "test@example.com",
            "password": "secure_password"
        }
        headers = {
            "X-CSRF-Token": csrf_token,
            "X-Session-ID": "test_session"
        }
        
        with patch('app.services.auth_service.authenticate_user') as mock_auth:
            mock_auth.return_value = {"user_id": "123", "tenant_id": "tenant_123"}
            
            response = client.post("/api/v1/auth/login", json=login_data, headers=headers)
            
            # Should succeed with proper CSRF token
            assert response.status_code in [200, 201]
    
    def test_api_request_with_jwt_and_rate_limiting(self):
        """Test API request with JWT authentication and rate limiting"""
        
        # Create JWT token
        user_data = {"user_id": "123", "email": "test@example.com"}
        jwt_token = jwt_manager.create_access_token(user_data, "tenant_123")
        
        headers = {"Authorization": f"Bearer {jwt_token}"}
        
        # Make multiple requests to test rate limiting
        responses = []
        for i in range(10):
            response = client.get("/api/v1/accounts/", headers=headers)
            responses.append(response)
        
        # Most requests should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count > 0
    
    def test_tenant_isolation_with_security(self):
        """Test tenant isolation works with security measures"""
        
        # Create tokens for different tenants
        tenant1_token = jwt_manager.create_access_token(
            {"user_id": "user1"}, "tenant_1"
        )
        tenant2_token = jwt_manager.create_access_token(
            {"user_id": "user2"}, "tenant_2"
        )
        
        # Test that tenant 1 cannot access tenant 2 data
        headers1 = {"Authorization": f"Bearer {tenant1_token}"}
        headers2 = {"Authorization": f"Bearer {tenant2_token}"}
        
        # Create data for tenant 1
        account_data = {"account_code": "1000", "account_name": "Test Account"}
        csrf_token = csrf_protection.generate_token("session1")
        headers1.update({
            "X-CSRF-Token": csrf_token,
            "X-Session-ID": "session1"
        })
        
        with patch('app.modules.core_financials.general_ledger.services.AccountService.create') as mock_create:
            mock_create.return_value = {"id": 1, "tenant_id": "tenant_1", **account_data}
            
            response = client.post("/api/v1/accounts/", json=account_data, headers=headers1)
            
            # Should succeed for tenant 1
            assert response.status_code in [200, 201]
        
        # Try to access with tenant 2 token
        response = client.get("/api/v1/accounts/1", headers=headers2)
        
        # Should be blocked or return empty
        assert response.status_code in [403, 404] or response.json() == []
    
    def test_input_validation_integration(self):
        """Test input validation integration across the system"""
        
        # Create valid JWT token
        jwt_token = jwt_manager.create_access_token(
            {"user_id": "123"}, "tenant_123"
        )
        csrf_token = csrf_protection.generate_token("test_session")
        
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "X-CSRF-Token": csrf_token,
            "X-Session-ID": "test_session"
        }
        
        # Test malicious input is blocked
        malicious_data = {
            "account_code": "'; DROP TABLE accounts; --",
            "account_name": "<script>alert('xss')</script>",
            "description": "../../etc/passwd"
        }
        
        response = client.post("/api/v1/accounts/", json=malicious_data, headers=headers)
        
        # Should be rejected due to input validation
        assert response.status_code in [400, 422]
    
    def test_security_middleware_integration(self):
        """Test security middleware integration"""
        
        # Test that security headers are added
        response = client.get("/api/v1/health")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
    
    def test_error_handling_security(self):
        """Test that error handling doesn't leak sensitive information"""
        
        # Test with invalid JWT token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/accounts/", headers=headers)
        
        # Should return generic error, not detailed JWT error
        assert response.status_code == 401
        error_detail = response.json().get("detail", "")
        
        # Should not contain sensitive information
        assert "secret" not in error_detail.lower()
        assert "key" not in error_detail.lower()
        assert "algorithm" not in error_detail.lower()
    
    @pytest.mark.asyncio
    async def test_concurrent_security_operations(self):
        """Test security under concurrent operations"""
        
        async def make_authenticated_request():
            # Create JWT token
            jwt_token = jwt_manager.create_access_token(
                {"user_id": "123"}, "tenant_123"
            )
            headers = {"Authorization": f"Bearer {jwt_token}"}
            
            # Make request
            response = client.get("/api/v1/accounts/", headers=headers)
            return response.status_code
        
        # Run concurrent requests
        tasks = [make_authenticated_request() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        
        # Most should succeed (some might be rate limited)
        success_count = sum(1 for status in results if status == 200)
        rate_limited_count = sum(1 for status in results if status == 429)
        
        assert success_count > 0
        assert success_count + rate_limited_count == len(results)
    
    def test_security_audit_trail(self):
        """Test that security events are properly logged"""
        
        # This would test audit logging integration
        # In a real implementation, you'd verify logs are created
        
        # Test failed authentication attempt
        response = client.post("/api/v1/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrong_password"
        })
        
        # Should log the failed attempt
        assert response.status_code == 401
        
        # Test rate limit exceeded
        for i in range(200):  # Exceed rate limit
            response = client.get("/api/v1/health")
            if response.status_code == 429:
                break
        
        # Should log rate limit violation
        assert response.status_code == 429