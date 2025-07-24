import pytest
from unittest.mock import patch, AsyncMock
from app.core.security.tenant_isolation import CrossTenantAccessPrevention
from app.core.security.tenant_encryption import tenant_encryption

class TestTenantIsolation:
    def test_cross_tenant_access_prevention(self):
        CrossTenantAccessPrevention.log_blocked_attempt("tenant1", "tenant2", "asset")
        assert "tenant1:tenant2" in CrossTenantAccessPrevention.blocked_attempts

    def test_suspicious_access_pattern_detection(self):
        for i in range(15):
            CrossTenantAccessPrevention.log_blocked_attempt("tenant1", f"tenant{i}", "resource")
        
        is_suspicious = CrossTenantAccessPrevention.check_access_pattern("tenant1")
        assert is_suspicious is True

class TestTenantEncryption:
    def test_data_encryption_decryption(self):
        with patch('app.core.db.tenant_middleware.get_current_tenant') as mock_tenant:
            mock_tenant.return_value = 'test_tenant'
            
            original_data = "sensitive information"
            encrypted_data = tenant_encryption.encrypt_data(original_data)
            decrypted_data = tenant_encryption.decrypt_data(encrypted_data)
            
            assert encrypted_data != original_data
            assert decrypted_data == original_data

class TestSessionSecurity:
    async def test_session_isolation(self):
        from app.core.security.tenant_session import tenant_session_manager
        
        session_id = await tenant_session_manager.create_session(
            user_id="user1",
            ip_address="192.168.1.1",
            user_agent="test-agent",
            tenant_id="test_tenant"
        )
        
        assert session_id is not None