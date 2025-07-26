"""Rate limiting implementation"""
import redis
import time
from fastapi import Request, HTTPException
from typing import Optional

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is within rate limit"""
        current_time = int(time.time())
        window_start = current_time - window
        
        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_requests = self.redis.zcard(key)
        
        if current_requests >= limit:
            return False
        
        # Add current request
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, window)
        
        return True
    
    def get_remaining(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests in current window"""
        current_time = int(time.time())
        window_start = current_time - window
        
        self.redis.zremrangebyscore(key, 0, window_start)
        current_requests = self.redis.zcard(key)
        
        return max(0, limit - current_requests)

rate_limiter = RateLimiter(redis.Redis(host='localhost', port=6379, db=1))

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host
    user_id = getattr(request.state, 'user_id', None)
    
    # Different limits for different endpoints
    if request.url.path.startswith('/api/auth'):
        limit, window = 5, 60  # 5 requests per minute for auth
        key = f"rate_limit:auth:{client_ip}"
    elif user_id:
        limit, window = 1000, 3600  # 1000 requests per hour for authenticated users
        key = f"rate_limit:user:{user_id}"
    else:
        limit, window = 100, 3600  # 100 requests per hour for anonymous
        key = f"rate_limit:ip:{client_ip}"
    
    if not rate_limiter.is_allowed(key, limit, window):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(window)}
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    remaining = rate_limiter.get_remaining(key, limit, window)
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
    
    return response