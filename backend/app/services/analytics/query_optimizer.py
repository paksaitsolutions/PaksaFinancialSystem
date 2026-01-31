"""
Query Optimizer Service

This service provides query optimization and caching capabilities for analytics
to improve performance of data aggregation and reporting.
"""
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Any, Optional, Union, Callable
import asyncio
import json
import redis

from dataclasses import dataclass
from sqlalchemy import select, func, and_, or_, text, Index
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from uuid import UUID
import hashlib

from app.core.config import settings





@dataclass
class QueryMetrics:
    """Query performance metrics."""
    query_hash: str
    execution_time: float
    rows_returned: int
    cache_hit: bool
    timestamp: datetime


class QueryCache:
    """Redis-based query result cache."""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.default_ttl = 300  # 5 minutes

    def _generate_cache_key(self, query: str, params: Dict[str, Any]) -> str:
        cache_data = {
            'query': query,
            'params': sorted(params.items()) if params else []
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"query_cache:{hashlib.md5(cache_string.encode()).hexdigest()}"

    async def get(self, query: str, params: Dict[str, Any] = None) -> Optional[Any]:
        cache_key = self._generate_cache_key(query, params or {})
        try:
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
        except Exception:
            pass
        return None

    async def set(self, query: str, result: Any, params: Dict[str, Any] = None, ttl: int = None) -> None:
        cache_key = self._generate_cache_key(query, params or {})
        ttl = ttl or self.default_ttl
        try:
            self.redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(result, default=str)
            )
        except Exception:
            pass

    async def invalidate_pattern(self, pattern: str) -> None:
        try:
            keys = self.redis_client.keys(f"query_cache:*{pattern}*")
            if keys:
                self.redis_client.delete(*keys)
        except Exception:
            pass


