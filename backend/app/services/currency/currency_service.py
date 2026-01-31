"""
Currency service for managing currencies and exchange rates.
"""
from datetime import date, datetime
from typing import List, Optional, Dict, Any

from decimal import Decimal
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.exceptions import NotFoundException, ValidationException
from app.models.currency import Currency, ExchangeRate, ExchangeRateType, CurrencyStatus





class CurrencyService:
    """Service for managing currencies and exchange rates."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def get_all_currencies(self, include_inactive: bool = False) -> List[Currency]:
        """Get All Currencies."""
        """
        Get all currencies.
        
        Args:
            include_inactive: Whether to include inactive currencies
            
        Returns:
            List of Currency objects
        """
        query = self.db.query(Currency)
        
        if not include_inactive:
            query = query.filter(Currency.status == CurrencyStatus.ACTIVE)
            
        return query.order_by(Currency.code).all()
    
    def get_currency_by_code(self, code: str) -> Optional[Currency]:
        """Get Currency By Code."""
        """
        Get a currency by its code.
        
        Args:
            code: ISO 4217 currency code (e.g., 'USD', 'EUR')
            
        Returns:
            Currency object or None if not found
        """
        return self.db.query(Currency).filter(Currency.code == code.upper()).first()
    
    def get_currency_by_id(self, currency_id: UUID) -> Optional[Currency]:
        """Get Currency By Id."""
        """
        Get a currency by its ID.
        
        Args:
            currency_id: Currency UUID
            
        Returns:
            Currency object or None if not found
        """
        return self.db.query(Currency).filter(Currency.id == currency_id).first()
    
    def get_base_currency(self) -> Optional[Currency]:
        """Get Base Currency."""
        """
        Get the base currency for the system.
        
        Returns:
            Base Currency object or None if not set
        """
        return self.db.query(Currency).filter(Currency.is_base_currency == True).first()
    
    def create_currency(self, currency_data: Dict[str, Any], created_by: UUID) -> Currency:
        """Create Currency."""
        """
        Create a new currency.
        
        Args:
            currency_data: Dictionary with currency data
            created_by: User ID who created the currency
            
        Returns:
            Created Currency object
            
        Raises:
            ValidationException: If currency code already exists
        """
        # Check if currency code already exists
        existing = self.get_currency_by_code(currency_data['code'])
        if existing:
            raise ValidationException(f"Currency with code {currency_data['code']} already exists")
        
        # Create new currency
        currency = Currency(
            code=currency_data['code'].upper(),
            name=currency_data['name'],
            symbol=currency_data.get('symbol'),
            decimal_places=currency_data.get('decimal_places', 2),
            status=CurrencyStatus(currency_data.get('status', CurrencyStatus.ACTIVE)),
            is_base_currency=currency_data.get('is_base_currency', False),
            created_by=created_by,
            updated_by=created_by
        )
        
        # If this is set as base currency, unset any existing base currency
        if currency.is_base_currency:
            self._unset_existing_base_currency()
        
        self.db.add(currency)
        self.db.commit()
        self.db.refresh(currency)
        
        return currency
    
    def update_currency(self, currency_id: UUID, currency_data: Dict[str, Any], updated_by: UUID) -> Currency:
        """Update Currency."""
        """
        Update an existing currency.
        
        Args:
            currency_id: Currency UUID
            currency_data: Dictionary with currency data
            updated_by: User ID who updated the currency
            
        Returns:
            Updated Currency object
            
        Raises:
            NotFoundException: If currency not found
            ValidationException: If currency code already exists
        """
        # Get existing currency
        currency = self.get_currency_by_id(currency_id)
        if not currency:
            raise NotFoundException(f"Currency with ID {currency_id} not found")
        
        # Check if code is being changed and if it already exists
        if 'code' in currency_data and currency_data['code'].upper() != currency.code:
            existing = self.get_currency_by_code(currency_data['code'])
            if existing:
                raise ValidationException(f"Currency with code {currency_data['code']} already exists")
            currency.code = currency_data['code'].upper()
        
        # Update fields
        if 'name' in currency_data:
            currency.name = currency_data['name']
        
        if 'symbol' in currency_data:
            currency.symbol = currency_data['symbol']
        
        if 'decimal_places' in currency_data:
            currency.decimal_places = currency_data['decimal_places']
        
        if 'status' in currency_data:
            currency.status = CurrencyStatus(currency_data['status'])
        
        if 'is_base_currency' in currency_data:
            # If setting as base currency, unset any existing base currency
            if currency_data['is_base_currency'] and not currency.is_base_currency:
                self._unset_existing_base_currency()
            currency.is_base_currency = currency_data['is_base_currency']
        
        currency.updated_by = updated_by
        currency.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(currency)
        
        return currency
    
    def delete_currency(self, currency_id: UUID) -> bool:
        """Delete Currency."""
        """
        Delete a currency.
        
        Args:
            currency_id: Currency UUID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValidationException: If currency is in use or is the base currency
        """
        currency = self.get_currency_by_id(currency_id)
        if not currency:
            return False
        
        # Check if currency is the base currency
        if currency.is_base_currency:
            raise ValidationException("Cannot delete the base currency")
        
        # Check if currency is in use
        # This would need to check all tables that reference currencies
        # For simplicity, we'll just check exchange rates
        exchange_rates = self.db.query(ExchangeRate).filter(
            or_(
                ExchangeRate.source_currency_id == currency_id,
                ExchangeRate.target_currency_id == currency_id
            )
        ).count()
        
        if exchange_rates > 0:
            raise ValidationException(f"Cannot delete currency {currency.code} as it is used in {exchange_rates} exchange rates")
        
        self.db.delete(currency)
        self.db.commit()
        
        return True
    
    def get_exchange_rate(
        self,
        source_currency_code: str,
        target_currency_code: str,
        rate_date: date = None,
        rate_type: ExchangeRateType = ExchangeRateType.SPOT
    ) -> Optional[Decimal]:
        """Get Exchange Rate."""
        """
        Get the exchange rate between two currencies.
        
        Args:
            source_currency_code: Source currency code
            target_currency_code: Target currency code
            rate_date: Date for the rate (defaults to today)
            rate_type: Type of rate to retrieve
            
        Returns:
            Exchange rate as Decimal or None if not found
        """
        if rate_date is None:
            rate_date = date.today()
            
        # If same currency, return 1.0
        if source_currency_code.upper() == target_currency_code.upper():
            return Decimal('1.0')
        
        # Get currency IDs
        source_currency = self.get_currency_by_code(source_currency_code)
        target_currency = self.get_currency_by_code(target_currency_code)
        
        if not source_currency or not target_currency:
            return None
        
        # Try to find direct rate
        exchange_rate = self.db.query(ExchangeRate).filter(
            and_(
                ExchangeRate.source_currency_id == source_currency.id,
                ExchangeRate.target_currency_id == target_currency.id,
                ExchangeRate.effective_date <= rate_date,
                ExchangeRate.rate_type == rate_type
            )
        ).order_by(desc(ExchangeRate.effective_date)).first()
        
        if exchange_rate:
            return exchange_rate.rate
        
        # Try reverse rate
        reverse_rate = self.db.query(ExchangeRate).filter(
            and_(
                ExchangeRate.source_currency_id == target_currency.id,
                ExchangeRate.target_currency_id == source_currency.id,
                ExchangeRate.effective_date <= rate_date,
                ExchangeRate.rate_type == rate_type
            )
        ).order_by(desc(ExchangeRate.effective_date)).first()
        
        if reverse_rate:
            return Decimal('1.0') / reverse_rate.rate
        
        # Try to find a path through the base currency
        base_currency = self.get_base_currency()
        if not base_currency:
            return None
        
        # Skip if either currency is already the base currency
        if source_currency.id == base_currency.id or target_currency.id == base_currency.id:
            return None
        
        # Get rate from source to base
        source_to_base = self.get_exchange_rate(
            source_currency.code,
            base_currency.code,
            rate_date,
            rate_type
        )
        
        if not source_to_base:
            return None
        
        # Get rate from base to target
        base_to_target = self.get_exchange_rate(
            base_currency.code,
            target_currency.code,
            rate_date,
            rate_type
        )
        
        if not base_to_target:
            return None
        
        # Calculate cross rate
        return source_to_base * base_to_target
    
    def create_exchange_rate(self, rate_data: Dict[str, Any], created_by: UUID) -> ExchangeRate:
        """Create Exchange Rate."""
        """
        Create a new exchange rate.
        
        Args:
            rate_data: Dictionary with exchange rate data
            created_by: User ID who created the rate
            
        Returns:
            Created ExchangeRate object
            
        Raises:
            ValidationException: If currencies not found or rate already exists
        """
        # Get currencies
        source_currency = self.get_currency_by_code(rate_data['source_currency_code'])
        target_currency = self.get_currency_by_code(rate_data['target_currency_code'])
        
        if not source_currency:
            raise ValidationException(f"Source currency {rate_data['source_currency_code']} not found")
        
        if not target_currency:
            raise ValidationException(f"Target currency {rate_data['target_currency_code']} not found")
        
        if source_currency.id == target_currency.id:
            raise ValidationException("Source and target currencies cannot be the same")
        
        # Check if rate already exists for the date
        existing = self.db.query(ExchangeRate).filter(
            and_(
                ExchangeRate.source_currency_id == source_currency.id,
                ExchangeRate.target_currency_id == target_currency.id,
                ExchangeRate.effective_date == rate_data['effective_date'],
                ExchangeRate.rate_type == ExchangeRateType(rate_data.get('rate_type', ExchangeRateType.SPOT))
            )
        ).first()
        
        if existing:
            raise ValidationException(f"Exchange rate already exists for {source_currency.code} to {target_currency.code} on {rate_data['effective_date']}")
        
        # Create new exchange rate
        exchange_rate = ExchangeRate(
            source_currency_id=source_currency.id,
            target_currency_id=target_currency.id,
            rate=Decimal(str(rate_data['rate'])),
            effective_date=rate_data['effective_date'],
            rate_type=ExchangeRateType(rate_data.get('rate_type', ExchangeRateType.SPOT)),
            is_official=rate_data.get('is_official', False),
            source=rate_data.get('source', 'Manual'),
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(exchange_rate)
        self.db.commit()
        self.db.refresh(exchange_rate)
        
        return exchange_rate
    
    def _unset_existing_base_currency(self) -> None:
        """ Unset Existing Base Currency."""
        """Unset any existing base currency."""
        base_currency = self.get_base_currency()
        if base_currency:
            base_currency.is_base_currency = False
            self.db.commit()