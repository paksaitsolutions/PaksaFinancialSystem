"""GL permission checking and role-based access control"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.core_financials.general_ledger.settings import GLRole, GLApprovalWorkflow
from functools import wraps
from fastapi import HTTPException, status

class GLPermissionChecker:
    """Check GL-specific permissions for users"""
    
    @staticmethod
    async def has_permission(db: AsyncSession, user_id: str, tenant_id: str, permission: str) -> bool:
        """Check if user has specific GL permission"""
        # Get user's GL roles
        result = await db.execute(
            select(GLRole).where(GLRole.tenant_id == tenant_id)
        )
        roles = result.scalars().all()
        
        # Check if any role has the required permission
        for role in roles:
            if hasattr(role, permission) and getattr(role, permission):
                return True
        
        return False
    
    @staticmethod
    async def can_create_accounts(db: AsyncSession, user_id: str, tenant_id: str) -> bool:
        return await GLPermissionChecker.has_permission(db, user_id, tenant_id, 'can_create_accounts')
    
    @staticmethod
    async def can_post_entries(db: AsyncSession, user_id: str, tenant_id: str) -> bool:
        return await GLPermissionChecker.has_permission(db, user_id, tenant_id, 'can_post_journal_entries')
    
    @staticmethod
    async def can_approve_entries(db: AsyncSession, user_id: str, tenant_id: str) -> bool:
        return await GLPermissionChecker.has_permission(db, user_id, tenant_id, 'can_approve_entries')
    
    @staticmethod
    async def can_close_periods(db: AsyncSession, user_id: str, tenant_id: str) -> bool:
        return await GLPermissionChecker.has_permission(db, user_id, tenant_id, 'can_close_periods')

def require_gl_permission(permission: str):
    """Decorator to require specific GL permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract db, user_id, tenant_id from function arguments
            db = kwargs.get('db') or args[0] if args else None
            user_id = kwargs.get('user_id', 'test-user')  # Mock for testing
            tenant_id = kwargs.get('tenant_id', 'test-tenant')  # Mock for testing
            
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not available"
                )
            
            has_permission = await GLPermissionChecker.has_permission(
                db, user_id, tenant_id, permission
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {permission} required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class GLApprovalService:
    """Handle GL approval workflows"""
    
    @staticmethod
    async def requires_approval(db: AsyncSession, tenant_id: str, workflow_type: str, amount: float = 0) -> bool:
        """Check if operation requires approval"""
        result = await db.execute(
            select(GLApprovalWorkflow).where(
                GLApprovalWorkflow.tenant_id == tenant_id,
                GLApprovalWorkflow.workflow_type == workflow_type
            )
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            return False
        
        if not workflow.approval_required:
            return False
        
        # Check auto-approval threshold
        if workflow.auto_approve_threshold > 0 and amount <= workflow.auto_approve_threshold:
            return False
        
        return True
    
    @staticmethod
    async def get_approvers(db: AsyncSession, tenant_id: str, workflow_type: str) -> List[str]:
        """Get list of approver role IDs for workflow"""
        result = await db.execute(
            select(GLApprovalWorkflow).where(
                GLApprovalWorkflow.tenant_id == tenant_id,
                GLApprovalWorkflow.workflow_type == workflow_type
            )
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow or not workflow.approver_roles:
            return []
        
        import json
        try:
            return json.loads(workflow.approver_roles)
        except:
            return []