class QueryOptimizer:
    """Service for optimizing analytics queries."""

    def __init__(self, db: AsyncSession, company_id: UUID):
        self.db = db
        self.company_id = company_id
        self.cache = QueryCache()
        self.metrics: List[QueryMetrics] = []

    def cached_query(self, ttl: int = 300):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # Try to get from cache
                start_time = datetime.now()
                cached_result = await self.cache.get(cache_key)
                
                if cached_result is not None:
                    execution_time = (datetime.now() - start_time).total_seconds()
                    self._record_metrics(cache_key, execution_time, len(cached_result) if isinstance(cached_result, list) else 1, True)
                    return cached_result

                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.cache.set(cache_key, result, ttl=ttl)
                
                execution_time = (datetime.now() - start_time).total_seconds()
                self._record_metrics(cache_key, execution_time, len(result) if isinstance(result, list) else 1, False)
                
                return result
            return wrapper
        return decorator

    async def optimize_financial_summary_query(self, date_range: Dict[str, datetime]) -> Dict[str, Any]:
        
        # Use a single query with CTEs for better performance
        query = text("""
            WITH revenue_summary AS (
                SELECT 
                    COALESCE(SUM(t.amount), 0) as total_revenue
                FROM transactions t
                JOIN accounts a ON t.account_id = a.id
                WHERE a.company_id = :company_id
                AND a.account_type = 'revenue'
                AND t.transaction_type = 'credit'
                AND t.transaction_date BETWEEN :start_date AND :end_date
            ),
            expense_summary AS (
                SELECT 
                    COALESCE(SUM(t.amount), 0) as total_expenses
                FROM transactions t
                JOIN accounts a ON t.account_id = a.id
                WHERE a.company_id = :company_id
                AND a.account_type = 'expense'
                AND t.transaction_type = 'debit'
                AND t.transaction_date BETWEEN :start_date AND :end_date
            ),
            cash_flow_summary AS (
                SELECT 
                    COALESCE(SUM(r.amount), 0) as total_inflows,
                    COALESCE(SUM(p.amount), 0) as total_outflows
                FROM (
                    SELECT amount FROM receipts 
                    WHERE company_id = :company_id 
                    AND receipt_date BETWEEN :start_date AND :end_date
                ) r
                FULL OUTER JOIN (
                    SELECT amount FROM payments 
                    WHERE company_id = :company_id 
                    AND payment_date BETWEEN :start_date AND :end_date
                ) p ON true
            )
            SELECT 
                r.total_revenue,
                e.total_expenses,
                (r.total_revenue - e.total_expenses) as profit,
                cf.total_inflows,
                cf.total_outflows,
                (cf.total_inflows - cf.total_outflows) as net_cash_flow
            FROM revenue_summary r
            CROSS JOIN expense_summary e
            CROSS JOIN cash_flow_summary cf
        """)

        result = await self.db.execute(query, {
            'company_id': str(self.company_id),
            'start_date': date_range['start'],
            'end_date': date_range['end']
        })
        
        row = result.fetchone()
        
        return {
            'revenue': float(row.total_revenue or 0),
            'expenses': float(row.total_expenses or 0),
            'profit': float(row.profit or 0),
            'profit_margin': float((row.profit / row.total_revenue * 100) if row.total_revenue > 0 else 0),
            'cash_flow': {
                'inflows': float(row.total_inflows or 0),
                'outflows': float(row.total_outflows or 0),
                'net_cash_flow': float(row.net_cash_flow or 0)
            }
        }

    @cached_query(ttl=600)  # Cache for 10 minutes
    async def get_trend_data_optimized(self, metric: str, period: str, months: int) -> List[Dict[str, Any]]:
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        if period == 'monthly':
            date_trunc = 'month'
            date_format = 'YYYY-MM'
        elif period == 'weekly':
            date_trunc = 'week'
            date_format = 'YYYY-"W"WW'
        else:
            date_trunc = 'day'
            date_format = 'YYYY-MM-DD'

        if metric == 'revenue':
            query = text(f"""
                SELECT 
                    TO_CHAR(DATE_TRUNC('{date_trunc}', t.transaction_date), '{date_format}') as period,
                    SUM(t.amount) as value
                FROM transactions t
                JOIN accounts a ON t.account_id = a.id
                WHERE a.company_id = :company_id
                AND a.account_type = 'revenue'
                AND t.transaction_type = 'credit'
                AND t.transaction_date BETWEEN :start_date AND :end_date
                GROUP BY DATE_TRUNC('{date_trunc}', t.transaction_date)
                ORDER BY DATE_TRUNC('{date_trunc}', t.transaction_date)
            """)
        elif metric == 'expenses':
            query = text(f"""
                SELECT 
                    TO_CHAR(DATE_TRUNC('{date_trunc}', t.transaction_date), '{date_format}') as period,
                    SUM(t.amount) as value
                FROM transactions t
                JOIN accounts a ON t.account_id = a.id
                WHERE a.company_id = :company_id
                AND a.account_type = 'expense'
                AND t.transaction_type = 'debit'
                AND t.transaction_date BETWEEN :start_date AND :end_date
                GROUP BY DATE_TRUNC('{date_trunc}', t.transaction_date)
                ORDER BY DATE_TRUNC('{date_trunc}', t.transaction_date)
            """)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        result = await self.db.execute(query, {
            'company_id': str(self.company_id),
            'start_date': start_date,
            'end_date': end_date
        })

        return [
            {
                'period': row.period,
                'value': float(row.value or 0),
                'metric': metric
            }
            for row in result.fetchall()
        ]

    async def create_analytics_indexes(self) -> None:
        
        indexes = [
            # Transaction indexes
            Index('idx_transactions_company_date', 'company_id', 'transaction_date'),
            Index('idx_transactions_account_type_date', 'account_id', 'transaction_type', 'transaction_date'),
            
            # Account indexes
            Index('idx_accounts_company_type', 'company_id', 'account_type'),
            
            # Invoice indexes
            Index('idx_ar_invoices_company_status_date', 'company_id', 'status', 'invoice_date'),
            Index('idx_ap_invoices_company_status_date', 'company_id', 'status', 'invoice_date'),
            
            # Receipt and Payment indexes
            Index('idx_receipts_company_date', 'company_id', 'receipt_date'),
            Index('idx_payments_company_date', 'company_id', 'payment_date'),
        ]

        for index in indexes:
            try:
                await self.db.execute(f"CREATE INDEX IF NOT EXISTS {index.name} ON {index.table.name} ({', '.join(index.columns.keys())})")
            except Exception as e:
                print(f"Failed to create index {index.name}: {e}")

    async def analyze_query_performance(self) -> Dict[str, Any]:
        
        if not self.metrics:
            return {'message': 'No metrics available'}

        total_queries = len(self.metrics)
        cache_hits = sum(1 for m in self.metrics if m.cache_hit)
        cache_hit_rate = (cache_hits / total_queries) * 100 if total_queries > 0 else 0
        
        avg_execution_time = sum(m.execution_time for m in self.metrics) / total_queries if total_queries > 0 else 0
        
        slow_queries = [m for m in self.metrics if m.execution_time > 1.0]  # Queries taking more than 1 second
        
        return {
            'total_queries': total_queries,
            'cache_hit_rate': cache_hit_rate,
            'average_execution_time': avg_execution_time,
            'slow_queries_count': len(slow_queries),
            'slow_queries': [
                {
                    'query_hash': q.query_hash,
                    'execution_time': q.execution_time,
                    'timestamp': q.timestamp.isoformat()
                }
                for q in slow_queries[-10:]  # Last 10 slow queries
            ]
        }

    def _record_metrics(self, query_hash: str, execution_time: float, rows_returned: int, cache_hit: bool) -> None:
        
        metric = QueryMetrics(
            query_hash=query_hash,
            execution_time=execution_time,
            rows_returned=rows_returned,
            cache_hit=cache_hit,
            timestamp=datetime.now()
        )
        
        self.metrics.append(metric)
        
        # Keep only last 1000 metrics to prevent memory issues
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]

    async def invalidate_cache_for_company(self) -> None:
        await self.cache.invalidate_pattern(str(self.company_id))

    async def warm_cache(self) -> None:
        
        # Warm up financial summary
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        await self.optimize_financial_summary_query({
            'start': current_month,
            'end': datetime.now()
        })
        
        # Warm up trend data
        await self.get_trend_data_optimized('revenue', 'monthly', 12)
        await self.get_trend_data_optimized('expenses', 'monthly', 12)