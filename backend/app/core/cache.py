"""
Caching strategy implementation.
"""
import json
from typing import Any, Optional, Dict
from datetime import timedelta

from app.core.config import settings
from app.core.logging import logger

# Mock redis module
class MockRedis:
    def __init__(self, **kwargs):
        self._data = {}
    
    def get(self, key):
        return self._data.get(key)
    
    def setex(self, key, ttl, value):
        self._data[key] = value
        return True
    
    def delete(self, *keys):
        count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                count += 1
        return count
    
    def keys(self, pattern):
        return [k for k in self._data.keys() if pattern.replace('*', '') in k]

class redis:
    @staticmethod
    def Redis(**kwargs):
        return MockRedis(**kwargs)

class CacheManager:
    """Redis-based cache manager with tenant isolation."""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=getattr(settings, 'REDIS_HOST', 'localhost'),
            port=getattr(settings, 'REDIS_PORT', 6379),
            db=getattr(settings, 'REDIS_DB', 0),
            decode_responses=True
        )
    
    def _get_key(self, key: str, tenant_id: Optional[str] = None) -> str:
        """Generate tenant-aware cache key."""
        if tenant_id:
            return f"tenant:{tenant_id}:{key}"
        return f"global:{key}"
    
    async def get(self, key: str, tenant_id: Optional[str] = None) -> Optional[Any]:
        """Get value from cache."""
        try:
            cache_key = self._get_key(key, tenant_id)
            value = self.redis_client.get(cache_key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 3600,
        tenant_id: Optional[str] = None
    ) -> bool:
        """Set value in cache."""
        try:
            cache_key = self._get_key(key, tenant_id)
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(cache_key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    async def delete(self, key: str, tenant_id: Optional[str] = None) -> bool:
        """Delete value from cache."""
        try:
            cache_key = self._get_key(key, tenant_id)
            return bool(self.redis_client.delete(cache_key))
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    async def clear_tenant_cache(self, tenant_id: str) -> int:
        """Clear all cache entries for a tenant."""
        try:
            pattern = f"tenant:{tenant_id}:*"
            keys = self.redis_client.keys(pattern)
            return self.redis_client.delete(*keys) if keys else 0
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return 0

cache_manager = CacheManager()

def cache_result(key: str, ttl: int = 3600):
    """Decorator for caching function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            tenant_id = kwargs.get('tenant_id')
            cache_key = f"{func.__name__}:{key}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key, tenant_id)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl, tenant_id)
            return result
        return wrapper
    return decorator