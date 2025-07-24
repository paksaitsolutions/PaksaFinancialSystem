"""
Payment gateway integrations.
"""
import httpx
import stripe
from typing import Dict, Any, Optional
from decimal import Decimal

from app.core.config import settings
from app.core.logging import logger

class StripeIntegration:
    """Stripe payment gateway integration."""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    
    async def create_payment_intent(
        self, 
        amount: Decimal, 
        currency: str = "usd",
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create payment intent."""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                customer=customer_id,
                automatic_payment_methods={"enabled": True}
            )
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "status": intent.status
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise
    
    async def create_customer(self, email: str, name: str) -> str:
        """Create Stripe customer."""
        customer = stripe.Customer.create(email=email, name=name)
        return customer.id
    
    async def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm payment intent."""
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return {
            "status": intent.status,
            "amount": intent.amount / 100,
            "currency": intent.currency
        }

class PayPalIntegration:
    """PayPal payment gateway integration."""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.base_url = "https://api.paypal.com"
        self._access_token = None
    
    async def _get_access_token(self) -> str:
        """Get PayPal access token."""
        if self._access_token:
            return self._access_token
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                data="grant_type=client_credentials",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                auth=(self.client_id, self.client_secret)
            )
            self._access_token = response.json()["access_token"]
            return self._access_token
    
    async def create_order(self, amount: Decimal, currency: str = "USD") -> Dict[str, Any]:
        """Create PayPal order."""
        token = await self._get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders",
                json={
                    "intent": "CAPTURE",
                    "purchase_units": [{
                        "amount": {
                            "currency_code": currency,
                            "value": str(amount)
                        }
                    }]
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.json()
    
    async def capture_order(self, order_id: str) -> Dict[str, Any]:
        """Capture PayPal order."""
        token = await self._get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.json()

class PaymentGatewayManager:
    """Manage multiple payment gateways."""
    
    def __init__(self):
        self.stripe = StripeIntegration()
        self.paypal = PayPalIntegration()
    
    async def process_payment(
        self, 
        gateway: str, 
        amount: Decimal, 
        currency: str = "USD",
        **kwargs
    ) -> Dict[str, Any]:
        """Process payment through specified gateway."""
        if gateway == "stripe":
            return await self.stripe.create_payment_intent(amount, currency, **kwargs)
        elif gateway == "paypal":
            return await self.paypal.create_order(amount, currency)
        else:
            raise ValueError(f"Unsupported payment gateway: {gateway}")

payment_manager = PaymentGatewayManager()