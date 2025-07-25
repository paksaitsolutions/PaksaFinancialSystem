"""
Database replication management.
"""
import asyncio
from typing import List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import logger

class DatabaseReplicationManager:
    """Manage database replication and read/write splitting."""
    
    def __init__(self):
        # Primary database (write operations)
        self.primary_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Read replicas
        self.replica_engines = []
        self.replica_sessions = []
        self.current_replica_index = 0
        
        self._setup_replicas()
    
    def _setup_replicas(self):
        """Setup read replica connections."""
        replica_urls = getattr(settings, 'DATABASE_REPLICA_URLS', [])
        
        for i, replica_url in enumerate(replica_urls):
            engine = create_async_engine(
                replica_url,
                echo=settings.DEBUG,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            session_factory = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            
            self.replica_engines.append(engine)
            self.replica_sessions.append(session_factory)
            
            logger.info(f"Configured read replica {i+1}")
    
    def get_write_session(self) -> AsyncSession:
        """Get session for write operations (primary database)."""
        session_factory = sessionmaker(
            self.primary_engine, class_=AsyncSession, expire_on_commit=False
        )
        return session_factory()
    
    def get_read_session(self) -> AsyncSession:
        """Get session for read operations (replica with load balancing)."""
        if not self.replica_sessions:
            # Fallback to primary if no replicas configured
            return self.get_write_session()
        
        # Round-robin load balancing
        session_factory = self.replica_sessions[self.current_replica_index]
        self.current_replica_index = (self.current_replica_index + 1) % len(self.replica_sessions)
        
        return session_factory()
    
    async def check_replica_health(self) -> List[Dict]:
        """Check health of all read replicas."""
        health_status = []
        
        for i, engine in enumerate(self.replica_engines):
            try:
                async with engine.begin() as conn:
                    await conn.execute("SELECT 1")
                
                health_status.append({
                    "replica_id": i + 1,
                    "status": "healthy",
                    "last_check": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                health_status.append({
                    "replica_id": i + 1,
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                })
                
                logger.error(f"Replica {i+1} health check failed: {str(e)}")
        
        return health_status
    
    async def get_replication_lag(self) -> List[Dict]:
        """Get replication lag for all replicas."""
        lag_info = []
        
        for i, engine in enumerate(self.replica_engines):
            try:
                async with engine.begin() as conn:
                    result = await conn.execute(
                        "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag"
                    )
                    lag_seconds = result.scalar()
                
                lag_info.append({
                    "replica_id": i + 1,
                    "lag_seconds": lag_seconds or 0,
                    "status": "ok" if (lag_seconds or 0) < 60 else "warning"
                })
                
            except Exception as e:
                lag_info.append({
                    "replica_id": i + 1,
                    "lag_seconds": None,
                    "status": "error",
                    "error": str(e)
                })
        
        return lag_info

# Global replication manager
db_replication = DatabaseReplicationManager()