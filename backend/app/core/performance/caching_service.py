import redis
import json
import hashlib
from typing import Any, Optional
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class CachingService:
    """Redis-based caching service for performance optimization"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            self.available = True
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self.available = False
            self.local_cache = {}
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.available:
            return self.local_cache.get(key)
        
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set cached value with TTL"""
        if not self.available:
            self.local_cache[key] = value
            return
        
        try:
            serialized_value = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete cached value"""
        if not self.available:
            self.local_cache.pop(key, None)
            return
        
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def cache_financial_summary(self, company_id: int, data: dict):
        """Cache financial summary data"""
        cache_key = self._generate_cache_key("financial_summary", company_id=company_id)
        await self.set(cache_key, data, ttl=600)  # 10 minutes
    
    async def get_financial_summary(self, company_id: int) -> Optional[dict]:
        """Get cached financial summary"""
        cache_key = self._generate_cache_key("financial_summary", company_id=company_id)
        return await self.get(cache_key)
    
    async def cache_dashboard_data(self, company_id: int, period_start: str, period_end: str, data: dict):
        """Cache dashboard data"""
        cache_key = self._generate_cache_key(
            "dashboard", 
            company_id=company_id, 
            period_start=period_start, 
            period_end=period_end
        )
        await self.set(cache_key, data, ttl=900)  # 15 minutes
    
    async def get_dashboard_data(self, company_id: int, period_start: str, period_end: str) -> Optional[dict]:
        """Get cached dashboard data"""
        cache_key = self._generate_cache_key(
            "dashboard", 
            company_id=company_id, 
            period_start=period_start, 
            period_end=period_end
        )
        return await self.get(cache_key)
    
    async def invalidate_company_cache(self, company_id: int):
        """Invalidate all cache entries for a company"""
        if not self.available:
            # Clear local cache entries for company
            keys_to_delete = [k for k in self.local_cache.keys() if f"company_{company_id}" in k]
            for key in keys_to_delete:
                del self.local_cache[key]
            return
        
        try:
            # Get all keys matching company pattern
            pattern = f"*company_id*{company_id}*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if not self.available:
            return {
                "status": "local_cache",
                "entries": len(self.local_cache),
                "type": "in_memory"
            }
        
        try:
            info = self.redis_client.info()
            return {
                "status": "redis_connected",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "type": "redis"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}