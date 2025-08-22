"""
Redis utility functions for caching and report generation.
"""
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, cast
from datetime import datetime, timedelta
import functools
import pickle
import hashlib
import aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Type variable for generic function return type
T = TypeVar('T')

class RedisManager:
    """Manager for Redis connections and caching operations."""
    _instance = None
    _redis = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    async def initialize(self):
        """Initialize the Redis connection pool."""
        if not self._initialized:
            try:
                self._redis = await aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                self._initialized = True
                logger.info("Redis connection pool initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Redis: {e}")
                raise
    
    @property
    async def redis(self) -> aioredis.Redis:
        """Get a Redis client from the pool."""
        if not self._initialized:
            await self.initialize()
        return self._redis
    
    async def close(self):
        """Close the Redis connection pool."""
        if self._redis:
            await self._redis.close()
            await self._redis.connection_pool.disconnect()
            self._initialized = False
            logger.info("Redis connection pool closed")

# Global Redis manager instance
redis_manager = RedisManager()

# Decorator for caching function results
async def cache(
    key_prefix: str = "",
    ttl: int = settings.REDIS_CACHE_TTL,
    serialize: Callable[[Any], str] = json.dumps,
    deserialize: Callable[[str], Any] = json.loads,
    key_builder: Optional[Callable[..., str]] = None
):
    """
    Cache decorator for async functions.
    
    Args:
        key_prefix: Prefix for cache keys
        ttl: Time to live in seconds for cached items
        serialize: Function to serialize values for storage
        deserialize: Function to deserialize values from storage
        key_builder: Optional function to build custom cache keys
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if Redis is not available
            if not settings.REDIS_URL:
                return await func(*args, **kwargs)
                
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key builder
                key_parts = [key_prefix, func.__module__, func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(str(part) for part in key_parts).encode()).hexdigest()
            
            # Try to get from cache
            try:
                redis = await redis_manager.redis()
                cached = await redis.get(f"cache:{cache_key}")
                if cached is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return deserialize(cached)
            except Exception as e:
                logger.warning(f"Cache get error: {e}")
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            try:
                redis = await redis_manager.redis()
                await redis.set(
                    f"cache:{cache_key}",
                    serialize(result),
                    ex=ttl
                )
                logger.debug(f"Cached result for key: {cache_key}")
            except Exception as e:
                logger.warning(f"Cache set error: {e}")
            
            return result
        
        return wrapper
    return decorator

# Report generation utilities
class ReportManager:
    """Manager for report generation and caching."""
    
    @staticmethod
    async def generate_report_id(company_id: str, report_type: str, params: Dict[str, Any]) -> str:
        """Generate a unique report ID based on parameters."""
        key_parts = [
            "report",
            company_id,
            report_type,
            json.dumps(params, sort_keys=True),
            datetime.utcnow().strftime("%Y%m%d%H%M%S")
        ]
        return hashlib.sha256(":".join(str(part) for part in key_parts).encode()).hexdigest()
    
    @staticmethod
    async def store_report_status(report_id: str, status: str, result: Any = None, error: str = None):
        """Store report generation status in Redis."""
        if not settings.REDIS_URL:
            return
            
        try:
            redis = await redis_manager.redis()
            status_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
                "result": result,
                "error": error
            }
            await redis.set(
                f"report:status:{report_id}",
                json.dumps(status_data),
                ex=settings.REPORT_CACHE_TTL
            )
        except Exception as e:
            logger.error(f"Failed to store report status: {e}")
    
    @staticmethod
    async def get_report_status(report_id: str) -> Dict[str, Any]:
        """Get report generation status from Redis."""
        if not settings.REDIS_URL:
            return {"status": "not_found", "error": "Redis not configured"}
            
        try:
            redis = await redis_manager.redis()
            status_data = await redis.get(f"report:status:{report_id}")
            if status_data:
                return json.loads(status_data)
            return {"status": "not_found"}
        except Exception as e:
            logger.error(f"Failed to get report status: {e}")
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    async def store_report_chunk(report_id: str, chunk_id: int, data: Any):
        """Store a chunk of report data in Redis."""
        if not settings.REDIS_URL:
            return
            
        try:
            redis = await redis_manager.redis()
            await redis.rpush(
                f"report:data:{report_id}",
                json.dumps({"chunk_id": chunk_id, "data": data})
            )
            # Set expiration on the list
            await redis.expire(f"report:data:{report_id}", settings.REPORT_CACHE_TTL)
        except Exception as e:
            logger.error(f"Failed to store report chunk: {e}")
    
    @staticmethod
    async def get_report_chunks(report_id: str) -> List[Dict[str, Any]]:
        """Get all chunks of report data from Redis."""
        if not settings.REDIS_URL:
            return []
            
        try:
            redis = await redis_manager.redis()
            chunks = await redis.lrange(f"report:data:{report_id}", 0, -1)
            return [json.loads(chunk) for chunk in chunks]
        except Exception as e:
            logger.error(f"Failed to get report chunks: {e}")
            return []

# Initialize Redis manager on module import
async def init_redis():
    """Initialize Redis connection."""
    if settings.REDIS_URL:
        await redis_manager.initialize()

# Close Redis connections on shutdown
async def close_redis():
    """Close Redis connection."""
    if redis_manager._initialized:
        await redis_manager.close()
