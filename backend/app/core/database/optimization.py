"""Database optimization utilities"""
from sqlalchemy import Index, text
from sqlalchemy.orm import selectinload, joinedload
from functools import wraps
import redis
import json
from typing import Any, Dict, List

# Redis cache instance
cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cached_query(expiration: int = 300):
    """Decorator for caching query results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute query and cache result
            result = func(*args, **kwargs)
            cache.setex(cache_key, expiration, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

# Database indexes for performance
PERFORMANCE_INDEXES = [
    # Tenant filtering indexes
    Index('idx_accounts_tenant_id', 'accounts.tenant_id'),
    Index('idx_transactions_tenant_id', 'transactions.tenant_id'),
    Index('idx_journal_entries_tenant_id', 'journal_entries.tenant_id'),
    Index('idx_employees_tenant_id', 'employees.tenant_id'),
    Index('idx_vendors_tenant_id', 'vendors.tenant_id'),
    
    # Frequently queried columns
    Index('idx_accounts_account_number', 'accounts.account_number'),
    Index('idx_transactions_date', 'transactions.transaction_date'),
    Index('idx_journal_entries_date', 'journal_entries.entry_date'),
    Index('idx_employees_email', 'employees.email'),
    Index('idx_vendors_name', 'vendors.name'),
    
    # Composite indexes for common queries
    Index('idx_transactions_tenant_date', 'transactions.tenant_id', 'transactions.transaction_date'),
    Index('idx_accounts_tenant_type', 'accounts.tenant_id', 'accounts.account_type'),
]

def optimize_tenant_query(query, tenant_id: str):
    """Optimize query with tenant filtering"""
    return query.filter_by(tenant_id=tenant_id)

def fix_n_plus_one_accounts(db_session, tenant_id: str):
    """Fix N+1 query for accounts with transactions"""
    return db_session.query(Account)\
        .options(selectinload(Account.transactions))\
        .filter_by(tenant_id=tenant_id)\
        .all()

def fix_n_plus_one_journal_entries(db_session, tenant_id: str):
    """Fix N+1 query for journal entries with line items"""
    return db_session.query(JournalEntry)\
        .options(selectinload(JournalEntry.line_items))\
        .filter_by(tenant_id=tenant_id)\
        .all()

class DatabaseConnectionPool:
    """Database connection pooling configuration"""
    
    @staticmethod
    def get_pool_config():
        return {
            'pool_size': 20,
            'max_overflow': 30,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'pool_pre_ping': True
        }