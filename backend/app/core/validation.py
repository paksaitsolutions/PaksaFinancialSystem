"""
Input validation utilities for the Paksa Financial System.

This module provides utility functions for validating and sanitizing input data
across the application.
"""
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, date
import re
from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError, validator, constr, conint, condecimal
from email_validator import validate_email, EmailNotValidError

# Regular expressions for common patterns
PHONE_REGEX = r'^\+?[1-9]\d{1,14}$'  # E.164 format
POSTAL_CODE_REGEX = r'^[A-Z0-9\-\s]+$'
CURRENCY_REGEX = r'^[A-Z]{3}$'  # ISO 4217 currency codes

class ValidationErrorResponse(BaseModel):
    """Standard error response for validation errors."""
    detail: str
    errors: Optional[List[Dict[str, Any]] = None

class BaseValidator:
    """Base class for validators with common validation methods."""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate and normalize an email address."""
        try:
            # Validate and get info
            email_info = validate_email(email, check_deliverability=False)
            # Replace with normalized form
            return email_info.normalized
        except EmailNotValidError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid email address: {str(e)}"
            )
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate a phone number in E.164 format."""
        if not re.match(PHONE_REGEX, phone):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Phone number must be in E.164 format (e.g., +1234567890)"
            )
        return phone
    
    @staticmethod
    def validate_currency(currency: str) -> str:
        """Validate a 3-letter ISO currency code."""
        if not re.match(CURRENCY_REGEX, currency, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Currency must be a 3-letter ISO currency code (e.g., USD, EUR)"
            )
        return currency.upper()
    
    @staticmethod
    def validate_postal_code(postal_code: str) -> str:
        """Validate a postal/zip code."""
        if not re.match(POSTAL_CODE_REGEX, postal_code):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid postal/zip code format"
            )
        return postal_code.upper()
    
    @staticmethod
    def validate_date_range(
        start_date: Union[date, datetime, str],
        end_date: Union[date, datetime, str],
        date_format: str = "%Y-%m-%d"
    ) -> Tuple[date, date]:
        """
        Validate that start_date is before or equal to end_date.
        
        Args:
            start_date: Start date as date, datetime, or string
            end_date: End date as date, datetime, or string
            date_format: Format string for parsing string dates
            
        Returns:
            Tuple of (start_date, end_date) as date objects
            
        Raises:
            HTTPException: If dates are invalid or start_date > end_date
        """
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, date_format).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid start date format. Expected format: {date_format}"
                )
                
        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, date_format).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid end date format. Expected format: {date_format}"
                )
        
        # Ensure start_date is before or equal to end_date
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Start date must be before or equal to end date"
            )
            
        return start_date, end_date


def validate_with_model(model: BaseModel, data: Dict[str, Any]) -> BaseModel:
    """
    Validate data against a Pydantic model.
    
    Args:
        model: Pydantic model class to validate against
        data: Dictionary of data to validate
        
    Returns:
        Validated model instance
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        return model(**data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "detail": "Validation error",
                "errors": e.errors()
            }
        )


def validate_pagination(
    skip: int = 0,
    limit: int = 100,
    max_limit: int = 1000
) -> Tuple[int, int]:
    """
    Validate pagination parameters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        max_limit: Maximum allowed limit
        
    Returns:
        Tuple of (validated_skip, validated_limit)
        
    Raises:
        HTTPException: If validation fails
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Skip must be greater than or equal to 0"
        )
        
    if limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit must be greater than 0"
        )
        
    if limit > max_limit:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Maximum limit is {max_limit}"
        )
        
    return skip, min(limit, max_limit)
