"""Redis caching configuration and utilities"""

from typing import Optional, Any, Callable
from functools import wraps
import json
import redis
from app.core.config import settings

# Redis client instance
redis_client: Optional[redis.Redis] = None


class CacheManager:
    """Cache manager for Redis operations"""

    def __init__(self):
        self.client = None

    def init(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.Redis(
                host=getattr(settings, "REDIS_HOST", "localhost"),
                port=getattr(settings, "REDIS_PORT", 6379),
                db=getattr(settings, "REDIS_DB", 0),
                password=getattr(settings, "REDIS_PASSWORD", None),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            self.client.ping()
            return self.client
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.client = None
            return None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache"""
        if not self.client:
            return
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass

    def delete(self, key: str):
        """Delete key from cache"""
        if not self.client:
            return
        try:
            self.client.delete(key)
        except Exception:
            pass

    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        if not self.client:
            return
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception:
            pass


# Global cache manager instance
cache_manager = CacheManager()


def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=getattr(settings, "REDIS_DB", 0),
            password=getattr(settings, "REDIS_PASSWORD", None),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        redis_client.ping()
        cache_manager.client = redis_client
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
