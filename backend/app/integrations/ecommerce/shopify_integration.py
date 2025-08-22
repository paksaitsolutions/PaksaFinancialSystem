"""
E-commerce platform integrations.
"""
import httpx
from typing import Dict, List, Any
from app.core.logging import logger

class ShopifyIntegration:
    """Shopify e-commerce integration."""
    
    def __init__(self, shop_domain: str, access_token: str):
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.base_url = f"https://{shop_domain}.myshopify.com/admin/api/2023-10"
    
    async def get_orders(self, status: str = "any", limit: int = 50) -> List[Dict[str, Any]]:
        """Get orders from Shopify."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/orders.json",
                params={"status": status, "limit": limit},
                headers={"X-Shopify-Access-Token": self.access_token}
            )
            return response.json().get("orders", [])
    
    async def sync_inventory(self, inventory_items: List[Dict[str, Any]]) -> bool:
        """Sync inventory levels to Shopify."""
        try:
            for item in inventory_items:
                async with httpx.AsyncClient() as client:
                    await client.put(
                        f"{self.base_url}/inventory_levels/set.json",
                        json={
                            "location_id": item["location_id"],
                            "inventory_item_id": item["inventory_item_id"],
                            "available": item["quantity"]
                        },
                        headers={"X-Shopify-Access-Token": self.access_token}
                    )
            return True
        except Exception as e:
            logger.error(f"Shopify inventory sync failed: {str(e)}")
            return False