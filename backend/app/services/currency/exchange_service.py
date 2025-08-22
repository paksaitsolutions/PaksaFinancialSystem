"""Currency exchange rate service for handling multi-currency support."""
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
import logging
import json
import os
from functools import lru_cache

import httpx
from fastapi import HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.currency_models import ExchangeRate, Currency
from app.schemas.currency_schemas import ExchangeRateCreate, ExchangeRateUpdate

logger = logging.getLogger(__name__)

class ExchangeRateResult(BaseModel):
    """Result of an exchange rate lookup."""
    from_currency: str
    to_currency: str
    rate: Decimal
    date: datetime
    source: str
    is_reversed: bool = False

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }

class ExchangeService:
    """Service for handling currency exchange operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.base_currency = settings.BASE_CURRENCY
        self.providers = {
            'openexchangerates': self._get_openexchangerates_rate,
            'ecb': self._get_ecb_rate,
            'fixer': self._get_fixer_rate,
            'fallback': self._get_fallback_rate
        }
        self.active_providers = settings.EXCHANGE_RATE_PROVIDERS
        
    async def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None,
        force_refresh: bool = False
    ) -> ExchangeRateResult:
        """
        Get the exchange rate between two currencies.
        
        Args:
            from_currency: ISO 4217 currency code (e.g., 'USD', 'EUR')
            to_currency: ISO 4217 currency code
            date: Date for historical rate (defaults to current date)
            force_refresh: If True, bypass cache and fetch fresh rates
            
        Returns:
            ExchangeRateResult with rate information
            
        Raises:
            HTTPException: If rate cannot be determined
        """
        # Normalize currency codes
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Handle same currency case
        if from_currency == to_currency:
            return ExchangeRateResult(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=Decimal('1.0'),
                date=date or datetime.utcnow(),
                source='1:1',
                is_reversed=False
            )
        
        # Check cache first if not forcing refresh
        if not force_refresh:
            cached_rate = self._get_cached_rate(from_currency, to_currency, date)
            if cached_rate:
                logger.debug(f"Using cached rate: {cached_rate}")
                return cached_rate
        
        # Try to get rate from active providers
        for provider in self.active_providers:
            try:
                rate_result = await self.providers[provider](from_currency, to_currency, date)
                if rate_result:
                    # Cache the result
                    self._cache_rate(rate_result)
                    return rate_result
            except Exception as e:
                logger.warning(f"Failed to get rate from {provider}: {str(e)}")
                continue
        
        # If all else fails, try to calculate via base currency
        if from_currency != self.base_currency and to_currency != self.base_currency:
            try:
                rate1 = await self.get_rate(from_currency, self.base_currency, date, force_refresh)
                rate2 = await self.get_rate(self.base_currency, to_currency, date, force_refresh)
                
                calculated_rate = rate1.rate * rate2.rate
                
                result = ExchangeRateResult(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=calculated_rate.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP),
                    date=rate1.date,
                    source=f"calculated_via_{self.base_currency}",
                    is_reversed=False
                )
                
                # Cache the calculated rate
                self._cache_rate(result)
                return result
                
            except Exception as e:
                logger.error(f"Failed to calculate cross rate via {self.base_currency}: {str(e)}")
        
        raise HTTPException(
            status_code=400,
            detail=f"Could not determine exchange rate from {from_currency} to {to_currency}"
        )
    
    async def convert_amount(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None,
        force_refresh: bool = False
    ) -> Tuple[Decimal, ExchangeRateResult]:
        """
        Convert an amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            date: Date for historical rate
            force_refresh: If True, bypass cache and fetch fresh rates
            
        Returns:
            Tuple of (converted_amount, exchange_rate_result)
        """
        if from_currency == to_currency:
            rate_result = ExchangeRateResult(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=Decimal('1.0'),
                date=date or datetime.utcnow(),
                source='1:1',
                is_reversed=False
            )
            return amount, rate_result
            
        rate_result = await self.get_rate(from_currency, to_currency, date, force_refresh)
        converted = (amount * rate_result.rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return converted, rate_result
    
    async def get_historical_rates(
        self,
        base_currency: str,
        target_currencies: List[str],
        start_date: datetime,
        end_date: Optional[datetime] = None,
        frequency: str = 'daily'
    ) -> Dict[str, Dict[datetime, Decimal]]:
        """
        Get historical exchange rates for multiple currencies over a date range.
        
        Args:
            base_currency: Base currency code
            target_currencies: List of target currency codes
            start_date: Start date for historical data
            end_date: End date (defaults to today)
            frequency: One of 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
            
        Returns:
            Dict mapping currency codes to dicts of date: rate
        """
        # Implementation for historical rates
        pass
    
    # --- Provider Implementations ---
    
    async def _get_openexchangerates_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None
    ) -> Optional[ExchangeRateResult]:
        """Get exchange rate from Open Exchange Rates API."""
        if not settings.OPENEXCHANGERATES_APP_ID:
            return None
            
        base_url = "https://openexchangerates.org/api/"
        endpoint = "latest.json"
        params = {
            "app_id": settings.OPENEXCHANGERATES_APP_ID,
            "base": from_currency,
            "symbols": to_currency
        }
        
        if date:
            endpoint = f"historical/{date.strftime('%Y-%m-%d')}.json"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}{endpoint}", params=params)
                response.raise_for_status()
                data = response.json()
                
                rate_date = datetime.fromtimestamp(data['timestamp'])
                rate = Decimal(str(data['rates'][to_currency]))
                
                return ExchangeRateResult(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate,
                    date=rate_date,
                    source='openexchangerates',
                    is_reversed=False
                )
                
        except Exception as e:
            logger.error(f"OpenExchangeRates API error: {str(e)}")
            return None
    
    async def _get_ecb_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None
    ) -> Optional[ExchangeRateResult]:
        """Get exchange rate from European Central Bank."""
        # ECB only provides rates against EUR
        if from_currency != 'EUR' and to_currency != 'EUR':
            return None
            
        is_reversed = from_currency == 'EUR'
        base_currency = to_currency if is_reversed else from_currency
        
        try:
            # For ECB, we'll use a static file that's updated daily
            # In production, you'd want to implement proper ECB API integration
            ecb_rates = self._load_ecb_rates()
            
            if not ecb_rates:
                return None
                
            # Find the most recent rate on or before the requested date
            rate_date = (date or datetime.utcnow()).date()
            
            # Find the latest rate for the currency pair
            rate = None
            for entry in sorted(ecb_rates, key=lambda x: x['date'], reverse=True):
                if entry['date'] > rate_date:
                    continue
                    
                if base_currency in entry['rates']:
                    rate = entry['rates'][base_currency]
                    if is_reversed:
                        rate = Decimal('1') / rate
                    rate_date = entry['date']
                    break
            
            if not rate:
                return None
                
            return ExchangeRateResult(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=rate,
                date=datetime.combine(rate_date, datetime.min.time()),
                source='ecb',
                is_reversed=is_reversed
            )
            
        except Exception as e:
            logger.error(f"ECB rate lookup error: {str(e)}")
            return None
    
    async def _get_fixer_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None
    ) -> Optional[ExchangeRateResult]:
        """Get exchange rate from Fixer.io API."""
        if not settings.FIXER_API_KEY:
            return None
            
        base_url = "http://data.fixer.io/api/"
        endpoint = "latest"
        
        params = {
            "access_key": settings.FIXER_API_KEY,
            "base": from_currency,
            "symbols": to_currency
        }
        
        if date:
            endpoint = date.strftime("%Y-%m-%d")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}{endpoint}", params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('success', False):
                    logger.error(f"Fixer API error: {data.get('error', {}).get('info', 'Unknown error')}")
                    return None
                
                rate_date = datetime.fromtimestamp(data['timestamp'])
                rate = Decimal(str(data['rates'][to_currency]))
                
                return ExchangeRateResult(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate,
                    date=rate_date,
                    source='fixer',
                    is_reversed=False
                )
                
        except Exception as e:
            logger.error(f"Fixer API error: {str(e)}")
            return None
    
    async def _get_fallback_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None
    ) -> Optional[ExchangeRateResult]:
        """Fallback method to get exchange rate from database."""
        try:
            # Try to get rate from database
            query = self.db.query(ExchangeRate).filter(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency,
                ExchangeRate.is_active == True
            )
            
            if date:
                query = query.filter(ExchangeRate.effective_date <= date)
            
            rate = query.order_by(ExchangeRate.effective_date.desc()).first()
            
            if rate:
                return ExchangeRateResult(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate.rate,
                    date=rate.effective_date,
                    source=rate.source or 'database',
                    is_reversed=False
                )
                
            # Try the reverse rate
            reverse_rate = self.db.query(ExchangeRate).filter(
                ExchangeRate.from_currency == to_currency,
                ExchangeRate.to_currency == from_currency,
                ExchangeRate.is_active == True
            )
            
            if date:
                reverse_rate = reverse_rate.filter(ExchangeRate.effective_date <= date)
            
            reverse_rate = reverse_rate.order_by(ExchangeRate.effective_date.desc()).first()
            
            if reverse_rate:
                return ExchangeRateResult(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=Decimal('1') / reverse_rate.rate,
                    date=reverse_rate.effective_date,
                    source=f"1/{reverse_rate.source or 'database'}",
                    is_reversed=True
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Database rate lookup error: {str(e)}")
            return None
    
    # --- Helper Methods ---
    
    def _get_cached_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None
    ) -> Optional[ExchangeRateResult]:
        """Get exchange rate from cache."""
        # This is a simplified implementation
        # In production, you'd use Redis or similar
        try:
            cache_key = f"rate:{from_currency}:{to_currency}:{date.date() if date else 'latest'}"
            # Implement actual caching logic here
            return None
        except Exception as e:
            logger.warning(f"Cache lookup error: {str(e)}")
            return None
    
    def _cache_rate(self, rate_result: ExchangeRateResult) -> None:
        """Cache an exchange rate result."""
        # This is a simplified implementation
        # In production, you'd use Redis or similar with appropriate TTL
        try:
            cache_key = f"rate:{rate_result.from_currency}:{rate_result.to_currency}:{rate_result.date.date()}"
            # Implement actual caching logic here
            pass
        except Exception as e:
            logger.warning(f"Cache store error: {str(e)}")
    
    def _load_ecb_rates(self) -> List[Dict]:
        """Load ECB rates from a static file or database."""
        # In production, implement proper ECB API integration
        # This is just a placeholder with sample data
        return [
            {
                'date': datetime.utcnow().date(),
                'base': 'EUR',
                'rates': {
                    'USD': Decimal('1.18'),
                    'GBP': Decimal('0.85'),
                    'JPY': Decimal('130.5'),
                    # Add more currencies as needed
                }
            }
        ]

# Singleton instance for dependency injection
def get_exchange_service(db: Session) -> ExchangeService:
    """Get an instance of the exchange service."""
    return ExchangeService(db)
