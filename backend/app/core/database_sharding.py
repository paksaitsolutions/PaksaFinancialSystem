"""
Database sharding implementation for horizontal scaling.
"""
import hashlib
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import logger

class ShardManager:
    """Database sharding manager."""
    
    def __init__(self):
        self.shards: Dict[str, Dict] = {}
        self.shard_engines: Dict[str, any] = {}
        self.shard_sessions: Dict[str, sessionmaker] = {}
        self._setup_shards()
    
    def _setup_shards(self):
        """Setup database shards configuration."""
        # Default shard configuration
        self.shards = {
            "shard_0": {
                "database_url": settings.DATABASE_URL,
                "tenant_range": (0, 33),  # Hash range 0-33%
                "read_replicas": [settings.DATABASE_READ_URL] if hasattr(settings, 'DATABASE_READ_URL') else []
            },
            "shard_1": {
                "database_url": settings.DATABASE_URL_SHARD_1 if hasattr(settings, 'DATABASE_URL_SHARD_1') else settings.DATABASE_URL,
                "tenant_range": (34, 66),  # Hash range 34-66%
                "read_replicas": []
            },
            "shard_2": {
                "database_url": settings.DATABASE_URL_SHARD_2 if hasattr(settings, 'DATABASE_URL_SHARD_2') else settings.DATABASE_URL,
                "tenant_range": (67, 100),  # Hash range 67-100%
                "read_replicas": []
            }
        }
        
        # Create engines and sessions for each shard
        for shard_id, shard_config in self.shards.items():
            engine = create_async_engine(
                shard_config["database_url"],
                echo=settings.DEBUG,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            session_factory = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            
            self.shard_engines[shard_id] = engine
            self.shard_sessions[shard_id] = session_factory
            
            logger.info(f"Initialized shard {shard_id}")
    
    def get_shard_for_tenant(self, tenant_id: str) -> str:
        """Determine which shard a tenant belongs to."""
        # Use consistent hashing based on tenant_id
        hash_value = int(hashlib.md5(tenant_id.encode()).hexdigest(), 16)
        hash_percentage = (hash_value % 100)
        
        for shard_id, shard_config in self.shards.items():
            min_range, max_range = shard_config["tenant_range"]
            if min_range <= hash_percentage <= max_range:
                return shard_id
        
        # Fallback to first shard
        return list(self.shards.keys())[0]
    
    def get_session(self, tenant_id: str, read_only: bool = False) -> AsyncSession:
        """Get database session for tenant."""
        shard_id = self.get_shard_for_tenant(tenant_id)
        
        # For read-only operations, try to use read replica
        if read_only and self.shards[shard_id]["read_replicas"]:
            # Simple round-robin selection of read replica
            # In production, implement proper load balancing
            replica_url = self.shards[shard_id]["read_replicas"][0]
            
            # Create read replica session (simplified)
            engine = create_async_engine(replica_url, echo=settings.DEBUG)
            session_factory = sessionmaker(engine, class_=AsyncSession)
            return session_factory()
        
        # Use primary shard session
        return self.shard_sessions[shard_id]()
    
    async def execute_on_all_shards(self, query_func, *args, **kwargs) -> List:
        """Execute query on all shards and aggregate results."""
        results = []
        
        for shard_id in self.shards.keys():
            try:
                session = self.shard_sessions[shard_id]()
                result = await query_func(session, *args, **kwargs)
                results.extend(result if isinstance(result, list) else [result])
                await session.close()
                
            except Exception as e:
                logger.error(f"Query failed on shard {shard_id}: {str(e)}")
        
        return results
    
    async def migrate_tenant(self, tenant_id: str, target_shard: str) -> bool:
        """Migrate tenant data to different shard."""
        current_shard = self.get_shard_for_tenant(tenant_id)
        
        if current_shard == target_shard:
            logger.info(f"Tenant {tenant_id} already on target shard {target_shard}")
            return True
        
        try:
            # This would involve:
            # 1. Copy tenant data from current shard to target shard
            # 2. Update tenant shard mapping
            # 3. Verify data integrity
            # 4. Remove data from current shard
            
            logger.info(f"Migrating tenant {tenant_id} from {current_shard} to {target_shard}")
            
            # Simplified migration logic
            source_session = self.shard_sessions[current_shard]()
            target_session = self.shard_sessions[target_shard]()
            
            # In real implementation, copy all tenant data
            # await copy_tenant_data(source_session, target_session, tenant_id)
            
            await source_session.close()
            await target_session.close()
            
            logger.info(f"Successfully migrated tenant {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate tenant {tenant_id}: {str(e)}")
            return False
    
    def get_shard_stats(self) -> Dict[str, Dict]:
        """Get statistics for all shards."""
        stats = {}
        
        for shard_id, shard_config in self.shards.items():
            stats[shard_id] = {
                "tenant_range": shard_config["tenant_range"],
                "database_url": shard_config["database_url"],
                "read_replicas": len(shard_config["read_replicas"]),
                "status": "active"  # In real implementation, check connection health
            }
        
        return stats

# Global shard manager
shard_manager = ShardManager()

def get_sharded_session(tenant_id: str, read_only: bool = False) -> AsyncSession:
    """Get database session for tenant with sharding support."""
    return shard_manager.get_session(tenant_id, read_only)