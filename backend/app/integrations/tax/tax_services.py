"""
Tax service integrations.
"""
from typing import Dict, Any, Optional
from decimal import Decimal

from app.core.config import settings
from app.core.logging import logger

# Try to import httpx, but make it optional
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

class TaxService:
    """Tax calculation service integration."""
    
    def __init__(self):
        self.api_key = getattr(settings, 'TAX_SERVICE_API_KEY', '')
        self.base_url = "https://api.taxservice.com"
    
    async def calculate_tax(
        self, 
        amount: Decimal, 
        tax_jurisdiction: str,
        item_type: str = "general"
    ) -> Dict[str, Any]:
        """Calculate tax for given amount and jurisdiction."""
        if not HTTPX_AVAILABLE:
            # Return mock tax calculation
            tax_rate = Decimal('0.08')  # 8% default
            tax_amount = amount * tax_rate
            return {
                "tax_rate": float(tax_rate),
                "tax_amount": float(tax_amount),
                "total_amount": float(amount + tax_amount),
                "jurisdiction": tax_jurisdiction,
                "mock": True
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/calculate",
                    json={
                        "amount": str(amount),
                        "jurisdiction": tax_jurisdiction,
                        "item_type": item_type
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.json()
        except Exception as e:
            logger.error(f"Error calculating tax: {e}")
            # Return fallback calculation
            tax_rate = Decimal('0.08')
            tax_amount = amount * tax_rate
            return {
                "tax_rate": float(tax_rate),
                "tax_amount": float(tax_amount),
                "total_amount": float(amount + tax_amount),
                "jurisdiction": tax_jurisdiction,
                "error": str(e)
            }
    
    async def validate_tax_id(self, tax_id: str, jurisdiction: str) -> Dict[str, Any]:
        """Validate tax ID."""
        if not HTTPX_AVAILABLE:
            return {"valid": True, "mock": True}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/validate",
                    json={
                        "tax_id": tax_id,
                        "jurisdiction": jurisdiction
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.json()
        except Exception as e:
            logger.error(f"Error validating tax ID: {e}")
            return {"valid": False, "error": str(e)}

tax_service = TaxService()