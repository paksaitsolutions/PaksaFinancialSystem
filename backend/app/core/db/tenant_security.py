from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any
from .tenant_middleware import get_current_tenant
import logging

logger = logging.getLogger(__name__)

class TenantSecurityManager:
    """Manages tenant data security and isolation"""
    
    @staticmethod
    async def set_tenant_context_in_db(db: AsyncSession, tenant_id: str):
        """Set the current tenant context in the database session"""
        await db.execute(text(f"SET app.current_tenant = '{tenant_id}'"))
    
    @staticmethod
    async def validate_tenant_access(db: AsyncSession, model_instance: Any, tenant_id: str):
        """Validate that a model instance belongs to the specified tenant"""
        if hasattr(model_instance, 'tenant_id'):
            if model_instance.tenant_id != tenant_id:
                logger.warning(f"Attempted cross-tenant access: {tenant_id} tried to access {model_instance.tenant_id}")
                raise PermissionError("Cross-tenant access denied")
    
    @staticmethod
    def setup_tenant_security_events():
        """Setup SQLAlchemy events for tenant security"""
        
        @event.listens_for(Session, "before_flush")
        def validate_tenant_on_flush(session, flush_context, instances):
            """Validate tenant isolation before flushing changes"""
            try:
                current_tenant = get_current_tenant()
                
                for instance in session.new:
                    if hasattr(instance, 'tenant_id'):
                        if not instance.tenant_id:
                            instance.tenant_id = current_tenant
                        elif instance.tenant_id != current_tenant:
                            raise PermissionError(f"Cannot create object for different tenant: {instance.tenant_id}")
                
                for instance in session.dirty:
                    if hasattr(instance, 'tenant_id'):
                        if instance.tenant_id != current_tenant:
                            raise PermissionError(f"Cannot modify object from different tenant: {instance.tenant_id}")
                
                for instance in session.deleted:
                    if hasattr(instance, 'tenant_id'):
                        if instance.tenant_id != current_tenant:
                            raise PermissionError(f"Cannot delete object from different tenant: {instance.tenant_id}")
                            
            except Exception as e:
                logger.error(f"Tenant security validation failed: {e}")
                raise
        
        @event.listens_for(Session, "after_transaction_create")
        def set_tenant_context_on_transaction(session, transaction):
            """Set tenant context when a new transaction is created"""
            try:
                tenant_id = get_current_tenant()
                session.execute(text(f"SET LOCAL app.current_tenant = '{tenant_id}'"))
            except Exception:
                # If no tenant context is available, that's okay for some operations
                pass

class CrossTenantPreventionMixin:
    """Mixin to prevent cross-tenant data access"""
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        # Add tenant validation to all query methods
        original_get = cls.get if hasattr(cls, 'get') else None
        original_get_multi = cls.get_multi if hasattr(cls, 'get_multi') else None
        
        if original_get:
            def validated_get(self, db: AsyncSession, id: Any):
                result = original_get(self, db, id)
                if result and hasattr(result, 'tenant_id'):
                    current_tenant = get_current_tenant()
                    if result.tenant_id != current_tenant:
                        logger.warning(f"Cross-tenant access attempt blocked: {current_tenant} -> {result.tenant_id}")
                        return None
                return result
            cls.get = validated_get
        
        if original_get_multi:
            def validated_get_multi(self, db: AsyncSession, **kwargs):
                results = original_get_multi(self, db, **kwargs)
                current_tenant = get_current_tenant()
                filtered_results = []
                for result in results:
                    if hasattr(result, 'tenant_id') and result.tenant_id == current_tenant:
                        filtered_results.append(result)
                    elif not hasattr(result, 'tenant_id'):
                        filtered_results.append(result)
                return filtered_results
            cls.get_multi = validated_get_multi

def create_tenant_backup_policy():
    """Create database policy for tenant data backup"""
    return """
    CREATE OR REPLACE FUNCTION backup_tenant_data(target_tenant_id TEXT)
    RETURNS TABLE(table_name TEXT, row_count BIGINT) AS $$
    DECLARE
        table_record RECORD;
        query TEXT;
        backup_path TEXT;
    BEGIN
        backup_path := '/backups/tenant_' || target_tenant_id || '/';
        
        FOR table_record IN 
            SELECT t.table_name 
            FROM information_schema.tables t
            JOIN information_schema.columns c ON t.table_name = c.table_name
            WHERE t.table_schema = 'public' 
            AND c.column_name = 'tenant_id'
        LOOP
            query := format('COPY (SELECT * FROM %I WHERE tenant_id = %L) TO %L CSV HEADER',
                          table_record.table_name, target_tenant_id, 
                          backup_path || table_record.table_name || '.csv');
            EXECUTE query;
            
            EXECUTE format('SELECT COUNT(*) FROM %I WHERE tenant_id = %L', 
                          table_record.table_name, target_tenant_id) INTO row_count;
            
            table_name := table_record.table_name;
            RETURN NEXT;
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;
    """

def create_tenant_restore_policy():
    """Create database policy for tenant data restore"""
    return """
    CREATE OR REPLACE FUNCTION restore_tenant_data(target_tenant_id TEXT, backup_date DATE)
    RETURNS TABLE(table_name TEXT, rows_restored BIGINT) AS $$
    DECLARE
        table_record RECORD;
        query TEXT;
        backup_path TEXT;
    BEGIN
        backup_path := '/backups/tenant_' || target_tenant_id || '_' || backup_date || '/';
        
        FOR table_record IN 
            SELECT t.table_name 
            FROM information_schema.tables t
            JOIN information_schema.columns c ON t.table_name = c.table_name
            WHERE t.table_schema = 'public' 
            AND c.column_name = 'tenant_id'
        LOOP
            -- Clear existing data for tenant
            EXECUTE format('DELETE FROM %I WHERE tenant_id = %L', 
                          table_record.table_name, target_tenant_id);
            
            -- Restore from backup
            query := format('COPY %I FROM %L CSV HEADER',
                          table_record.table_name,
                          backup_path || table_record.table_name || '.csv');
            EXECUTE query;
            
            GET DIAGNOSTICS rows_restored = ROW_COUNT;
            table_name := table_record.table_name;
            RETURN NEXT;
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;
    """