"""
Tax Calculation API Endpoints

This module provides API endpoints for tax calculation functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Dict, Optional, Any
from datetime import date, datetime
import logging

from pydantic import BaseModel, Field, validator
from decimal import Decimal

from ....core.security import get_current_active_user, role_required
from ....core.tax.tax_calculation_service import (
    TaxCalculationService,
    TaxCalculationRequest,
    TaxCalculationResponse,
    TaxLineItem,
    TaxCalculationMode
)
from ....models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

# Request and Response Models
class TaxLineItemRequest(BaseModel):
    """Request model for a single line item in a tax calculation"""
    amount: Decimal = Field(..., gt=0, description="Taxable amount")
    quantity: int = Field(1, ge=1, description="Quantity of items")
    tax_code: Optional[str] = Field(None, description="Tax code for this line item")
    product_code: Optional[str] = Field(None, description="Product or service code")
    description: Optional[str] = Field(None, description="Item description")
    is_taxable: bool = Field(True, description="Whether this item is taxable")
    tax_included: bool = Field(False, description="Whether tax is included in the amount")
    tax_override: Optional[Decimal] = Field(None, description="Manual tax override amount")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class TaxCalculationApiRequest(BaseModel):
    """Request model for tax calculation"""
    line_items: List[TaxLineItemRequest] = Field(..., min_items=1, description="List of line items")
    customer_id: Optional[str] = Field(None, description="Customer ID for tax exemption lookup")
    customer_tax_id: Optional[str] = Field(None, description="Customer tax ID (VAT, GST, etc.)")
    customer_tax_id_type: Optional[str] = Field(None, description="Type of tax ID (VAT, GST, etc.)")
    customer_type: Optional[str] = Field(None, description="Type of customer (individual, business, etc.)")
    
    # Billing address
    billing_country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    billing_state: Optional[str] = Field(None, description="State/Province code")
    billing_city: Optional[str] = Field(None, description="City")
    billing_zip: Optional[str] = Field(None, description="Postal/ZIP code")
    
    # Shipping address (optional, defaults to billing)
    shipping_country: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 country code")
    shipping_state: Optional[str] = Field(None, description="State/Province code")
    shipping_city: Optional[str] = Field(None, description="City")
    shipping_zip: Optional[str] = Field(None, description="Postal/ZIP code")
    
    # Transaction details
    transaction_date: date = Field(default_factory=date.today, description="Date of the transaction")
    currency: str = Field("USD", min_length=3, max_length=3, description="ISO 4217 currency code")
    mode: TaxCalculationMode = Field(TaxCalculationMode.AUTO, description="Tax calculation mode")
    
    # Exemption details
    exemption_certificate_id: Optional[str] = Field(None, description="Exemption certificate ID")
    exemption_reason: Optional[str] = Field(None, description="Reason for exemption")
    
    # Metadata
    reference_id: Optional[str] = Field(None, description="Reference ID for the transaction")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }
    
    @validator('line_items')
    def validate_line_items(cls, v):
        if not v:
            raise ValueError("At least one line item is required")
        return v


class TaxCalculationApiResponse(BaseModel):
    """Response model for tax calculation"""
    transaction_id: str = Field(..., description="Unique ID for this tax calculation")
    transaction_date: date = Field(..., description="Date of the transaction")
    currency: str = Field(..., description="Currency code")
    
    # Amounts
    subtotal: Decimal = Field(..., description="Total before tax")
    tax_amount: Decimal = Field(..., description="Total tax amount")
    total: Decimal = Field(..., description="Total including tax")
    
    # Line items with tax details
    line_items: List[Dict] = Field(..., description="Line items with tax details")
    
    # Jurisdictions
    jurisdictions: List[Dict] = Field(default_factory=list, description="Tax jurisdictions involved")
    
    # Exemption info
    is_exempt: bool = Field(False, description="Whether the transaction is tax exempt")
    exemption_certificate_id: Optional[str] = Field(None, description="Exemption certificate ID if applicable")
    
    # Metadata
    reference_id: Optional[str] = Field(None, description="Reference ID from the request")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


@router.post("/calculate", response_model=TaxCalculationApiResponse)
async def calculate_taxes(
    request: Request,
    tax_request: TaxCalculationApiRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate taxes for a transaction.
    
    This endpoint calculates taxes for a transaction based on the provided
    line items, customer information, and addresses. It supports both
    inclusive and exclusive tax calculation modes.
    
    - **line_items**: List of items to calculate tax for
    - **customer_id**: Customer ID for tax exemption lookup
    - **billing_country**: Billing country code (required)
    - **shipping_country**: Shipping country code (defaults to billing)
    - **transaction_date**: Date of the transaction (defaults to today)
    - **currency**: Currency code (defaults to USD)
    - **mode**: Tax calculation mode (inclusive, exclusive, auto)
    
    Returns a detailed breakdown of the calculated taxes.
    """
    try:
        # Convert API request to service request
        line_items = [
            TaxLineItem(
                amount=item.amount,
                quantity=item.quantity,
                tax_code=item.tax_code,
                product_code=item.product_code,
                description=item.description,
                is_taxable=item.is_taxable,
                tax_included=item.tax_included,
                tax_override=item.tax_override,
                metadata=item.metadata
            )
            for item in tax_request.line_items
        ]
        
        service_request = TaxCalculationRequest(
            line_items=line_items,
            customer_id=tax_request.customer_id,
            customer_tax_id=tax_request.customer_tax_id,
            customer_tax_id_type=tax_request.customer_tax_id_type,
            customer_type=tax_request.customer_type,
            billing_country=tax_request.billing_country,
            billing_state=tax_request.billing_state,
            billing_city=tax_request.billing_city,
            billing_zip=tax_request.billing_zip,
            shipping_country=tax_request.shipping_country,
            shipping_state=tax_request.shipping_state,
            shipping_city=tax_request.shipping_city,
            shipping_zip=tax_request.shipping_zip,
            transaction_date=tax_request.transaction_date,
            currency=tax_request.currency,
            mode=tax_request.mode,
            exemption_certificate_id=tax_request.exemption_certificate_id,
            exemption_reason=tax_request.exemption_reason,
            reference_id=tax_request.reference_id,
            metadata=tax_request.metadata
        )
        
        # Calculate taxes
        tax_service = TaxCalculationService()
        result = await tax_service.calculate_taxes(service_request)
        
        # Convert service response to API response
        return TaxCalculationApiResponse(
            transaction_id=result.transaction_id,
            transaction_date=result.transaction_date,
            currency=result.currency,
            subtotal=result.subtotal,
            tax_amount=result.tax_amount,
            total=result.total,
            line_items=result.line_items,
            jurisdictions=result.jurisdictions,
            is_exempt=result.is_exempt,
            exemption_certificate_id=result.exemption_certificate_id,
            reference_id=result.reference_id,
            metadata=result.metadata
        )
        
    except Exception as e:
        logger.error(f"Error calculating taxes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/rates", response_model=Dict[str, Any])
