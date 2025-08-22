from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional
from app.core.db.tenant_base import Company
from app.core.db.tenant_migration import migration_manager
from app.core.db.tenant_security import TenantSecurityManager
import uuid
import logging

logger = logging.getLogger(__name__)

class TenantService:
    async def create_tenant(self, db: AsyncSession, company_data: dict) -> Company:
        """Create a new tenant with isolated data"""
        
        # Generate unique tenant_id
        tenant_id = str(uuid.uuid4())[:8]
        
        # Create company record
        company = Company(
            tenant_id=tenant_id,
            name=company_data['name'],
            email=company_data['email'],
            phone=company_data.get('phone'),
            address=company_data.get('address'),
            industry=company_data.get('industry'),
            status='active'
        )
        
        db.add(company)
        await db.commit()
        await db.refresh(company)
        
        # Setup tenant database structure
        await self._setup_tenant_database(tenant_id)
        
        logger.info(f"Created new tenant: {tenant_id} for company: {company_data['name']}")
        return company
    
    async def get_tenant_by_id(self, db: AsyncSession, tenant_id: str) -> Optional[Company]:
        """Get tenant by ID"""
        result = await db.execute(select(Company).where(Company.tenant_id == tenant_id))
        return result.scalar_one_or_none()
    
    async def list_tenants(self, db: AsyncSession) -> List[Company]:
        """List all tenants (admin only)"""
        result = await db.execute(select(Company).where(Company.is_active == True))
        return result.scalars().all()
    
    async def suspend_tenant(self, db: AsyncSession, tenant_id: str) -> bool:
        """Suspend a tenant"""
        company = await self.get_tenant_by_id(db, tenant_id)
        if company:
            company.status = 'suspended'
            await db.commit()
            logger.info(f"Suspended tenant: {tenant_id}")
            return True
        return False
    
    async def delete_tenant(self, db: AsyncSession, tenant_id: str) -> bool:
        """Delete a tenant and all its data"""
        company = await self.get_tenant_by_id(db, tenant_id)
        if company:
            # Backup tenant data before deletion
            await migration_manager.backup_tenant_data(tenant_id, f"/backups/{tenant_id}")
            
            # Delete tenant data
            await self._delete_tenant_data(db, tenant_id)
            
            # Mark company as deleted
            company.is_active = False
            company.status = 'deleted'
            await db.commit()
            
            logger.info(f"Deleted tenant: {tenant_id}")
            return True
        return False
    
    async def get_tenant_stats(self, db: AsyncSession, tenant_id: str) -> dict:
        """Get statistics for a tenant"""
        stats = {}
        
        # Count records in each table
        tables = ['fixed_assets', 'budgets', 'tax_transactions', 'accounts', 'journal_entries']
        
        for table in tables:
            result = await db.execute(text(f"SELECT COUNT(*) FROM {table} WHERE tenant_id = :tenant_id"), 
                                    {"tenant_id": tenant_id})
            stats[table] = result.scalar()
        
        return stats
    
    async def _setup_tenant_database(self, tenant_id: str):
        """Setup database structure for new tenant"""
        try:
            # Create tenant schema if using schema isolation
            await migration_manager.create_tenant_schema(tenant_id)
            
            # Run migrations for tenant
            migration_manager.run_tenant_migrations(tenant_id)
            
            # Setup security policies
            await migration_manager.setup_row_level_security()
            
        except Exception as e:
            logger.error(f"Failed to setup database for tenant {tenant_id}: {e}")
            raise
    
    async def _delete_tenant_data(self, db: AsyncSession, tenant_id: str):
        """Delete all data for a tenant"""
        tables = [
            'maintenance_records', 'depreciation_entries', 'fixed_assets',
            'budget_line_items', 'budgets', 'tax_transaction_components',
            'tax_transactions', 'tax_exemptions', 'journal_entry_lines',
            'journal_entries', 'accounts'
        ]
        
        for table in tables:
            await db.execute(text(f"DELETE FROM {table} WHERE tenant_id = :tenant_id"), 
                           {"tenant_id": tenant_id})
        
        await db.commit()

tenant_service = TenantService()