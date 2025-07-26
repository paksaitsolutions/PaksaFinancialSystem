from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database query optimization service"""
    
    async def optimize_queries(self, db: AsyncSession):
        """Optimize database queries with indexes"""
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_ap_bills_vendor_date ON ap_bills(vendor_id, bill_date)",
            "CREATE INDEX IF NOT EXISTS idx_ap_payments_date_status ON ap_payments(payment_date, status)",
            "CREATE INDEX IF NOT EXISTS idx_ar_invoices_customer_due ON ar_invoices(customer_id, due_date)",
            "CREATE INDEX IF NOT EXISTS idx_ar_payments_customer_date ON ar_payments(customer_id, payment_date)",
            "CREATE INDEX IF NOT EXISTS idx_cm_transactions_account_date ON cm_bank_transactions(account_id, transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_budgets_fiscal_status ON budgets(fiscal_year, status)"
        ]
        
        for index_sql in indexes:
            try:
                await db.execute(text(index_sql))
                logger.info(f"Created index: {index_sql}")
            except Exception as e:
                logger.warning(f"Index creation failed: {e}")
        
        await db.commit()
        return {"indexes_created": len(indexes)}
    
    async def analyze_slow_queries(self, db: AsyncSession) -> List[Dict]:
        """Analyze slow queries"""
        
        slow_queries = []
        try:
            result = await db.execute(text("""
                SELECT query, calls, total_time, mean_time
                FROM pg_stat_statements 
                WHERE mean_time > 100
                ORDER BY mean_time DESC
                LIMIT 10
            """))
            
            for row in result:
                slow_queries.append({
                    "query": row.query[:100] + "...",
                    "calls": row.calls,
                    "total_time": row.total_time,
                    "mean_time": row.mean_time
                })
        except Exception:
            slow_queries = [{"message": "Query analysis not available"}]
        
        return slow_queries