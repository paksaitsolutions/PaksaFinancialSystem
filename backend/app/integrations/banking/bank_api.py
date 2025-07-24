"""
Banking API integrations.
"""
import httpx
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, date

from app.core.config import settings
from app.core.logging import logger

class BankAPIClient:
    """Generic bank API client."""
    
    def __init__(self, bank_config: Dict[str, Any]):
        self.base_url = bank_config.get("base_url")
        self.api_key = bank_config.get("api_key")
        self.client_id = bank_config.get("client_id")
        self.client_secret = bank_config.get("client_secret")
        
    async def get_account_balance(self, account_id: str) -> Dict[str, Any]:
        """Get account balance."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/accounts/{account_id}/balance",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()
    
    async def get_transactions(
        self, 
        account_id: str, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Get account transactions."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/accounts/{account_id}/transactions",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json().get("transactions", [])
    
    async def initiate_transfer(
        self, 
        from_account: str, 
        to_account: str, 
        amount: Decimal,
        reference: str
    ) -> Dict[str, Any]:
        """Initiate bank transfer."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/transfers",
                json={
                    "from_account": from_account,
                    "to_account": to_account,
                    "amount": str(amount),
                    "reference": reference
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()

class PlaidIntegration:
    """Plaid banking integration."""
    
    def __init__(self):
        self.client_id = settings.PLAID_CLIENT_ID
        self.secret = settings.PLAID_SECRET
        self.base_url = "https://production.plaid.com"
    
    async def create_link_token(self, user_id: str) -> str:
        """Create Plaid Link token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/link/token/create",
                json={
                    "client_id": self.client_id,
                    "secret": self.secret,
                    "user": {"client_user_id": user_id},
                    "client_name": "Paksa Financial",
                    "products": ["transactions", "accounts"],
                    "country_codes": ["US"]
                }
            )
            return response.json()["link_token"]
    
    async def exchange_public_token(self, public_token: str) -> str:
        """Exchange public token for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/item/public_token/exchange",
                json={
                    "client_id": self.client_id,
                    "secret": self.secret,
                    "public_token": public_token
                }
            )
            return response.json()["access_token"]
    
    async def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """Get linked accounts."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/accounts/get",
                json={
                    "client_id": self.client_id,
                    "secret": self.secret,
                    "access_token": access_token
                }
            )
            return response.json()["accounts"]

plaid_client = PlaidIntegration()