from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from app.core.config import settings

# Create rate limiter with Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=["1000/hour", "100/minute"]
)

# Enhanced rate limiter with tenant awareness
class TenantAwareRateLimiter:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.limits = {
            "login": {"requests": 5, "window": 300},  # 5 requests per 5 minutes
            "api": {"requests": 100, "window": 60},   # 100 requests per minute
            "upload": {"requests": 10, "window": 3600} # 10 uploads per hour
        }
    
    def check_rate_limit(self, key: str, limit_type: str = "api") -> bool:
        """Check if request is within rate limits"""
        limit_config = self.limits.get(limit_type, self.limits["api"])
        
        current_count = self.redis_client.get(key)
        if current_count is None:
            # First request
            self.redis_client.setex(key, limit_config["window"], 1)
            return True
        
        current_count = int(current_count)
        if current_count >= limit_config["requests"]:
            return False
        
        # Increment counter
        self.redis_client.incr(key)
        return True
    
    def get_tenant_key(self, request: Request, tenant_id: str, limit_type: str) -> str:
        """Generate tenant-specific rate limit key"""
        ip = get_remote_address(request)
        return f"rate_limit:{tenant_id}:{ip}:{limit_type}"

tenant_rate_limiter = TenantAwareRateLimiter()

def rate_limit_check(limit_type: str = "api"):
    """Decorator for rate limiting endpoints"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            from app.core.db.tenant_middleware import get_current_tenant
            
            try:
                tenant_id = get_current_tenant()
                key = tenant_rate_limiter.get_tenant_key(request, tenant_id, limit_type)
                
                if not tenant_rate_limiter.check_rate_limit(key, limit_type):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded for {limit_type}"
                    )
                
                return await func(request, *args, **kwargs)
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise
                # If tenant context fails, use IP-based limiting
                ip = get_remote_address(request)
                key = f"rate_limit:unknown:{ip}:{limit_type}"
                if not tenant_rate_limiter.check_rate_limit(key, limit_type):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded"
                    )
                return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator