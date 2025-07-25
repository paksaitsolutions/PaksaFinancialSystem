import pytest
from app.core.security.input_validation import AccountCodeValidator, EmailValidator, TenantIdValidator
from app.core.security.csrf_protection import CSRFProtection
from app.core.security.jwt_enhanced import EnhancedJWTManager
from app.core.security.rate_limiter import TenantAwareRateLimiter
import secrets
import time

class TestSecurityReview:
    """Security specialist review tests"""
    
    def test_input_validation_security(self):
        """Test input validation security measures"""
        
        # Test account code validation
        with pytest.raises(ValueError):
            AccountCodeValidator.validate("'; DROP TABLE accounts; --")
        
        with pytest.raises(ValueError):
            AccountCodeValidator.validate("<script>alert('xss')</script>")
        
        # Valid input should pass
        valid_code = AccountCodeValidator.validate("ACC-001")
        assert valid_code == "ACC-001"
        
        # Test email validation
        with pytest.raises(ValueError):
            EmailValidator.validate("admin'; DROP TABLE users; --")
        
        valid_email = EmailValidator.validate("user@example.com")
        assert valid_email == "user@example.com"
        
        # Test tenant ID validation
        with pytest.raises(ValueError):
            TenantIdValidator.validate("../../../etc/passwd")
        
        valid_tenant = TenantIdValidator.validate("tenant_123")
        assert valid_tenant == "tenant_123"
    
    def test_csrf_token_security(self):
        """Test CSRF token security implementation"""
        csrf = CSRFProtection("test-secret-key")
        session_id = "test_session_123"
        
        # Generate token
        token = csrf.generate_token(session_id)
        assert token is not None
        assert ":" in token  # Should have timestamp:signature format
        
        # Valid token should validate
        assert csrf.validate_token(token, session_id) is True
        
        # Invalid session should fail
        assert csrf.validate_token(token, "different_session") is False
        
        # Malformed token should fail
        assert csrf.validate_token("malformed_token", session_id) is False
        
        # Empty token should fail
        assert csrf.validate_token("", session_id) is False
    
    def test_jwt_security_enhancements(self):
        """Test JWT security enhancements"""
        jwt_manager = EnhancedJWTManager()
        
        # Test token creation
        user_data = {"user_id": "123", "email": "test@example.com"}
        token = jwt_manager.create_access_token(user_data, "tenant_123")
        
        assert token is not None
        assert isinstance(token, str)
        
        # Test token verification
        payload = jwt_manager.verify_token(token)
        assert payload["user_id"] == "123"
        assert payload["tenant_id"] == "tenant_123"
        assert "jti" in payload  # JWT ID should be present
        
        # Test token revocation
        jwt_manager.revoke_token(token)
        
        # Revoked token should fail verification
        with pytest.raises(Exception):  # Should raise HTTPException
            jwt_manager.verify_token(token)
    
    def test_rate_limiting_security(self):
        """Test rate limiting security implementation"""
        rate_limiter = TenantAwareRateLimiter()
        
        # Test rate limit checking
        key = "test_tenant:127.0.0.1:api"
        
        # First requests should pass
        for i in range(5):
            assert rate_limiter.check_rate_limit(key, "api") is True
        
        # Simulate hitting the limit
        for i in range(100):
            rate_limiter.check_rate_limit(key, "api")
        
        # Should be rate limited now
        assert rate_limiter.check_rate_limit(key, "api") is False
    
    def test_cryptographic_security(self):
        """Test cryptographic implementations"""
        
        # Test secure random generation
        token1 = secrets.token_urlsafe(32)
        token2 = secrets.token_urlsafe(32)
        
        # Tokens should be different
        assert token1 != token2
        assert len(token1) >= 32
        assert len(token2) >= 32
        
        # Test HMAC implementation in CSRF
        csrf = CSRFProtection("test-secret-key")
        session_id = "test_session"
        
        token1 = csrf.generate_token(session_id)
        time.sleep(0.001)  # Small delay
        token2 = csrf.generate_token(session_id)
        
        # Tokens should be different due to timestamp
        assert token1 != token2
        
        # Both should validate for same session
        assert csrf.validate_token(token1, session_id) is True
        assert csrf.validate_token(token2, session_id) is True
    
    def test_security_headers_validation(self):
        """Test security headers implementation"""
        from app.middleware.security_middleware import SecurityMiddleware
        
        middleware = SecurityMiddleware(None)
        
        # Mock response object
        class MockResponse:
            def __init__(self):
                self.headers = {}
        
        response = MockResponse()
        middleware._add_security_headers(response)
        
        # Verify security headers are present
        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy"
        ]
        
        for header in expected_headers:
            assert header in response.headers
        
        # Verify header values
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "max-age" in response.headers["Strict-Transport-Security"]
    
    def test_tenant_isolation_security(self):
        """Test tenant isolation security measures"""
        from app.core.security.input_validation import sanitize_sql_input
        
        # Test SQL injection prevention in tenant context
        malicious_tenant_id = "tenant'; DROP TABLE accounts; --"
        sanitized = sanitize_sql_input(malicious_tenant_id)
        
        assert "DROP" not in sanitized
        assert ";" not in sanitized
        assert "--" not in sanitized
        
        # Test cross-tenant access prevention patterns
        cross_tenant_attempts = [
            "../other_tenant/data",
            "../../admin/config",
            "tenant_123/../tenant_456/secrets"
        ]
        
        for attempt in cross_tenant_attempts:
            sanitized = sanitize_sql_input(attempt)
            assert "../" not in sanitized
            assert ".." not in sanitized