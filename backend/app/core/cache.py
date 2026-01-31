"""Redis caching configuration and utilities"""
from typing import Optional, Any, Callable
from functools import wraps
import json
import redis
from app.core.config import settings

# Redis client instance
redis_client: Optional[redis.Redis] = None

def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        redis_client.ping()
        return redis_client
    except Exception as e:
        print(f"Redis connection failed: {e}")
        redis_client = None
        return None

def get_redis() -> Optional[redis.Redis]:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        init_redis()
    return redis_client

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)

def cached(prefix: str, ttl: int = 300):
    """Decorator for caching function results
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client = get_redis()
            if client is None:
                return await func(*args, **kwargs)
            
            # Generate cache key
            key = f"{prefix}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            try:
                cached_value = client.get(key)
                if cached_value:
                    return json.loads(cached_value)
            except Exception:
                pass
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                client.setex(key, ttl, json.dumps(result))
            except Exception:
                pass
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern"""
    client = get_redis()
    if client:
        try:
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
        except Exception:
            pass

# Common cache patterns
CACHE_PATTERNS = {
    "chart_of_accounts": "coa:*",
    "vendors": "vendors:*",
    "customers": "customers:*",
    "tax_codes": "tax_codes:*",
    "exchange_rates": "exchange_rates:*",
    "user_permissions": "permissions:*",
}
