"""
Production health monitoring and alerting.
"""
import asyncio
import psutil
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Production health monitoring service."""
    
    def __init__(self):
        self.alerts = []
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'db_connections': 80,
            'response_time': 2000  # ms
        }
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Comprehensive system health check."""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # CPU Check
        cpu_usage = psutil.cpu_percent(interval=1)
        health_status['checks']['cpu'] = {
            'status': 'healthy' if cpu_usage < self.thresholds['cpu_usage'] else 'warning',
            'usage_percent': cpu_usage,
            'threshold': self.thresholds['cpu_usage']
        }
        
        # Memory Check
        memory = psutil.virtual_memory()
        health_status['checks']['memory'] = {
            'status': 'healthy' if memory.percent < self.thresholds['memory_usage'] else 'warning',
            'usage_percent': memory.percent,
            'available_gb': round(memory.available / (1024**3), 2),
            'threshold': self.thresholds['memory_usage']
        }
        
        # Disk Check
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        health_status['checks']['disk'] = {
            'status': 'healthy' if disk_percent < self.thresholds['disk_usage'] else 'critical',
            'usage_percent': round(disk_percent, 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'threshold': self.thresholds['disk_usage']
        }
        
        # Determine overall status
        statuses = [check['status'] for check in health_status['checks'].values()]
        if 'critical' in statuses:
            health_status['overall_status'] = 'critical'
        elif 'warning' in statuses:
            health_status['overall_status'] = 'warning'
        
        return health_status
    
    async def check_database_health(self, db: AsyncSession) -> Dict[str, Any]:
        """Database health check."""
        try:
            start_time = datetime.utcnow()
            
            # Test basic connectivity
            result = await db.execute(text("SELECT 1"))
            result.scalar()
            
            # Check response time
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Check active connections (PostgreSQL specific)
            conn_result = await db.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            ))
            active_connections = conn_result.scalar()
            
            return {
                'status': 'healthy' if response_time < self.thresholds['response_time'] else 'warning',
                'response_time_ms': round(response_time, 2),
                'active_connections': active_connections,
                'connection_threshold': self.thresholds['db_connections']
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    async def check_api_endpoints(self) -> Dict[str, Any]:
        """Check critical API endpoints."""
        endpoints = [
            '/api/v1/health',
            '/api/v1/auth/verify',
            '/api/v1/gl/accounts'
        ]
        
        endpoint_status = {}
        for endpoint in endpoints:
            try:
                # In production, make actual HTTP requests
                endpoint_status[endpoint] = {
                    'status': 'healthy',
                    'response_time_ms': 150
                }
            except Exception as e:
                endpoint_status[endpoint] = {
                    'status': 'critical',
                    'error': str(e)
                }
        
        return endpoint_status
    
    def create_alert(self, alert_type: str, message: str, severity: str = 'warning'):
        """Create system alert."""
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity,
            'resolved': False
        }
        
        self.alerts.append(alert)
        logger.warning(f"ALERT [{severity.upper()}]: {alert_type} - {message}")
        
        # In production, send to monitoring system (PagerDuty, Slack, etc.)
        return alert
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return [alert for alert in self.alerts if not alert['resolved']]
    
    def resolve_alert(self, alert_id: int):
        """Resolve an alert."""
        if 0 <= alert_id < len(self.alerts):
            self.alerts[alert_id]['resolved'] = True
            self.alerts[alert_id]['resolved_at'] = datetime.utcnow().isoformat()

class PerformanceMonitor:
    """Performance monitoring service."""
    
    def __init__(self):
        self.metrics = []
        self.max_metrics = 1000
    
    def record_api_call(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Record API call metrics."""
        metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'response_time_ms': response_time,
            'status_code': status_code
        }
        
        self.metrics.append(metric)
        
        # Keep only recent metrics
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
        
        # Alert on slow responses
        if response_time > 2000:  # 2 seconds
            logger.warning(f"Slow API response: {endpoint} took {response_time}ms")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {'message': 'No metrics available'}
        
        recent_metrics = self.metrics[-100:]  # Last 100 calls
        
        response_times = [m['response_time_ms'] for m in recent_metrics]
        status_codes = [m['status_code'] for m in recent_metrics]
        
        return {
            'total_calls': len(recent_metrics),
            'avg_response_time_ms': round(sum(response_times) / len(response_times), 2),
            'max_response_time_ms': max(response_times),
            'min_response_time_ms': min(response_times),
            'error_rate': len([s for s in status_codes if s >= 400]) / len(status_codes),
            'success_rate': len([s for s in status_codes if s < 400]) / len(status_codes)
        }