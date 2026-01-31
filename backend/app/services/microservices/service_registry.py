"""
Microservices service registry and discovery.
"""
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

import httpx

from app.core.logging import logger


# from app.core.cache import cache_manager

class ServiceRegistry:
    """Service registry for microservices discovery."""
    
    def __init__(self):
        self.services: Dict[str, Dict] = {}
        self.running = False
    
    async def register_service(self, service_name: str, service_url: str, health_check_url: str):
        service_info = {
            "name": service_name,
            "url": service_url,
            "health_check_url": health_check_url,
            "status": "healthy",
            "last_health_check": datetime.utcnow(),
            "registered_at": datetime.utcnow()
        }
        
        self.services[service_name] = service_info
        # await cache_manager.set(f"service:{service_name}", service_info, ttl=300)
        logger.info(f"Registered service: {service_name} at {service_url}")
    
    async def get_service(self, service_name: str) -> Optional[Dict]:
        # service_info = await cache_manager.get(f"service:{service_name}")
        # if service_info:
        #     return service_info
        return self.services.get(service_name)
    
    async def start_health_checks(self):
        self.running = True
        while self.running:
            await self._perform_health_checks()
            await asyncio.sleep(30)
    
    async def _perform_health_checks(self):
        for service_name, service_info in self.services.items():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(service_info["health_check_url"])
                    service_info["status"] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                service_info["status"] = "unhealthy"
            
            service_info["last_health_check"] = datetime.utcnow()
            # await cache_manager.set(f"service:{service_name}", service_info, ttl=300)

class ServiceClient:
    """Client for making requests to microservices."""
    
    def __init__(self, service_registry: ServiceRegistry):
        self.registry = service_registry
    
    async def call_service(self, service_name: str, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
        service_info = await self.registry.get_service(service_name)
        
        if not service_info or service_info["status"] != "healthy":
            return None
        
        url = f"{service_info['url']}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                else:
                    return None
                
                response.raise_for_status()
                return response.json()
        except Exception:
            return None

service_registry = ServiceRegistry()
service_client = ServiceClient(service_registry)