from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
from typing import List
from app.core.config import settings

class TenantMigrationManager:
    """Manages database migrations for multi-tenant architecture"""
    
    def __init__(self):
        self.alembic_cfg = Config("alembic.ini")
        self.engine = create_async_engine(settings.DATABASE_URL)
    
    async def create_tenant_schema(self, tenant_id: str):
        """Create a new schema for a tenant"""
        async with self.engine.begin() as conn:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS tenant_{tenant_id}"))
            await conn.execute(text(f"GRANT ALL ON SCHEMA tenant_{tenant_id} TO {settings.DB_USER}"))
    
    async def drop_tenant_schema(self, tenant_id: str):
        """Drop a tenant's schema"""
        async with self.engine.begin() as conn:
            await conn.execute(text(f"DROP SCHEMA IF EXISTS tenant_{tenant_id} CASCADE"))
    
    def run_tenant_migrations(self, tenant_id: str):
        """Run migrations for a specific tenant schema"""
        # Set the schema search path for this migration
        self.alembic_cfg.set_main_option("sqlalchemy.url", 
            f"{settings.DATABASE_URL}?options=-csearch_path=tenant_{tenant_id}")
        
        # Run the migration
        command.upgrade(self.alembic_cfg, "head")
    
    async def migrate_all_tenants(self):
        """Run migrations for all existing tenants"""
        # Get all tenant schemas
        async with self.engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name LIKE 'tenant_%'
            """))
            schemas = result.fetchall()
        
        # Run migrations for each tenant
        for schema in schemas:
            tenant_id = schema[0].replace('tenant_', '')
            self.run_tenant_migrations(tenant_id)
    
    async def add_tenant_id_columns(self):
        """Add tenant_id columns to existing tables"""
        tables_to_update = [
            'fixed_assets', 'depreciation_entries', 'maintenance_records',
            'budgets', 'budget_line_items', 'tax_jurisdictions', 'tax_rates',
            'tax_transactions', 'tax_exemptions', 'tax_returns', 'accounts',
            'journal_entries', 'journal_entry_lines', 'fiscal_periods'
        ]
        
        async with self.engine.begin() as conn:
            for table in tables_to_update:
                # Check if tenant_id column exists
                result = await conn.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = 'tenant_id'
                """))
                
                if not result.fetchone():
                    # Add tenant_id column
                    await conn.execute(text(f"""
                        ALTER TABLE {table} 
                        ADD COLUMN tenant_id VARCHAR(50) NOT NULL DEFAULT 'default'
                    """))
                    
                    # Create index on tenant_id
                    await conn.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS idx_{table}_tenant_id 
                        ON {table} (tenant_id)
                    """))
    
    async def setup_row_level_security(self):
        """Setup row-level security policies for tenant isolation"""
        tables_with_rls = [
            'fixed_assets', 'depreciation_entries', 'maintenance_records',
            'budgets', 'budget_line_items', 'tax_transactions', 'accounts',
            'journal_entries', 'journal_entry_lines'
        ]
        
        async with self.engine.begin() as conn:
            for table in tables_with_rls:
                # Enable RLS
                await conn.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
                
                # Create policy for tenant isolation
                await conn.execute(text(f"""
                    CREATE POLICY tenant_isolation ON {table}
                    FOR ALL
                    TO PUBLIC
                    USING (tenant_id = current_setting('app.current_tenant', true))
                """))
    
    async def backup_tenant_data(self, tenant_id: str, backup_path: str):
        """Backup data for a specific tenant"""
        async with self.engine.begin() as conn:
            # Export tenant data to backup file
            await conn.execute(text(f"""
                COPY (
                    SELECT * FROM fixed_assets WHERE tenant_id = '{tenant_id}'
                ) TO '{backup_path}/fixed_assets_{tenant_id}.csv' CSV HEADER
            """))
            # Add more tables as needed
    
    async def restore_tenant_data(self, tenant_id: str, backup_path: str):
        """Restore data for a specific tenant"""
        async with self.engine.begin() as conn:
            # Import tenant data from backup file
            await conn.execute(text(f"""
                COPY fixed_assets FROM '{backup_path}/fixed_assets_{tenant_id}.csv' 
                CSV HEADER
            """))
            # Add more tables as needed

# Global migration manager instance
migration_manager = TenantMigrationManager()