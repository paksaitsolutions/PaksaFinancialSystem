from sqlalchemy import Index, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Database indexes for performance optimization
PERFORMANCE_INDEXES = [
    # Tenant-based indexes
    Index('idx_accounts_tenant_code', 'tenant_id', 'account_code'),
    Index('idx_journal_entries_tenant_date', 'tenant_id', 'entry_date'),
    Index('idx_journal_entry_lines_tenant_account', 'tenant_id', 'account_id'),
    Index('idx_fixed_assets_tenant_status', 'tenant_id', 'status'),
    Index('idx_budgets_tenant_period', 'tenant_id', 'start_date', 'end_date'),
    Index('idx_tax_transactions_tenant_date', 'tenant_id', 'transaction_date'),
    Index('idx_users_tenant_email', 'tenant_id', 'email'),
    
    # Performance indexes
    Index('idx_journal_entries_date_desc', 'entry_date DESC'),
    Index('idx_accounts_active_code', 'is_active', 'account_code'),
    Index('idx_transactions_amount_date', 'amount', 'created_at'),
]

class OptimizedQueryMixin:
    """Mixin for optimized database queries"""
    
    @staticmethod
    async def execute_with_logging(db: AsyncSession, query, description: str = "Query"):
        """Execute query with performance logging"""
        import time
        start_time = time.time()
        
        try:
            result = await db.execute(query)
            execution_time = time.time() - start_time
            
            if execution_time > 0.1:  # Log slow queries (>100ms)
                logger.warning(f"Slow query detected: {description} took {execution_time:.3f}s")
            
            return result
        except Exception as e:
            logger.error(f"Query failed: {description} - {str(e)}")
            raise
    
    @staticmethod
    def optimize_select_query(query, eager_load_relations: List[str] = None):
        """Optimize SELECT query with eager loading"""
        if eager_load_relations:
            for relation in eager_load_relations:
                if '.' in relation:
                    # Nested relation
                    query = query.options(selectinload(relation))
                else:
                    # Direct relation
                    query = query.options(joinedload(relation))
        
        return query

class DatabaseOptimizer:
    """Database optimization utilities"""
    
    @staticmethod
    async def create_performance_indexes(db: AsyncSession):
        """Create performance indexes"""
        for index in PERFORMANCE_INDEXES:
            try:
                await db.execute(text(f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {index.name} ON {index.table.name} ({', '.join(index.columns)})"))
                logger.info(f"Created index: {index.name}")
            except Exception as e:
                logger.warning(f"Failed to create index {index.name}: {e}")
    
    @staticmethod
    async def analyze_table_stats(db: AsyncSession, table_name: str):
        """Analyze table statistics for optimization"""
        try:
            await db.execute(text(f"ANALYZE {table_name}"))
            logger.info(f"Analyzed table: {table_name}")
        except Exception as e:
            logger.error(f"Failed to analyze table {table_name}: {e}")
    
    @staticmethod
    async def get_slow_queries(db: AsyncSession, limit: int = 10):
        """Get slow queries from PostgreSQL logs"""
        try:
            result = await db.execute(text("""
                SELECT query, mean_time, calls, total_time
                FROM pg_stat_statements
                ORDER BY mean_time DESC
                LIMIT :limit
            """), {"limit": limit})
            return result.fetchall()
        except Exception as e:
            logger.error(f"Failed to get slow queries: {e}")
            return []

# Connection pool optimization
DATABASE_POOL_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True
}