async def get_tax_rates(
    request: Request,
    country_code: str,
    state_code: Optional[str] = None,
    city: Optional[str] = None,
    postal_code: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get tax rates for a specific location.
    
    This endpoint returns the applicable tax rates for a given location.
    
    - **country_code**: ISO 3166-1 alpha-2 country code (required)
    - **state_code**: State/Province code (if applicable)
    - **city**: City name (if applicable)
    - **postal_code**: Postal/ZIP code (if applicable)
    
    Returns a list of tax rates for the specified location.
    """
    try:
        tax_service = TaxCalculationService()
        
        # In a real implementation, this would query the tax policy service
        # For now, return a mock response
        return {
            "country_code": country_code,
            "state_code": state_code,
            "city": city,
            "postal_code": postal_code,
            "rates": [
                {
                    "type": "VAT",
                    "name": "Standard Rate",
                    "rate": 20.0,
                    "is_standard": True
                },
                {
                    "type": "VAT",
                    "name": "Reduced Rate",
                    "rate": 10.0,
                    "is_standard": False,
                    "applies_to": ["books", "food", "medical"]
                }
            ],
            "effective_date": date.today().isoformat(),
            "source": "Paksa Tax Engine"
        }
        
    except Exception as e:
        logger.error(f"Error getting tax rates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/validate-exemption", response_model=Dict[str, Any])
async def validate_tax_exemption(
    request: Request,
    exemption_id: str,
    country_code: str,
    state_code: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate a tax exemption certificate.
    
    This endpoint validates a tax exemption certificate for a given jurisdiction.
    
    - **exemption_id**: The exemption certificate ID to validate
    - **country_code**: ISO 3166-1 alpha-2 country code (required)
    - **state_code**: State/Province code (if applicable)
    
    Returns validation status and details about the exemption.
    """
    try:
        # In a real implementation, this would validate against a database or external service
        # For now, return a mock response
        return {
            "exemption_id": exemption_id,
            "is_valid": True,
            "valid_from": "2023-01-01",
            "valid_to": "2024-12-31",
            "jurisdiction": {
                "country_code": country_code,
                "state_code": state_code
            },
            "customer": {
                "id": "CUST12345",
                "name": "Example Customer Inc.",
                "tax_id": "GB123456789",
                "tax_id_type": "VAT"
            },
            "exemption_type": "RESALE",
            "certificate_required": True,
            "certificate_on_file": True,
            "last_validated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error validating tax exemption: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
