from typing import Any, Optional
from app.core.db.tenant_middleware import get_current_tenant
import json

class TenantAwareCache:
    def __init__(self):
        self._cache = {}
    
    def _get_tenant_key(self, key: str) -> str:
        tenant_id = get_current_tenant()
        return f"tenant:{tenant_id}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        tenant_key = self._get_tenant_key(key)
        return self._cache.get(tenant_key)
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        tenant_key = self._get_tenant_key(key)
        self._cache[tenant_key] = value
    
    async def delete(self, key: str):
        tenant_key = self._get_tenant_key(key)
        self._cache.pop(tenant_key, None)
    
    async def clear_tenant_cache(self, tenant_id: str = None):
        if not tenant_id:
            tenant_id = get_current_tenant()
        pattern = f"tenant:{tenant_id}:"
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(pattern)]
        for key in keys_to_delete:
            del self._cache[key]

tenant_cache = TenantAwareCache()