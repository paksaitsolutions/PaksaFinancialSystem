"""
Application monitoring and metrics.
"""
import time
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque

from app.core.logging import logger

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class MetricsCollector:
    """Collect application metrics."""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(deque)
        self.error_counts = defaultdict(int)
        self.active_sessions = set()
        self.tenant_usage = defaultdict(lambda: {"requests": 0, "errors": 0})
        
    def record_request(self, method: str, path: str, tenant_id: str = None):
        """Record HTTP request."""
        self.request_counts[f"{method} {path}"] += 1
        if tenant_id:
            self.tenant_usage[tenant_id]["requests"] += 1
    
    def record_response_time(self, method: str, path: str, duration: float):
        """Record response time."""
        key = f"{method} {path}"
        self.response_times[key].append(duration)
        # Keep only last 1000 measurements
        if len(self.response_times[key]) > 1000:
            self.response_times[key].popleft()
    
    def record_error(self, error_type: str, tenant_id: str = None):
        """Record application error."""
        self.error_counts[error_type] += 1
        if tenant_id:
            self.tenant_usage[tenant_id]["errors"] += 1
    
    def add_active_session(self, session_id: str):
        """Add active session."""
        self.active_sessions.add(session_id)
    
    def remove_active_session(self, session_id: str):
        """Remove active session."""
        self.active_sessions.discard(session_id)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        # System metrics (only if psutil is available)
        system_metrics = {}
        if PSUTIL_AVAILABLE:
            try:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                system_metrics = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used_gb": memory.used / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_used_gb": disk.used / (1024**3)
                }
            except Exception:
                system_metrics = {"error": "Unable to collect system metrics"}
        else:
            system_metrics = {"error": "psutil not available"}
        
        # Application metrics
        avg_response_times = {}
        for endpoint, times in self.response_times.items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_metrics,
            "application": {
                "active_sessions": len(self.active_sessions),
                "total_requests": sum(self.request_counts.values()),
                "total_errors": sum(self.error_counts.values()),
                "avg_response_times": avg_response_times,
                "error_breakdown": dict(self.error_counts),
                "tenant_usage": dict(self.tenant_usage)
            }
        }

# Global metrics collector
metrics = MetricsCollector()

class PerformanceMonitor:
    """Monitor application performance."""
    
    def __init__(self):
        self.slow_queries = deque(maxlen=100)
        self.memory_usage = deque(maxlen=1000)
        self.cpu_usage = deque(maxlen=1000)
    
    def record_slow_query(self, query: str, duration: float, tenant_id: str = None):
        """Record slow database query."""
        self.slow_queries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "query": query[:500],  # Truncate long queries
            "duration": duration,
            "tenant_id": tenant_id
        })
        
        logger.warning(
            f"Slow query detected: {duration:.2f}s",
            extra={
                "query": query[:200],
                "duration": duration,
                "tenant_id": tenant_id
            }
        )
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check system health status."""
        if not PSUTIL_AVAILABLE:
            return {
                "status": "unknown",
                "alerts": ["System monitoring unavailable - psutil not installed"],
                "metrics": {},
                "trends": {}
            }
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Record for trending
            self.cpu_usage.append(cpu_percent)
            self.memory_usage.append(memory.percent)
            
            health_status = "healthy"
            alerts = []
            
            # Check thresholds
            if cpu_percent > 80:
                health_status = "warning"
                alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > 85:
                health_status = "critical" if memory.percent > 95 else "warning"
                alerts.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > 90:
                health_status = "critical"
                alerts.append(f"Low disk space: {disk.percent:.1f}% used")
            
            return {
                "status": health_status,
                "alerts": alerts,
                "metrics": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent
                },
                "trends": {
                    "avg_cpu_5min": sum(list(self.cpu_usage)[-300:]) / min(len(self.cpu_usage), 300),
                    "avg_memory_5min": sum(list(self.memory_usage)[-300:]) / min(len(self.memory_usage), 300)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "alerts": [f"Error checking system health: {str(e)}"],
                "metrics": {},
                "trends": {}
            }

# Global performance monitor
performance_monitor = PerformanceMonitor()

def track_request_time(func):
    """Decorator to track request execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            metrics.record_response_time(func.__name__, "", duration)
            return result
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_error(type(e).__name__)
            raise
    return wrapper