from fastapi import Request, HTTPException
from app.core.db.tenant_middleware import get_current_tenant
from app.core.cache.tenant_cache import tenant_cache
from datetime import datetime, timedelta
import uuid
import json

class TenantSessionManager:
    def __init__(self):
        self.session_timeout = 3600  # 1 hour default
        self.max_sessions_per_user = 5
    
    async def create_session(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str,
        tenant_id: str = None
    ) -> str:
        """Create a new tenant-isolated session"""
        if not tenant_id:
            tenant_id = get_current_tenant()
        
        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat()
        }
        
        # Store session with tenant isolation
        session_key = f"session:{session_id}"
        await tenant_cache.set(session_key, json.dumps(session_data), expire=self.session_timeout)
        
        # Track user sessions
        user_sessions_key = f"user_sessions:{user_id}"
        user_sessions = await tenant_cache.get(user_sessions_key) or []
        user_sessions.append(session_id)
        
        # Limit concurrent sessions
        if len(user_sessions) > self.max_sessions_per_user:
            # Remove oldest session
            oldest_session = user_sessions.pop(0)
            await self.invalidate_session(oldest_session)
        
        await tenant_cache.set(user_sessions_key, user_sessions, expire=self.session_timeout)
        
        return session_id
    
    async def validate_session(self, session_id: str, request: Request) -> dict:
        """Validate session and ensure tenant isolation"""
        session_key = f"session:{session_id}"
        session_data_str = await tenant_cache.get(session_key)
        
        if not session_data_str:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        session_data = json.loads(session_data_str)
        
        # Validate tenant context
        current_tenant = get_current_tenant()
        if session_data['tenant_id'] != current_tenant:
            raise HTTPException(status_code=403, detail="Session tenant mismatch")
        
        # Validate IP address (optional security check)
        if session_data['ip_address'] != request.client.host:
            # Log suspicious activity but don't block (IP can change)
            pass
        
        # Update last activity
        session_data['last_activity'] = datetime.utcnow().isoformat()
        await tenant_cache.set(session_key, json.dumps(session_data), expire=self.session_timeout)
        
        return session_data
    
    async def invalidate_session(self, session_id: str):
        """Invalidate a specific session"""
        session_key = f"session:{session_id}"
        await tenant_cache.delete(session_key)
    
    async def invalidate_user_sessions(self, user_id: str):
        """Invalidate all sessions for a user"""
        user_sessions_key = f"user_sessions:{user_id}"
        user_sessions = await tenant_cache.get(user_sessions_key) or []
        
        for session_id in user_sessions:
            await self.invalidate_session(session_id)
        
        await tenant_cache.delete(user_sessions_key)
    
    async def get_active_sessions(self, user_id: str) -> list:
        """Get active sessions for a user"""
        user_sessions_key = f"user_sessions:{user_id}"
        session_ids = await tenant_cache.get(user_sessions_key) or []
        
        active_sessions = []
        for session_id in session_ids:
            session_key = f"session:{session_id}"
            session_data_str = await tenant_cache.get(session_key)
            if session_data_str:
                active_sessions.append(json.loads(session_data_str))
        
        return active_sessions

# Global session manager
tenant_session_manager = TenantSessionManager()

async def require_valid_session(request: Request, session_id: str):
    """Dependency to require valid tenant session"""
    return await tenant_session_manager.validate_session(session_id, request)