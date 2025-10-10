"""
Currency and Exchange Rate models for multi-currency support.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Numeric, Date, DateTime, ForeignKey, 
    Enum as SQLEnum, Boolean, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel, GUID


class CurrencyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Currency(BaseModel):
    """
    Represents a currency in the system.
    """
    __tablename__ = "currencies"
    
    # ISO 4217 currency code (e.g., USD, EUR, PKR)
    code = Column(String(3), unique=True, index=True, nullable=False)
    
    # Currency name (e.g., US Dollar, Euro, Pakistani Rupee)
    name = Column(String(100), nullable=False)
    
    # Symbol (e.g., $, €, ₨)
    symbol = Column(String(10), nullable=True)
    
    # Number of decimal places (e.g., 2 for USD, 0 for JPY)
    decimal_places = Column(Numeric(1, 0), nullable=False, default=2)
    
    # Status (active/inactive)
    status = Column(SQLEnum(CurrencyStatus), nullable=False, default=CurrencyStatus.ACTIVE)
    
    # Is this the base currency for the organization?
    is_base_currency = Column(Boolean, default=False, nullable=False)
    
    # Exchange rate entries where this is the target currency
    exchange_rates = relationship(
        "ExchangeRate", 
        foreign_keys="[ExchangeRate.target_currency_id]",
        back_populates="target_currency"
    )
    
    # Exchange rate entries where this is the source currency
    source_exchange_rates = relationship(
        "ExchangeRate",
        foreign_keys="[ExchangeRate.source_currency_id]",
        back_populates="source_currency"
    )
    
    # GL accounts using this currency
    gl_accounts = relationship("GLChartOfAccounts", back_populates="currency")
    
    __table_args__ = (
        CheckConstraint("LENGTH(code) = 3", name="ck_currency_code_length"),
        CheckConstraint("decimal_places >= 0", name="ck_currency_decimal_places_positive"),
        UniqueConstraint('code', name='uq_currencies_code'),
        {'extend_existing': True}
    )
    
    def __repr__(self) -> str:
        return f"<Currency(id={self.id}, code='{self.code}', name='{self.name}')>"


class ExchangeRateType(str, Enum):
    SPOT = "spot"
    FORWARD = "forward"
    HISTORICAL = "historical"


class ExchangeRate(BaseModel):
    """
    Represents an exchange rate between two currencies.
    """
    __tablename__ = "exchange_rates"
    # Source and target currencies
    source_currency_id = Column(GUID(), ForeignKey("currencies.id"), nullable=False)
    target_currency_id = Column(GUID(), ForeignKey("currencies.id"), nullable=False)
    
    # Exchange rate (1 source_currency = rate target_currency)
    rate = Column(Numeric(20, 10), nullable=False)
    
    # Date for which this rate is valid
    effective_date = Column(Date, nullable=False, index=True)
    
    # Type of exchange rate
    rate_type = Column(SQLEnum(ExchangeRateType), nullable=False, default=ExchangeRateType.SPOT)
    
    # Is this the official rate?
    is_official = Column(Boolean, default=False, nullable=False)
    
    # Source of the rate (e.g., "ECB", "OANDA", "Manual")
    source = Column(String(50), nullable=True)
    
    # Relationships
    source_currency = relationship(
        "Currency", 
        foreign_keys=[source_currency_id],
        back_populates="source_exchange_rates"
    )
    
    target_currency = relationship(
        "Currency", 
        foreign_keys=[target_currency_id],
        back_populates="exchange_rates"
    )
    
    __table_args__ = (
        UniqueConstraint(
            'source_currency_id', 
            'target_currency_id', 
            'effective_date',
            'rate_type',
            name='uq_exchange_rates_unique_rate'
        ),
        CheckConstraint("rate > 0", name="ck_exchange_rate_positive"),
        CheckConstraint("source_currency_id != target_currency_id", 
                      name="ck_exchange_rate_different_currencies"),
        {'extend_existing': True}
    )
    
    @classmethod
    async def get_rate(
        cls, 
        db, 
        source_currency_id: UUID, 
        target_currency_id: UUID, 
        date: date = None,
        rate_type: ExchangeRateType = ExchangeRateType.SPOT
    ) -> Optional[Decimal]:
        """
        Get the exchange rate between two currencies on a specific date.
        
        Args:
            db: Database session
            source_currency_id: Source currency ID
            target_currency_id: Target currency ID
            date: Date for the rate (defaults to today)
            rate_type: Type of rate to retrieve
            
        Returns:
            The exchange rate or None if not found
        """
        from sqlalchemy import select, and_, or_
        
        if date is None:
            date = date.today()
            
        if source_currency_id == target_currency_id:
            return Decimal('1.0')
            
        # Try to find the most specific rate first
        stmt = (
            select(cls)
            .where(
                and_(
                    cls.source_currency_id == source_currency_id,
                    cls.target_currency_id == target_currency_id,
                    cls.effective_date <= date,
                    cls.rate_type == rate_type,
                )
            )
            .order_by(cls.effective_date.desc())
            .limit(1)
        )
        
        result = await db.execute(stmt)
        rate = result.scalars().first()
        
        if rate:
            return rate.rate
            
        # If no direct rate found, try to find a path through the base currency
        base_currency = await db.execute(
            select(Currency)
            .where(Currency.is_base_currency == True)
            .limit(1)
        )
        base_currency = base_currency.scalars().first()
        
        if not base_currency:
            return None
            
        # Get rate from source to base
        source_to_base = await cls.get_rate(
            db, source_currency_id, base_currency.id, date, rate_type
        )
        
        if not source_to_base:
            return None
            
        # Get rate from base to target
        base_to_target = await cls.get_rate(
            db, base_currency.id, target_currency_id, date, rate_type
        )
        
        if not base_to_target:
            return None
            
        # Calculate cross rate
        return source_to_base * base_to_target
    
    def __repr__(self) -> str:
        return (
            f"<ExchangeRate(id={self.id}, "
            f"{self.source_currency_id}->{self.target_currency_id} "
            f"{self.rate} on {self.effective_date})>"
        )
