from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class APIPerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for API performance monitoring and optimization"""
    
    def __init__(self, app, max_response_time: float = 0.2):
        super().__init__(app)
        self.max_response_time = max_response_time
        self.slow_endpoints = []
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log slow endpoints
        if process_time > self.max_response_time:
            self.slow_endpoints.append({
                "endpoint": str(request.url),
                "method": request.method,
                "response_time": process_time,
                "timestamp": time.time()
            })
            logger.warning(f"Slow endpoint: {request.method} {request.url} - {process_time:.3f}s")
        
        return response

class APIOptimizer:
    """API response time optimization service"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_cached_response(self, cache_key: str):
        """Get cached response if available and not expired"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                del self.cache[cache_key]
        return None
    
    def cache_response(self, cache_key: str, data):
        """Cache response data"""
        self.cache[cache_key] = (data, time.time())
    
    def optimize_pagination(self, query_params: dict) -> dict:
        """Optimize pagination parameters"""
        limit = min(int(query_params.get('limit', 50)), 1000)  # Max 1000 items
        offset = max(int(query_params.get('offset', 0)), 0)
        
        return {
            "limit": limit,
            "offset": offset,
            "optimized": True
        }
    
    def get_performance_metrics(self) -> Dict:
        """Get API performance metrics"""
        return {
            "cache_size": len(self.cache),
            "cache_hit_ratio": 0.85,  # Mock metric
            "average_response_time": 0.15,  # Mock metric
            "optimization_status": "active"
        }