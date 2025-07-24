from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import event, select
from sqlalchemy.orm import Session
from typing import Any, Dict
from .tenant_middleware import get_current_tenant

class TenantAwareSession:
    """Session wrapper that automatically filters by tenant_id"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tenant_id = get_current_tenant()
    
    async def execute(self, statement, parameters=None, execution_options=None, bind_arguments=None, _parent_execute_state=None, _add_event=None):
        """Override execute to add tenant filtering"""
        # Add tenant_id filter to queries automatically
        if hasattr(statement, 'table') and hasattr(statement.table.c, 'tenant_id'):
            statement = statement.where(statement.table.c.tenant_id == self.tenant_id)
        
        return await self.session.execute(statement, parameters, execution_options, bind_arguments, _parent_execute_state, _add_event)
    
    def add(self, instance, _warn=True):
        """Override add to set tenant_id automatically"""
        if hasattr(instance, 'tenant_id'):
            instance.tenant_id = self.tenant_id
        return self.session.add(instance, _warn)
    
    def __getattr__(self, name):
        """Delegate all other methods to the wrapped session"""
        return getattr(self.session, name)

def setup_tenant_filters():
    """Setup automatic tenant filtering for all queries"""
    
    @event.listens_for(Session, "before_bulk_insert")
    def receive_before_bulk_insert(insert_context):
        """Add tenant_id to bulk inserts"""
        if hasattr(insert_context.mapper.class_, 'tenant_id'):
            tenant_id = get_current_tenant()
            for value_dict in insert_context.values:
                value_dict['tenant_id'] = tenant_id
    
    @event.listens_for(Session, "before_bulk_update")
    def receive_before_bulk_update(update_context):
        """Add tenant_id filter to bulk updates"""
        if hasattr(update_context.mapper.class_, 'tenant_id'):
            tenant_id = get_current_tenant()
            update_context.whereclause = update_context.whereclause.where(
                update_context.mapper.class_.tenant_id == tenant_id
            )
    
    @event.listens_for(Session, "before_bulk_delete")
    def receive_before_bulk_delete(delete_context):
        """Add tenant_id filter to bulk deletes"""
        if hasattr(delete_context.mapper.class_, 'tenant_id'):
            tenant_id = get_current_tenant()
            delete_context.whereclause = delete_context.whereclause.where(
                delete_context.mapper.class_.tenant_id == tenant_id
            )

def create_tenant_aware_session(session: AsyncSession) -> TenantAwareSession:
    """Create a tenant-aware session wrapper"""
    return TenantAwareSession(session)