from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.db.tenant_middleware import get_current_tenant
from app.core.cache.tenant_cache import tenant_cache
from datetime import datetime

class TenantUsageTracker:
    def __init__(self):
        self.usage_limits = {
            'api_calls_per_hour': 1000,
            'storage_mb': 1000,
            'users': 50
        }
    
    async def track_api_call(self, endpoint: str):
        tenant_id = get_current_tenant()
        key = f"api_calls:{endpoint}:{datetime.now().hour}"
        
        current_count = await tenant_cache.get(key) or 0
        await tenant_cache.set(key, current_count + 1, expire=3600)
        
        if current_count >= self.usage_limits['api_calls_per_hour']:
            raise Exception("API rate limit exceeded")
    
    async def get_usage_stats(self, db: AsyncSession):
        tenant_id = get_current_tenant()
        
        api_usage = await tenant_cache.get(f"api_calls:total:{datetime.now().hour}") or 0
        
        result = await db.execute(text("SELECT COUNT(*) FROM users WHERE tenant_id = :tenant_id"), 
                                {"tenant_id": tenant_id})
        user_count = result.scalar() or 0
        
        return {
            'tenant_id': tenant_id,
            'api_calls_hour': api_usage,
            'users': user_count,
            'limits': self.usage_limits
        }

usage_tracker = TenantUsageTracker()