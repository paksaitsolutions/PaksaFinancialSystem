"""
Caching strategy implementation.
"""
import json
import redis
from typing import Any, Optional, Dict
from datetime import timedelta

from app.core.config import settings
from app.core.logging import logger

class CacheManager:
    """Redis-based cache manager with tenant isolation."""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
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