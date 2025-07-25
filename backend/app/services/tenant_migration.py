"""
Tenant-aware database migration service.
"""
import asyncio
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.db.session import get_db
from app.core.logging import logger

class TenantMigrationService:
    """Service for managing tenant-specific database operations."""
    
    def __init__(self):
        self.migration_scripts = {
            "create_tenant_schema": """
                -- Create tenant-specific views and functions if needed
                CREATE OR REPLACE FUNCTION get_tenant_data(tenant_uuid UUID)
                RETURNS TABLE(table_name TEXT, record_count BIGINT) AS $$
                BEGIN
                    RETURN QUERY
                    SELECT 
                        t.table_name::TEXT,
                        (SELECT COUNT(*) FROM information_schema.tables 
                         WHERE table_schema = 'public' 
                         AND table_name = t.table_name)::BIGINT
                    FROM information_schema.tables t
                    WHERE t.table_schema = 'public'
                    AND EXISTS (
                        SELECT 1 FROM information_schema.columns c
                        WHERE c.table_name = t.table_name
                        AND c.column_name = 'tenant_id'
                    );
                END;
                $$ LANGUAGE plpgsql;
            """,
            
            "setup_rls_policies": """
                -- Enable RLS on all tenant tables
                DO $$
                DECLARE
                    table_record RECORD;
                BEGIN
                    FOR table_record IN 
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        AND EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = table_record.table_name 
                            AND column_name = 'tenant_id'
                        )
                    LOOP
                        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_record.table_name);
                        
                        EXECUTE format('
                            CREATE POLICY tenant_isolation_policy ON %I
                            FOR ALL TO PUBLIC
                            USING (tenant_id = current_setting(''app.current_tenant_id'')::UUID)
                        ', table_record.table_name);
                    END LOOP;
                END $$;
            """
        }
    
    async def setup_tenant_environment(self, tenant_id: UUID) -> bool:
        """Setup database environment for a new tenant."""
        try:
            async with get_db() as db:
                # Set tenant context for this session
                await db.execute(
                    text("SET app.current_tenant_id = :tenant_id"),
                    {"tenant_id": str(tenant_id)}
                )
                
                # Run tenant setup scripts
                for script_name, script_sql in self.migration_scripts.items():
                    logger.info(f"Running {script_name} for tenant {tenant_id}")
                    await db.execute(text(script_sql))
                
                await db.commit()
                logger.info(f"Tenant environment setup completed for {tenant_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to setup tenant environment for {tenant_id}: {str(e)}")
            return False
    
    async def migrate_tenant_data(self, tenant_id: UUID, migration_name: str) -> bool:
        """Run specific migration for a tenant."""
        try:
            async with get_db() as db:
                # Set tenant context
                await db.execute(
                    text("SET app.current_tenant_id = :tenant_id"),
                    {"tenant_id": str(tenant_id)}
                )
                
                # Check if migration already applied
                result = await db.execute(
                    text("""
                        SELECT 1 FROM tenant_migrations 
                        WHERE tenant_id = :tenant_id AND migration_name = :migration_name
                    """),
                    {"tenant_id": tenant_id, "migration_name": migration_name}
                )
                
                if result.fetchone():
                    logger.info(f"Migration {migration_name} already applied for tenant {tenant_id}")
                    return True
                
                # Apply migration (placeholder - actual migrations would be defined)
                logger.info(f"Applying migration {migration_name} for tenant {tenant_id}")
                
                # Record migration
                await db.execute(
                    text("""
                        INSERT INTO tenant_migrations (tenant_id, migration_name, applied_at)
                        VALUES (:tenant_id, :migration_name, NOW())
                    """),
                    {"tenant_id": tenant_id, "migration_name": migration_name}
                )
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to migrate tenant {tenant_id}: {str(e)}")
            return False
    
    async def get_tenant_stats(self, tenant_id: UUID) -> Dict[str, Any]:
        """Get statistics for a specific tenant."""
        try:
            async with get_db() as db:
                # Set tenant context
                await db.execute(
                    text("SET app.current_tenant_id = :tenant_id"),
                    {"tenant_id": str(tenant_id)}
                )
                
                # Get table counts
                result = await db.execute(
                    text("SELECT * FROM get_tenant_data(:tenant_id)"),
                    {"tenant_id": tenant_id}
                )
                
                table_stats = {}
                for row in result.fetchall():
                    table_stats[row.table_name] = row.record_count
                
                return {
                    "tenant_id": str(tenant_id),
                    "table_statistics": table_stats,
                    "total_records": sum(table_stats.values())
                }
                
        except Exception as e:
            logger.error(f"Failed to get tenant stats for {tenant_id}: {str(e)}")
            return {}
    
    async def cleanup_tenant_data(self, tenant_id: UUID) -> bool:
        """Clean up all data for a tenant (use with caution)."""
        try:
            async with get_db() as db:
                # Get all tables with tenant_id column
                result = await db.execute(
                    text("""
                        SELECT table_name 
                        FROM information_schema.columns 
                        WHERE column_name = 'tenant_id' 
                        AND table_schema = 'public'
                    """)
                )
                
                tables = [row.table_name for row in result.fetchall()]
                
                # Delete data from each table
                for table in tables:
                    await db.execute(
                        text(f"DELETE FROM {table} WHERE tenant_id = :tenant_id"),
                        {"tenant_id": tenant_id}
                    )
                    logger.info(f"Cleaned up {table} for tenant {tenant_id}")
                
                await db.commit()
                logger.info(f"Tenant cleanup completed for {tenant_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to cleanup tenant {tenant_id}: {str(e)}")
            return False

# Global instance
tenant_migration_service = TenantMigrationService()