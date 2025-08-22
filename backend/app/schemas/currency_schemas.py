"""
Schemas for currency and exchange rate operations.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class CurrencyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ExchangeRateType(str, Enum):
    SPOT = "spot"
    FORWARD = "forward"
    HISTORICAL = "historical"


class CurrencyBase(BaseModel):
    """Base schema for currency operations."""
    code: str = Field(..., description="ISO 4217 currency code (e.g., USD, EUR)")
    name: str = Field(..., description="Currency name (e.g., US Dollar, Euro)")
    symbol: Optional[str] = Field(None, description="Currency symbol (e.g., $, €)")
    decimal_places: int = Field(2, description="Number of decimal places")
    status: CurrencyStatus = Field(CurrencyStatus.ACTIVE, description="Currency status")
    is_base_currency: bool = Field(False, description="Whether this is the base currency")

    @validator('code')
    def validate_code(cls, v):
        """Validate currency code."""
        if not v or len(v) != 3:
            raise ValueError("Currency code must be 3 characters")
        return v.upper()


class CurrencyCreate(CurrencyBase):
    """Schema for creating a new currency."""
    pass


class CurrencyUpdate(BaseModel):
    """Schema for updating an existing currency."""
    code: Optional[str] = Field(None, description="ISO 4217 currency code (e.g., USD, EUR)")
    name: Optional[str] = Field(None, description="Currency name (e.g., US Dollar, Euro)")
    symbol: Optional[str] = Field(None, description="Currency symbol (e.g., $, €)")
    decimal_places: Optional[int] = Field(None, description="Number of decimal places")
    status: Optional[CurrencyStatus] = Field(None, description="Currency status")
    is_base_currency: Optional[bool] = Field(None, description="Whether this is the base currency")

    @validator('code')
    def validate_code(cls, v):
        """Validate currency code."""
        if v is not None and len(v) != 3:
            raise ValueError("Currency code must be 3 characters")
        return v.upper() if v else v


class CurrencyResponse(CurrencyBase):
    """Schema for currency response."""
    id: UUID = Field(..., description="Currency ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class ExchangeRateBase(BaseModel):
    """Base schema for exchange rate operations."""
    source_currency_code: str = Field(..., description="Source currency code")
    target_currency_code: str = Field(..., description="Target currency code")
    rate: Decimal = Field(..., description="Exchange rate (1 source = rate target)")
    effective_date: date = Field(..., description="Date for which this rate is valid")
    rate_type: ExchangeRateType = Field(ExchangeRateType.SPOT, description="Type of exchange rate")
    is_official: bool = Field(False, description="Whether this is the official rate")
    source: Optional[str] = Field(None, description="Source of the rate (e.g., ECB, Manual)")

    @validator('source_currency_code', 'target_currency_code')
    def validate_currency_code(cls, v):
        """Validate currency code."""
        if not v or len(v) != 3:
            raise ValueError("Currency code must be 3 characters")
        return v.upper()

    @validator('rate')
    def validate_rate(cls, v):
        """Validate exchange rate."""
        if v <= 0:
            raise ValueError("Exchange rate must be positive")
        return v


class ExchangeRateCreate(ExchangeRateBase):
    """Schema for creating a new exchange rate."""
    pass


class ExchangeRateUpdate(BaseModel):
    """Schema for updating an existing exchange rate."""
    rate: Optional[Decimal] = Field(None, description="Exchange rate (1 source = rate target)")
    is_official: Optional[bool] = Field(None, description="Whether this is the official rate")
    source: Optional[str] = Field(None, description="Source of the rate (e.g., ECB, Manual)")

    @validator('rate')
    def validate_rate(cls, v):
        """Validate exchange rate."""
        if v is not None and v <= 0:
            raise ValueError("Exchange rate must be positive")
        return v


class ExchangeRateResponse(BaseModel):
    """Schema for exchange rate response."""
    id: UUID = Field(..., description="Exchange rate ID")
    source_currency: CurrencyResponse = Field(..., description="Source currency")
    target_currency: CurrencyResponse = Field(..., description="Target currency")
    rate: Decimal = Field(..., description="Exchange rate (1 source = rate target)")
    effective_date: date = Field(..., description="Date for which this rate is valid")
    rate_type: ExchangeRateType = Field(..., description="Type of exchange rate")
    is_official: bool = Field(..., description="Whether this is the official rate")
    source: Optional[str] = Field(None, description="Source of the rate (e.g., ECB, Manual)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class ConversionRequest(BaseModel):
    """Schema for currency conversion request."""
    amount: Decimal = Field(..., description="Amount to convert")
    from_currency: str = Field(..., description="Source currency code")
    to_currency: str = Field(..., description="Target currency code")
    conversion_date: Optional[date] = Field(None, description="Date for conversion rate")

    @validator('from_currency', 'to_currency')
    def validate_currency_code(cls, v):
        """Validate currency code."""
        if not v or len(v) != 3:
            raise ValueError("Currency code must be 3 characters")
        return v.upper()

    @validator('amount')
    def validate_amount(cls, v):
        """Validate amount."""
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class ConversionResponse(BaseModel):
    """Schema for currency conversion response."""
    original_amount: Decimal = Field(..., description="Original amount")
    original_currency: str = Field(..., description="Original currency code")
    converted_amount: Decimal = Field(..., description="Converted amount")
    target_currency: str = Field(..., description="Target currency code")
    exchange_rate: Decimal = Field(..., description="Exchange rate used")
    conversion_date: date = Field(..., description="Date of the conversion")
    rate_source: Optional[str] = Field(None, description="Source of the exchange rate")