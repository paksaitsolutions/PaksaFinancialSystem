"""
Schemas for region and country operations.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class RegionBase(BaseModel):
    """Base schema for region operations."""
    code: str = Field(..., description="Region code (e.g., NA, EU, AS)")
    name: str = Field(..., description="Region name (e.g., North America, Europe)")
    status: bool = Field(True, description="Region status")

    @validator('code')
    def validate_code(cls, v):
        """Validate region code."""
        if not v or len(v) > 10:
            raise ValueError("Region code must be 1-10 characters")
        return v.upper()


class RegionCreate(RegionBase):
    """Schema for creating a new region."""
    pass


class RegionUpdate(BaseModel):
    """Schema for updating an existing region."""
    code: Optional[str] = Field(None, description="Region code")
    name: Optional[str] = Field(None, description="Region name")
    status: Optional[bool] = Field(None, description="Region status")

    @validator('code')
    def validate_code(cls, v):
        """Validate region code."""
        if v is not None and (not v or len(v) > 10):
            raise ValueError("Region code must be 1-10 characters")
        return v.upper() if v else v


class RegionResponse(RegionBase):
    """Schema for region response."""
    id: UUID = Field(..., description="Region ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class CountryBase(BaseModel):
    """Base schema for country operations."""
    code: str = Field(..., description="ISO 3166-1 alpha-2 country code")
    code_alpha3: Optional[str] = Field(None, description="ISO 3166-1 alpha-3 country code")
    name: str = Field(..., description="Country name")
    official_name: Optional[str] = Field(None, description="Official country name")
    region_id: Optional[UUID] = Field(None, description="Region ID")
    default_currency_id: Optional[UUID] = Field(None, description="Default currency ID")
    phone_code: Optional[str] = Field(None, description="Phone country code")
    status: bool = Field(True, description="Country status")
    capital: Optional[str] = Field(None, description="Capital city")
    timezone: Optional[str] = Field(None, description="Primary timezone")

    @validator('code')
    def validate_code(cls, v):
        """Validate country code."""
        if not v or len(v) != 2:
            raise ValueError("Country code must be 2 characters")
        return v.upper()

    @validator('code_alpha3')
    def validate_code_alpha3(cls, v):
        """Validate alpha-3 country code."""
        if v is not None and len(v) != 3:
            raise ValueError("Alpha-3 country code must be 3 characters")
        return v.upper() if v else v


class CountryCreate(CountryBase):
    """Schema for creating a new country."""
    pass


class CountryUpdate(BaseModel):
    """Schema for updating an existing country."""
    code: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 country code")
    code_alpha3: Optional[str] = Field(None, description="ISO 3166-1 alpha-3 country code")
    name: Optional[str] = Field(None, description="Country name")
    official_name: Optional[str] = Field(None, description="Official country name")
    region_id: Optional[UUID] = Field(None, description="Region ID")
    default_currency_id: Optional[UUID] = Field(None, description="Default currency ID")
    phone_code: Optional[str] = Field(None, description="Phone country code")
    status: Optional[bool] = Field(None, description="Country status")
    capital: Optional[str] = Field(None, description="Capital city")
    timezone: Optional[str] = Field(None, description="Primary timezone")

    @validator('code')
    def validate_code(cls, v):
        """Validate country code."""
        if v is not None and (not v or len(v) != 2):
            raise ValueError("Country code must be 2 characters")
        return v.upper() if v else v

    @validator('code_alpha3')
    def validate_code_alpha3(cls, v):
        """Validate alpha-3 country code."""
        if v is not None and len(v) != 3:
            raise ValueError("Alpha-3 country code must be 3 characters")
        return v.upper() if v else v


class CountryResponse(CountryBase):
    """Schema for country response."""
    id: UUID = Field(..., description="Country ID")
    region: Optional[RegionResponse] = Field(None, description="Region details")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True