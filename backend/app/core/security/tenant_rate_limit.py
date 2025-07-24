from fastapi import HTTPException, Request
from app.core.db.tenant_middleware import get_current_tenant
from app.core.cache.tenant_cache import tenant_cache
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio

class TenantRateLimiter:
    def __init__(self):
        self.default_limits = {
            'api_calls_per_minute': 100,
            'api_calls_per_hour': 1000,
            'login_attempts_per_hour': 10,
            'export_requests_per_hour': 5
        }
        
        self.tenant_limits = {}  # Custom limits per tenant
    
    async def check_rate_limit(
        self,
        action: str,
        limit_per_minute: int = None,
        limit_per_hour: int = None
    ) -> bool:
        """Check if action is within rate limits for current tenant"""
        tenant_id = get_current_tenant()
        
        # Use custom limits if available
        tenant_config = self.tenant_limits.get(tenant_id, {})
        minute_limit = limit_per_minute or tenant_config.get(f'{action}_per_minute', self.default_limits.get(f'{action}_per_minute', 100))
        hour_limit = limit_per_hour or tenant_config.get(f'{action}_per_hour', self.default_limits.get(f'{action}_per_hour', 1000))
        
        # Check minute limit
        minute_key = f"rate_limit:{action}:minute:{datetime.now().strftime('%Y%m%d%H%M')}"
        minute_count = await tenant_cache.get(minute_key) or 0
        
        if minute_count >= minute_limit:
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded: {action} per minute")
        
        # Check hour limit
        hour_key = f"rate_limit:{action}:hour:{datetime.now().strftime('%Y%m%d%H')}"
        hour_count = await tenant_cache.get(hour_key) or 0
        
        if hour_count >= hour_limit:
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded: {action} per hour")
        
        # Increment counters
        await tenant_cache.set(minute_key, minute_count + 1, expire=60)
        await tenant_cache.set(hour_key, hour_count + 1, expire=3600)
        
        return True
    
    async def set_tenant_limits(self, tenant_id: str, limits: Dict[str, int]):
        """Set custom rate limits for a tenant"""
        self.tenant_limits[tenant_id] = limits
    
    async def get_current_usage(self, action: str) -> Dict[str, int]:
        """Get current usage for an action"""
        minute_key = f"rate_limit:{action}:minute:{datetime.now().strftime('%Y%m%d%H%M')}"
        hour_key = f"rate_limit:{action}:hour:{datetime.now().strftime('%Y%m%d%H')}"
        
        minute_count = await tenant_cache.get(minute_key) or 0
        hour_count = await tenant_cache.get(hour_key) or 0
        
        return {
            'minute_usage': minute_count,
            'hour_usage': hour_count
        }

# Global rate limiter instance
tenant_rate_limiter = TenantRateLimiter()

def rate_limit(action: str, per_minute: int = None, per_hour: int = None):
    """Decorator for rate limiting endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            await tenant_rate_limiter.check_rate_limit(action, per_minute, per_hour)
            return await func(*args, **kwargs)
        return wrapper
    return decorator