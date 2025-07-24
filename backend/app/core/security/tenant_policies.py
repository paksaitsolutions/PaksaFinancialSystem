from enum import Enum
from typing import Dict, List, Any
from app.core.db.tenant_middleware import get_current_tenant
from app.core.cache.tenant_cache import tenant_cache
import json

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TenantSecurityPolicy:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.policies = {
            'password_policy': {
                'min_length': 8,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_symbols': True,
                'max_age_days': 90
            },
            'session_policy': {
                'timeout_minutes': 60,
                'max_concurrent_sessions': 5,
                'require_mfa': False
            },
            'data_policy': {
                'encryption_required': True,
                'backup_retention_days': 365,
                'audit_retention_days': 2555  # 7 years
            },
            'access_policy': {
                'max_login_attempts': 5,
                'lockout_duration_minutes': 30,
                'ip_whitelist': [],
                'allowed_countries': []
            }
        }
    
    async def get_policy(self, policy_type: str) -> Dict[str, Any]:
        """Get specific security policy for tenant"""
        # Try to get from cache first
        cache_key = f"security_policy:{policy_type}"
        cached_policy = await tenant_cache.get(cache_key)
        
        if cached_policy:
            return json.loads(cached_policy)
        
        policy = self.policies.get(policy_type, {})
        await tenant_cache.set(cache_key, json.dumps(policy), expire=3600)
        
        return policy
    
    async def update_policy(self, policy_type: str, policy_data: Dict[str, Any]):
        """Update security policy for tenant"""
        self.policies[policy_type] = policy_data
        
        # Update cache
        cache_key = f"security_policy:{policy_type}"
        await tenant_cache.set(cache_key, json.dumps(policy_data), expire=3600)
    
    async def validate_password(self, password: str) -> List[str]:
        """Validate password against tenant policy"""
        policy = await self.get_policy('password_policy')
        errors = []
        
        if len(password) < policy['min_length']:
            errors.append(f"Password must be at least {policy['min_length']} characters")
        
        if policy['require_uppercase'] and not any(c.isupper() for c in password):
            errors.append("Password must contain uppercase letters")
        
        if policy['require_lowercase'] and not any(c.islower() for c in password):
            errors.append("Password must contain lowercase letters")
        
        if policy['require_numbers'] and not any(c.isdigit() for c in password):
            errors.append("Password must contain numbers")
        
        if policy['require_symbols'] and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain symbols")
        
        return errors
    
    async def check_ip_access(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        policy = await self.get_policy('access_policy')
        whitelist = policy.get('ip_whitelist', [])
        
        if not whitelist:
            return True  # No restrictions
        
        return ip_address in whitelist

class TenantSecurityManager:
    def __init__(self):
        self.tenant_policies = {}
    
    def get_tenant_policy(self, tenant_id: str = None) -> TenantSecurityPolicy:
        """Get security policy for tenant"""
        if not tenant_id:
            tenant_id = get_current_tenant()
        
        if tenant_id not in self.tenant_policies:
            self.tenant_policies[tenant_id] = TenantSecurityPolicy(tenant_id)
        
        return self.tenant_policies[tenant_id]
    
    async def enforce_security_level(self, level: SecurityLevel):
        """Enforce security level for current tenant"""
        tenant_policy = self.get_tenant_policy()
        
        if level == SecurityLevel.HIGH:
            await tenant_policy.update_policy('session_policy', {
                'timeout_minutes': 30,
                'max_concurrent_sessions': 3,
                'require_mfa': True
            })
        elif level == SecurityLevel.CRITICAL:
            await tenant_policy.update_policy('session_policy', {
                'timeout_minutes': 15,
                'max_concurrent_sessions': 1,
                'require_mfa': True
            })

# Global security manager
tenant_security_manager = TenantSecurityManager()