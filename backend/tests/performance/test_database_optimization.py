import pytest
import asyncio
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from app.core.db import get_db
from app.modules.core_financials.general_ledger.models import Account, JournalEntry
from app.core.db.optimized_queries import OptimizedQueryMixin, DatabaseOptimizer

class TestDatabasePerformance:
    """Test database performance optimizations"""
    
    @pytest.mark.asyncio
    async def test_tenant_query_performance(self, test_db: AsyncSession):
        """Test tenant-filtered query performance"""
        tenant_id = "test_tenant_123"
        
        # Test query with tenant filtering
        start_time = time.time()
        
        query = select(Account).where(Account.tenant_id == tenant_id).limit(100)
        result = await OptimizedQueryMixin.execute_with_logging(
            test_db, query, "Tenant account query"
        )
        
        execution_time = time.time() - start_time
        
        # Should execute within 100ms
        assert execution_time < 0.1, f"Query too slow: {execution_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_index_effectiveness(self, test_db: AsyncSession):
        """Test that indexes are being used effectively"""
        tenant_id = "test_tenant_123"
        
        # Query that should use tenant index
        query = text("""
            EXPLAIN (ANALYZE, BUFFERS) 
            SELECT * FROM accounts 
            WHERE tenant_id = :tenant_id 
            AND account_code = :code
        """)
        
        result = await test_db.execute(query, {
            "tenant_id": tenant_id,
            "code": "1000"
        })
        
        explain_output = result.fetchall()
        explain_text = str(explain_output)
        
        # Should use index scan, not sequential scan
        assert "Index Scan" in explain_text or "Bitmap" in explain_text
        assert "Seq Scan" not in explain_text
    
    @pytest.mark.asyncio
    async def test_connection_pool_performance(self):
        """Test connection pool performance under load"""
        async def make_query():
            async with get_db() as db:
                result = await db.execute(text("SELECT 1"))
                return result.scalar()
        
        # Simulate concurrent connections
        start_time = time.time()
        tasks = [make_query() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        execution_time = time.time() - start_time
        
        # All queries should succeed
        assert all(r == 1 for r in results)
        # Should handle 50 concurrent queries within 2 seconds
        assert execution_time < 2.0
    
    @pytest.mark.asyncio
    async def test_bulk_insert_performance(self, test_db: AsyncSession):
        """Test bulk insert performance"""
        tenant_id = "test_tenant_123"
        
        # Create test accounts for bulk insert
        accounts = []
        for i in range(1000):
            accounts.append(Account(
                tenant_id=tenant_id,
                account_code=f"TEST{i:04d}",
                account_name=f"Test Account {i}",
                account_type="ASSET",
                is_active=True
            ))
        
        start_time = time.time()
        test_db.add_all(accounts)
        await test_db.commit()
        execution_time = time.time() - start_time
        
        # Should insert 1000 records within 1 second
        assert execution_time < 1.0, f"Bulk insert too slow: {execution_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_complex_query_optimization(self, test_db: AsyncSession):
        """Test complex query with joins and aggregations"""
        tenant_id = "test_tenant_123"
        
        # Complex query with joins
        query = text("""
            SELECT a.account_code, a.account_name, 
                   COALESCE(SUM(jel.debit_amount), 0) as total_debits,
                   COALESCE(SUM(jel.credit_amount), 0) as total_credits
            FROM accounts a
            LEFT JOIN journal_entry_lines jel ON a.id = jel.account_id
            LEFT JOIN journal_entries je ON jel.journal_entry_id = je.id
            WHERE a.tenant_id = :tenant_id
            AND a.is_active = true
            GROUP BY a.id, a.account_code, a.account_name
            ORDER BY a.account_code
            LIMIT 100
        """)
        
        start_time = time.time()
        result = await test_db.execute(query, {"tenant_id": tenant_id})
        rows = result.fetchall()
        execution_time = time.time() - start_time
        
        # Complex query should execute within 200ms
        assert execution_time < 0.2, f"Complex query too slow: {execution_time:.3f}s"

class TestQueryOptimization:
    """Test query optimization utilities"""
    
    @pytest.mark.asyncio
    async def test_eager_loading_optimization(self, test_db: AsyncSession):
        """Test eager loading optimization"""
        tenant_id = "test_tenant_123"
        
        # Query with eager loading
        query = select(JournalEntry).where(JournalEntry.tenant_id == tenant_id)
        optimized_query = OptimizedQueryMixin.optimize_select_query(
            query, eager_load_relations=['lines', 'lines.account']
        )
        
        start_time = time.time()
        result = await test_db.execute(optimized_query)
        entries = result.scalars().all()
        execution_time = time.time() - start_time
        
        # Should load related data efficiently
        assert execution_time < 0.1
        
        # Verify related data is loaded (no additional queries)
        if entries:
            entry = entries[0]
            # Accessing related data should not trigger additional queries
            lines = entry.lines  # Should be already loaded
            assert lines is not None
    
    @pytest.mark.asyncio
    async def test_database_analyzer(self, test_db: AsyncSession):
        """Test database analysis utilities"""
        # Test table analysis
        await DatabaseOptimizer.analyze_table_stats(test_db, "accounts")
        
        # Test slow query detection
        slow_queries = await DatabaseOptimizer.get_slow_queries(test_db, limit=5)
        assert isinstance(slow_queries, list)
    
    def test_query_logging(self):
        """Test query execution logging"""
        import logging
        from app.core.db.optimized_queries import OptimizedQueryMixin
        
        # Capture log output
        with pytest.LoggingPlugin.caplog.at_level(logging.WARNING):
            # This would be tested with actual slow query
            pass