"""
Tax service integrations.
"""
import httpx
from typing import Dict, List, Any, Optional
from decimal import Decimal

from app.core.config import settings
from app.core.logging import logger

class AvalaraIntegration:
    """Avalara tax service integration."""
    
    def __init__(self):
        self.base_url = "https://rest.avatax.com"
        self.account_id = settings.AVALARA_ACCOUNT_ID
        self.license_key = settings.AVALARA_LICENSE_KEY
    
    async def calculate_tax(
        self, 
        amount: Decimal,
        from_address: Dict[str, str],
        to_address: Dict[str, str],
        tax_code: str = "P0000000"
    ) -> Dict[str, Any]:
        """Calculate tax for transaction."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v2/transactions/create",
                json={
                    "type": "SalesInvoice",
                    "companyCode": "DEFAULT",
                    "date": "2024-01-01",
                    "customerCode": "CUSTOMER",
                    "addresses": {
                        "ShipFrom": from_address,
                        "ShipTo": to_address
                    },
                    "lines": [{
                        "number": "1",
                        "amount": float(amount),
                        "taxCode": tax_code
                    }]
                },
                auth=(f"{self.account_id}:{self.license_key}", "")
            )
            return response.json()
    
    async def validate_address(self, address: Dict[str, str]) -> Dict[str, Any]:
        """Validate address."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v2/addresses/resolve",
                json=address,
                auth=(f"{self.account_id}:{self.license_key}", "")
            )
            return response.json()

class TaxJarIntegration:
    """TaxJar tax service integration."""
    
    def __init__(self):
        self.base_url = "https://api.taxjar.com/v2"
        self.api_token = settings.TAXJAR_API_TOKEN
    
    async def calculate_tax(
        self,
        amount: Decimal,
        from_zip: str,
        to_zip: str,
        from_state: str,
        to_state: str
    ) -> Dict[str, Any]:
        """Calculate tax using TaxJar."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/taxes",
                json={
                    "from_country": "US",
                    "from_zip": from_zip,
                    "from_state": from_state,
                    "to_country": "US",
                    "to_zip": to_zip,
                    "to_state": to_state,
                    "amount": float(amount),
                    "shipping": 0
                },
                headers={"Authorization": f"Token token={self.api_token}"}
            )
            return response.json()
    
    async def get_tax_rates(self, zip_code: str) -> Dict[str, Any]:
        """Get tax rates for location."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/rates/{zip_code}",
                headers={"Authorization": f"Token token={self.api_token}"}
            )
            return response.json()

class TaxServiceManager:
    """Manage tax service integrations."""
    
    def __init__(self):
        self.avalara = AvalaraIntegration()
        self.taxjar = TaxJarIntegration()
    
    async def calculate_tax(
        self, 
        service: str,
        amount: Decimal,
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate tax using specified service."""
        if service == "avalara":
            return await self.avalara.calculate_tax(amount, **kwargs)
        elif service == "taxjar":
            return await self.taxjar.calculate_tax(amount, **kwargs)
        else:
            raise ValueError(f"Unsupported tax service: {service}")

tax_service = TaxServiceManager()