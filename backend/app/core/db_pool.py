"""Database connection pooling configuration"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings

# Optimized engine configuration
engine_config = {
    "poolclass": QueuePool,
    "pool_size": 20,  # Number of connections to maintain
    "max_overflow": 10,  # Additional connections when pool is full
    "pool_timeout": 30,  # Seconds to wait for connection
    "pool_recycle": 3600,  # Recycle connections after 1 hour
    "pool_pre_ping": True,  # Verify connections before using
    "echo": False,  # Disable SQL logging in production
    "future": True,  # Use SQLAlchemy 2.0 style
}

def create_optimized_engine(database_url: str):
    """Create database engine with optimized settings"""
    engine = create_engine(database_url, **engine_config)
    
    # Add connection pool listeners
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Configure connection on creation"""
        # Set connection timeout
        dbapi_conn.execute("SET statement_timeout = '30s'")
        # Enable query plan caching
        dbapi_conn.execute("SET plan_cache_mode = 'force_generic_plan'")
    
    return engine

def get_session_factory(engine):
    """Create session factory with optimized settings"""
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False  # Prevent lazy loading after commit
    )

# Query optimization utilities
class QueryOptimizer:
    """Utilities for query optimization"""
    
    @staticmethod
    def add_eager_loading(query, *relationships):
        """Add eager loading for relationships"""
        from sqlalchemy.orm import joinedload
        for rel in relationships:
            query = query.options(joinedload(rel))
        return query
    
    @staticmethod
    def add_select_in_loading(query, *relationships):
        """Add select-in loading for collections"""
        from sqlalchemy.orm import selectinload
        for rel in relationships:
            query = query.options(selectinload(rel))
        return query
    
    @staticmethod
    def add_pagination(query, page: int, page_size: int):
        """Add efficient pagination"""
        offset = (page - 1) * page_size
        return query.offset(offset).limit(page_size)
