"""
Tax Calculation Service

This module provides comprehensive tax calculation functionality for the Paksa Financial System.
It handles complex tax scenarios including multi-jurisdictional taxes, exemptions, and special tax rules.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Union, Any, Callable, TypeVar
from enum import Enum
import logging
import hashlib
import json
import time
from functools import wraps

from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Type variable for generic return type
T = TypeVar('T')

def cache_key_builder(
    func: Callable[..., T],
    *args,
    **kwargs
) -> str:
    """Generate a cache key from function name and arguments."""
    # Convert args and kwargs to a consistent string representation
    args_str = ",".join(str(arg) for arg in args)
    kwargs_str = ",".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_str = f"{func.__module__}:{func.__name__}:{args_str}:{kwargs_str}"
    
    # Create a hash of the key string to ensure it's a valid cache key
    return f"tax:{hashlib.md5(key_str.encode('utf-8')).hexdigest()}"

from app.core.tax.tax_policy_service import (
    TaxType, 
    TaxRateType, 
    TaxRule, 
    TaxRuleType,
    TaxExemptionCertificate as TaxExemptionCertificateModel,
    TaxRate as TaxRateModel,
    TaxRule as TaxRuleModel
)
from app.core.config import settings
from app.db.session import get_db_context
from app.crud import tax_exemption as tax_exemption_crud
from app.crud import tax_exemption_certificate

logger = logging.getLogger(__name__)

class TaxCalculationMode(str, Enum):
    """Modes for tax calculation"""
    INCLUSIVE = "inclusive"  # Tax is included in the price
    EXCLUSIVE = "exclusive"  # Tax is added to the price
    AUTO = "auto"  # Determine based on jurisdiction rules


class TaxLineItem(BaseModel):
    """Represents a single line item for tax calculation"""
    amount: Decimal = Field(..., gt=0, description="Taxable amount")
    quantity: int = Field(1, ge=1, description="Quantity of items")
    tax_code: Optional[str] = Field(None, description="Tax code for this line item")
    product_code: Optional[str] = Field(None, description="Product or service code")
    description: Optional[str] = Field(None, description="Item description")
    is_taxable: bool = Field(True, description="Whether this item is taxable")
    tax_included: bool = Field(False, description="Whether tax is included in the amount")
    tax_override: Optional[Decimal] = Field(None, description="Manual tax override amount")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")


class TaxCalculationRequest(BaseModel):
    """Request for tax calculation"""
    line_items: List[TaxLineItem] = Field(..., min_items=1)
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


class TaxCalculationResponse(BaseModel):
    """Response from tax calculation"""
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


class TaxCalculationService:
    """Service for calculating taxes on transactions."""
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize the tax calculation service.
        
        Args:
            db: Optional SQLAlchemy session. If not provided, a new session will be created when needed.
        """
        self.db = db
        self.tax_policy_service = tax_policy_service
        self._cache_enabled = settings.REDIS_URL is not None
        self._cache_ttl = settings.CACHE_TTL_SECONDS if hasattr(settings, 'CACHE_TTL_SECONDS') else 300  # 5 minutes default
        self._last_cache_refresh = datetime.min
        self._local_cache = {}
        
        # Initialize Redis cache if available
        if self._cache_enabled and not hasattr(self, '_redis_initialized'):
            try:
                from redis import asyncio as aioredis
                redis = aioredis.from_url(settings.REDIS_URL)
                FastAPICache.init(RedisBackend(redis), prefix="tax-cache")
                self._redis_initialized = True
                logger.info("Redis cache initialized for tax service")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {str(e)}. Using in-memory cache only.")
                self._cache_enabled = False
        
    def _get_db(self) -> Session:
        """Get a database session, creating one if needed."""
        if self.db is None:
            from app.db.session import SessionLocal
            self.db = SessionLocal()
        return self.db
        
    def _generate_tax_rules_cache_key(
        self,
        item: TaxLineItem,
        billing_country: str,
        billing_state: Optional[str],
        billing_city: Optional[str],
        shipping_country: str,
        shipping_state: Optional[str],
        shipping_city: Optional[str],
        transaction_date: date,
        customer_id: Optional[str],
        customer_type: Optional[str],
        exemption_certificate_id: Optional[str]
    ) -> str:
        """Generate a cache key for tax rules lookup."""
        key_parts = [
            f"item:{item.tax_code}:{item.product_type}",
            f"bill:{billing_country}:{billing_state or ''}:{billing_city or ''}",
            f"ship:{shipping_country}:{shipping_state or ''}:{shipping_city or ''}",
            f"date:{transaction_date}",
            f"cust:{customer_id or ''}:{customer_type or ''}",
            f"exempt:{exemption_certificate_id or ''}"
        ]
        return f"tax_rules:{hashlib.md5('|'.join(key_parts).encode('utf-8')).hexdigest()}"
        
    async def _cache_tax_rules_result(self, cache_key: str, rules: List[Dict]) -> None:
        """Cache the result of a tax rules lookup."""
        if not rules:
            expiry = 60  # 1 minute for empty results
        else:
            expiry = self._cache_ttl
            
        # Update local cache
        self._local_cache[cache_key] = (
            rules,
            datetime.now() + timedelta(seconds=expiry)
        )
        
        # Update Redis cache if enabled
        if self._cache_enabled:
            try:
                await FastAPICache.set(cache_key, rules, expire=expiry)
            except Exception as e:
                logger.warning(f"Error updating Redis cache: {str(e)}")
    
    async def _get_tax_rules_with_cache(
        self,
        country_code: str,
        state_code: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Dict]:
        """
        Get tax rules with caching support.
        
        Args:
            country_code: Country code (e.g., 'US')
            state_code: Optional state/province code
            city: Optional city name
            
        Returns:
            List of tax rules
        """
        cache_key = f"tax_rules_jurisdiction:{country_code}:{state_code or ''}:{city or ''}"
        
        # Try local cache first
        if cache_key in self._local_cache:
            rules, expiry = self._local_cache[cache_key]
            if datetime.now() < expiry:
                return rules
            del self._local_cache[cache_key]
            
        # Try Redis cache
        if self._cache_enabled:
            try:
                cached_rules = await FastAPICache.get(cache_key)
                if cached_rules is not None:
                    # Update local cache
                    self._local_cache[cache_key] = (
                        cached_rules,
                        datetime.now() + timedelta(minutes=15)
                    )
                    return cached_rules
            except Exception as e:
                logger.warning(f"Error getting tax rules from Redis cache: {str(e)}")
        
        # Get from database
        db = self._get_db()
        rules = await self.tax_policy_service.search_tax_rules(
            tax_type=None,
            country_code=country_code,
            state_code=state_code,
            city=city,
            is_active=True
        )
        
        # Cache the result
        expiry = 3600  # 1 hour for jurisdiction-based rules
        self._local_cache[cache_key] = (rules, datetime.now() + timedelta(seconds=expiry))
        
        if self._cache_enabled:
            try:
                await FastAPICache.set(cache_key, rules, expire=expiry)
            except Exception as e:
                logger.warning(f"Error setting Redis cache: {str(e)}")
                
        return rules
    
    async def calculate_taxes(
        self, 
        request: TaxCalculationRequest
    ) -> TaxCalculationResponse:
        """
        Calculate taxes for a transaction.
        
        Args:
            request: TaxCalculationRequest containing transaction details
            
        Returns:
            TaxCalculationResponse with calculated tax amounts
        """
        try:
            # Initialize response
            response = TaxCalculationResponse(
                transaction_id=self._generate_transaction_id(),
                transaction_date=request.transaction_date,
                currency=request.currency,
                subtotal=Decimal('0'),
                tax_amount=Decimal('0'),
                total=Decimal('0'),
                line_items=[],
                jurisdictions=[],
                is_exempt=False,
                reference_id=request.reference_id,
                metadata=request.metadata
            )
            
            # Process line items
            for item in request.line_items:
                line_result = await self._process_line_item(item, request)
                response.line_items.append(line_result)
                
                # Update totals
                response.subtotal += line_result['amount']
                response.tax_amount += line_result.get('tax_amount', Decimal('0'))
            
            # Calculate total
            response.total = response.subtotal + response.tax_amount
            
            # Apply any transaction-level adjustments
            response = self._apply_transaction_adjustments(response, request)
            
            # Round amounts to currency precision
            response = self._round_amounts(response, request.currency)
            
            return response
            
        except Exception as e:
            logger.error(f"Error calculating taxes: {str(e)}", exc_info=True)
            raise
    
    async def _process_line_item(
        self, 
        item: TaxLineItem, 
        request: TaxCalculationRequest
    ) -> Dict:
        """Process a single line item for tax calculation"""
        try:
            # Initialize line result
            line_result = {
                'amount': item.amount * item.quantity,
                'quantity': item.quantity,
                'tax_code': item.tax_code,
                'product_code': item.product_code,
                'description': item.description,
                'is_taxable': item.is_taxable,
                'tax_included': item.tax_included,
                'tax_breakdown': [],
                'tax_amount': Decimal('0')
            }
            
            # Skip tax calculation for non-taxable items
            if not item.is_taxable:
                return line_result
            
            # Get applicable tax rules for this item
            tax_rules = await self._get_applicable_tax_rules(
                item=item,
                billing_country=request.billing_country,
                billing_state=request.billing_state,
                billing_city=request.billing_city,
                shipping_country=request.shipping_country or request.billing_country,
                shipping_state=request.shipping_state or request.billing_state,
                shipping_city=request.shipping_city or request.billing_city,
                transaction_date=request.transaction_date,
                customer_id=request.customer_id,
                customer_tax_id=request.customer_tax_id,
                customer_type=request.customer_type,
                exemption_certificate_id=request.exemption_certificate_id
            )
            
            # Apply tax rules to the line item
            for rule in tax_rules:
                tax_result = self._apply_tax_rule(
                    rule=rule,
                    amount=item.amount,
                    quantity=item.quantity,
                    is_tax_included=item.tax_included
                )
                
                if tax_result:
                    line_result['tax_breakdown'].append(tax_result)
                    line_result['tax_amount'] += tax_result['amount']
            
            return line_result
            
        except Exception as e:
            logger.error(f"Error processing line item: {str(e)}", exc_info=True)
            raise
    
    async def _get_applicable_tax_rules(
        self,
        item: TaxLineItem,
        billing_country: str,
        billing_state: Optional[str],
        billing_city: Optional[str],
        shipping_country: str,
        shipping_state: Optional[str],
        shipping_city: Optional[str],
        transaction_date: date,
        customer_id: Optional[str] = None,
        customer_tax_id: Optional[str] = None,
        customer_type: Optional[str] = None,
        exemption_certificate_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get applicable tax rules for a line item based on various criteria.
        
        This method determines which tax rules apply to a given line item
        based on location, product type, customer information, and other factors.
        """
        # Generate a cache key based on the function arguments
        cache_key = self._generate_tax_rules_cache_key(
            item=item,
            billing_country=billing_country,
            billing_state=billing_state,
            billing_city=billing_city,
            shipping_country=shipping_country,
            shipping_state=shipping_state,
            shipping_city=shipping_city,
            transaction_date=transaction_date,
            customer_id=customer_id,
            customer_type=customer_type,
            exemption_certificate_id=exemption_certificate_id
        )
        
        # Try to get from local cache first
        if cache_key in self._local_cache:
            cached_rules, expiry = self._local_cache[cache_key]
            if datetime.now() < expiry:
                return cached_rules
            # Cache expired, remove it
            del self._local_cache[cache_key]
        
        # Try to get from Redis cache if enabled
        if self._cache_enabled:
            try:
                cached_rules = await FastAPICache.get(cache_key)
                if cached_rules is not None:
                    # Cache for 15 minutes in local cache after getting from Redis
                    self._local_cache[cache_key] = (
                        cached_rules,
                        datetime.now() + timedelta(minutes=15)
                    )
                    return cached_rules
            except Exception as e:
                logger.warning(f"Error getting tax rules from Redis cache: {str(e)}")
        
        # Not in cache, proceed with calculation
        try:
            # Check for tax exemption first
            is_exempt = await self._check_tax_exemption(
                customer_id=customer_id,
                customer_tax_id=customer_tax_id,
                customer_type=customer_type,
                exemption_certificate_id=exemption_certificate_id,
                tax_code=item.tax_code,
                transaction_date=transaction_date,
                country_code=billing_country,
                state_code=billing_state,
                city=billing_city
            )
            
            if is_exempt:
                result = []
                # Cache the empty result
                self._cache_tax_rules_result(cache_key, result)
                return result
            
            # Determine which jurisdiction to use (origin vs. destination)
            use_destination = self._should_use_destination_based_tax(
                billing_country=billing_country,
                shipping_country=shipping_country
            )
            
            # Get tax rules for the appropriate jurisdiction
            if use_destination:
                country = shipping_country
                state = shipping_state
                city = shipping_city
            else:
                country = billing_country
                state = billing_state
                city = billing_city
            
            # Get tax rules from the tax policy service with caching
            tax_rules = await self._get_tax_rules_with_cache(
                country_code=country,
                state_code=state,
                city=city
            )
            
            # Filter rules based on product type, customer type, etc.
            filtered_rules = []
            for rule in tax_rules:
                if self._does_rule_apply(rule, item, customer_type, transaction_date):
                    filtered_rules.append(rule)
            
            # Cache the result
            self._cache_tax_rules_result(cache_key, filtered_rules)
            
            return filtered_rules
            
        except Exception as e:
            logger.error(f"Error getting applicable tax rules: {str(e)}", exc_info=True)
            raise
    
    async def _check_tax_exemption(
        self,
        customer_id: Optional[str],
        customer_tax_id: Optional[str],
        customer_type: Optional[str],
        exemption_certificate_id: Optional[str],
        tax_code: Optional[str],
        transaction_date: date,
        country_code: str,
        state_code: Optional[str] = None,
        city: Optional[str] = None
    ) -> bool:
        """
        Check if a transaction is tax exempt based on various criteria.
        
        Args:
            customer_id: Unique identifier for the customer
            customer_tax_id: Customer's tax identification number
            customer_type: Type of customer (e.g., 'BUSINESS', 'GOVERNMENT')
            exemption_certificate_id: ID of any exemption certificate provided
            tax_code: Tax code for the line item
            transaction_date: Date of the transaction
            country_code: Billing country code (ISO 3166-1 alpha-2)
            state_code: Billing state/province code
            city: Billing city
            
        Returns:
            bool: True if the transaction is tax exempt, False otherwise
        """
        # Check for exemption certificate first (takes highest precedence)
        if exemption_certificate_id:
            is_valid = await self._validate_exemption_certificate(
                certificate_id=exemption_certificate_id,
                customer_id=customer_id,
                tax_code=tax_code,
                transaction_date=transaction_date,
                country_code=country_code,
                state_code=state_code,
                city=city
            )
            if is_valid:
                logger.info(f"Transaction exempt - Valid exemption certificate: {exemption_certificate_id}")
                return True
        
        # Check customer-level exemptions
        if customer_id:
            is_exempt = await self._check_customer_exemptions(
                customer_id=customer_id,
                customer_tax_id=customer_tax_id,
                customer_type=customer_type,
                tax_code=tax_code,
                transaction_date=transaction_date,
                country_code=country_code,
                state_code=state_code,
                city=city
            )
            if is_exempt:
                logger.info(f"Transaction exempt - Customer-level exemption for customer {customer_id}")
                return True
        
        # Check tax code exemptions (e.g., tax codes starting with 'EXEMPT_')
        if tax_code and tax_code.startswith('EXEMPT_'):
            logger.info(f"Transaction exempt - Tax code indicates exemption: {tax_code}")
            return True
        
        # Check for automatic exemptions based on customer type
        if customer_type in ['GOVERNMENT', 'NONPROFIT', 'DIPLOMATIC']:
            logger.info(f"Transaction exempt - Customer type {customer_type} is automatically exempt")
            return True
            
        return False
    
    async def _validate_exemption_certificate(
        self,
        certificate_id: str,
        customer_id: Optional[str],
        tax_code: Optional[str],
        transaction_date: date,
        country_code: str,
        state_code: Optional[str] = None,
        city: Optional[str] = None
    ) -> bool:
        """
        Validate an exemption certificate.
        
        Args:
            certificate_id: The exemption certificate ID to validate
            customer_id: Customer ID associated with the certificate
            tax_code: Tax code this exemption applies to
            transaction_date: Date of the transaction
            country_code: Billing country code
            state_code: Billing state/province code
            city: Billing city
            
        Returns:
            bool: True if the certificate is valid and applicable, False otherwise
        """
        try:
            # Get the exemption certificate from the database
            cert = await self._get_exemption_certificate(certificate_id)
            if not cert:
                logger.warning(f"Exemption certificate not found: {certificate_id}")
                return False
            
            # Check certificate expiration
            expiry_date = cert.get('expiry_date')
            if expiry_date and expiry_date < transaction_date:
                logger.warning(f"Exemption certificate {certificate_id} expired on {expiry_date}")
                return False
            
            # Check if certificate is valid for this customer
            if customer_id and cert.get('customer_id') != customer_id:
                logger.warning(f"Certificate {certificate_id} does not belong to customer {customer_id}")
                return False
            
            # Check if certificate is valid for this tax code
            if tax_code and cert.get('tax_codes'):
                if tax_code not in cert['tax_codes']:
                    logger.warning(f"Certificate {certificate_id} not valid for tax code {tax_code}")
                    return False
            
            # Check jurisdiction restrictions
            if not self._is_certificate_valid_for_jurisdiction(
                cert,
                country_code,
                state_code,
                city
            ):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating exemption certificate {certificate_id}: {str(e)}", exc_info=True)
            return False
    
    async def _get_exemption_certificate(self, certificate_id: str) -> Optional[Dict]:
        """
        Get an exemption certificate from the database or cache.
        
        Args:
            certificate_id: The certificate number to retrieve
            
        Returns:
            Dict containing the certificate data, or None if not found
        """
        # Generate cache key
        cache_key = f"exemption_cert:{certificate_id}"
        
        # Try to get from local cache first
        if cache_key in self._local_cache:
            cert_data, expiry = self._local_cache[cache_key]
            if datetime.now() < expiry:
                return cert_data
            # Cache expired, remove it
            del self._local_cache[cache_key]
        
        # Try to get from Redis cache if enabled
        if self._cache_enabled:
            try:
                cached_cert = await FastAPICache.get(cache_key)
                if cached_cert:
                    # Cache for 1 hour in local cache after getting from Redis
                    self._local_cache[cache_key] = (
                        cached_cert, 
                        datetime.now() + timedelta(minutes=5)  # Local cache for 5 minutes
                    )
                    return cached_cert
            except Exception as e:
                logger.warning(f"Error getting from Redis cache: {str(e)}")
        
        # Not in cache, fetch from database
        try:
            db = self._get_db()
            cert = tax_exemption_certificate.get_by_certificate_number(db, certificate_number=certificate_id)
            
            if not cert:
                logger.warning(f"Exemption certificate not found: {certificate_id}")
                # Cache negative result for a short time to prevent repeated lookups
                self._local_cache[cache_key] = (None, datetime.now() + timedelta(minutes=1))
                return None
                
            # Convert SQLAlchemy model to dict
            cert_dict = {
                'id': str(cert.id),
                'certificate_number': cert.certificate_number,
                'customer_id': str(cert.customer_id) if cert.customer_id else None,
                'customer_tax_id': cert.customer_tax_id,
                'customer_name': cert.customer_name,
                'exemption_type': cert.exemption_type,
                'issuing_jurisdiction': cert.issuing_jurisdiction,
                'issue_date': cert.issue_date,
                'expiry_date': cert.expiry_date,
                'is_active': cert.is_active,
                'tax_codes': cert.tax_codes or [],
                'jurisdictions': cert.jurisdictions or [],
                'document_reference': cert.document_reference,
                'notes': cert.notes,
                'created_by': str(cert.created_by) if cert.created_by else None,
                'updated_by': str(cert.updated_by) if cert.updated_by else None,
                'created_at': cert.created_at,
                'updated_at': cert.updated_at,
                'is_valid': cert.is_valid,
            }
            
            # Cache the result
            expiry = datetime.now() + timedelta(minutes=30)  # Cache for 30 minutes
            self._local_cache[cache_key] = (cert_dict, expiry)
            
            # Also cache in Redis if available
            if self._cache_enabled:
                try:
                    await FastAPICache.set(cache_key, cert_dict, expire=self._cache_ttl)
                except Exception as e:
                    logger.warning(f"Error setting Redis cache: {str(e)}")
            
            return cert_dict
            
        except Exception as e:
            logger.error(f"Error fetching exemption certificate {certificate_id}: {str(e)}", exc_info=True)
            return None
    
    async def _check_customer_exemptions(
        self,
        customer_id: str,
        customer_tax_id: Optional[str],
        customer_type: Optional[str],
        tax_code: Optional[str],
        transaction_date: date,
        country_code: str,
        state_code: Optional[str] = None,
        city: Optional[str] = None
    ) -> bool:
        """
        Check if a customer has any applicable tax exemptions.
        
        Args:
            customer_id: The customer ID to check
            customer_tax_id: Customer's tax ID (for validation)
            customer_type: Type of customer
            tax_code: Tax code for the line item
            transaction_date: Date of the transaction
            country_code: Billing country code
            state_code: Billing state/province code
            city: Billing city
            
        Returns:
            bool: True if the customer has a valid exemption, False otherwise
        """
        try:
            db = self._get_db()
            
            # Get active exemptions for this customer
            exemptions = tax_exemption_crud.get_active(
                db,
                skip=0,
                limit=100,  # Should be enough for most cases
                company_id=None,  # Get global and company-specific exemptions
            )
            
            # Convert to list of dicts
            result = []
            for exemption in exemptions:
                result.append({
                    'id': str(exemption.id),
                    'exemption_code': exemption.exemption_code,
                    'description': exemption.description,
                    'certificate_required': exemption.certificate_required,
                    'valid_from': exemption.valid_from,
                    'valid_to': exemption.valid_to,
                    'tax_types': exemption.tax_types or [],
                    'jurisdictions': exemption.jurisdictions or [],
                    'is_active': exemption.is_active,
                    'company_id': str(exemption.company_id) if exemption.company_id else None,
                    'created_at': exemption.created_at,
                    'updated_at': exemption.updated_at,
                })
                
            # Check if any exemptions apply
            for exemption in result:
                # Check if exemption is active
                if not exemption.get('is_active', False):
                    continue
                    
                # Check effective dates
                effective_from = exemption.get('effective_from')
                if effective_from and effective_from > transaction_date:
                    continue
                    
                effective_to = exemption.get('effective_to')
                if effective_to and effective_to < transaction_date:
                    continue
                
                # Check if exemption applies to this tax code
                if tax_code and exemption.get('tax_codes'):
                    if tax_code not in exemption['tax_codes']:
                        continue
                
                # Check jurisdiction
                if not self._is_exemption_valid_for_jurisdiction(
                    exemption,
                    country_code,
                    state_code,
                    city
                ):
                    continue
                
                # All checks passed - exemption applies
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking customer exemptions for {customer_id}: {str(e)}", exc_info=True)
            return False
    
    def _is_certificate_valid_for_jurisdiction(
        self,
        certificate: Dict,
        country_code: str,
        state_code: Optional[str] = None,
        city: Optional[str] = None
    ) -> bool:
        """Check if a certificate is valid for the given jurisdiction"""
        # If no jurisdiction restrictions, certificate is valid everywhere
        if not certificate.get('jurisdictions'):
            return True
            
        # Check if any of the certificate's jurisdictions match
        for jurisdiction in certificate['jurisdictions']:
            if jurisdiction.get('country_code') != country_code:
                continue
                
            # If state is specified, it must match
            if jurisdiction.get('state_code') and jurisdiction['state_code'] != state_code:
                continue
                
            # If city is specified, it must match
            if jurisdiction.get('city') and jurisdiction['city'].lower() != (city or '').lower():
                continue
                
            # All applicable jurisdiction fields match
            return True
            
        return False
    
    def _is_exemption_valid_for_jurisdiction(
        self,
        exemption: Dict,
        country_code: str,
        state_code: Optional[str] = None,
        city: Optional[str] = None
    ) -> bool:
        """Check if an exemption is valid for the given jurisdiction"""
        # If no jurisdiction restrictions, exemption is valid everywhere
        if not exemption.get('jurisdictions'):
            return True
            
        # Check if any of the exemption's jurisdictions match
        for jurisdiction in exemption['jurisdictions']:
            if jurisdiction.get('country_code') and jurisdiction['country_code'] != country_code:
                continue
                
            # If state is specified, it must match
            if jurisdiction.get('state_code') and jurisdiction['state_code'] != state_code:
                continue
                
            # If city is specified, it must match
            if jurisdiction.get('city') and jurisdiction['city'].lower() != (city or '').lower():
                continue
                
            # All applicable jurisdiction fields match
            return True
            
        return False
    
    def _should_use_destination_based_tax(
        self,
        billing_country: str,
        shipping_country: Optional[str]
    ) -> bool:
        """Determine whether to use destination-based or origin-based taxation"""
        # If shipping country is different from billing, use destination-based
        if shipping_country and shipping_country != billing_country:
            return True
            
        # TODO: Add more sophisticated logic based on country rules
        # For now, default to origin-based (billing address)
        return False
    
    def _does_rule_apply(
        self,
        rule: Dict,
        item: TaxLineItem,
        customer_type: Optional[str],
        transaction_date: date
    ) -> bool:
        """Determine if a tax rule applies to a given line item"""
        # Check if rule is active
        if not rule.get('is_active', True):
            return False
            
        # Check effective dates
        effective_from = rule.get('effective_from')
        if effective_from and effective_from > transaction_date:
            return False
            
        effective_to = rule.get('effective_to')
        if effective_to and effective_to < transaction_date:
            return False
        
        # Check customer type restrictions
        customer_types = rule.get('customer_types', [])
        if customer_types and customer_type and customer_type not in customer_types:
            return False
            
        # Check product restrictions
        product_codes = rule.get('product_codes', [])
        if product_codes and item.product_code and item.product_code not in product_codes:
            return False
            
        # Check tax code restrictions
        tax_codes = rule.get('tax_codes', [])
        if tax_codes and item.tax_code and item.tax_code not in tax_codes:
            return False
            
        return True
    
    def _apply_tax_rule(
        self,
        rule: Dict,
        amount: Decimal,
        quantity: int,
        is_tax_included: bool
    ) -> Dict:
        """Apply a tax rule to a line item amount"""
        try:
            # Get the applicable tax rate
            rate = self._get_applicable_tax_rate(rule)
            if not rate:
                return {}
            
            # Calculate tax amount
            taxable_amount = amount * quantity
            
            if is_tax_included:
                # Tax is included in the amount, calculate the tax amount
                tax_amount = taxable_amount - (taxable_amount / (1 + (rate / 100)))
            else:
                # Tax is added to the amount
                tax_amount = taxable_amount * (rate / 100)
            
            # Prepare tax breakdown
            return {
                'jurisdiction': rule.get('jurisdiction', {}).get('name', 'Unknown'),
                'jurisdiction_level': rule.get('jurisdiction', {}).get('level', 'country'),
                'tax_type': rule.get('type', 'sales'),
                'tax_name': rule.get('name', 'Tax'),
                'rate': float(rate),
                'amount': tax_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'is_compound': rule.get('is_compound', False),
                'tax_code': rule.get('code')
            }
            
        except Exception as e:
            logger.error(f"Error applying tax rule: {str(e)}", exc_info=True)
            return {}
    
    def _get_applicable_tax_rate(self, rule: Dict) -> Optional[Decimal]:
        """Get the applicable tax rate from a tax rule"""
        rates = rule.get('rates', [])
        if not rates:
            return None
            
        # For now, just return the first rate
        # In a real implementation, you'd select based on date, customer type, etc.
        return Decimal(str(rates[0].get('rate', 0)))
    
    def _is_tax_holiday(
        self, 
        transaction_date: date, 
        country_code: str, 
        state_code: Optional[str] = None
    ) -> bool:
        """
        Check if a transaction date falls on a tax holiday.
        
        Args:
            transaction_date: The date of the transaction
            country_code: The country code (ISO 3166-1 alpha-2)
            state_code: Optional state/province code
            
        Returns:
            bool: True if the date is a tax holiday, False otherwise
        """
        # TODO: Implement actual tax holiday lookup from database
        # This is a simplified implementation that checks a few common holidays
        
        # Example: Check for end-of-year tax holidays (common in some countries)
        if transaction_date.month == 12 and transaction_date.day in [24, 25, 26, 31]:
            return True
            
        # Example: Check for national holidays that might be tax-free days
        national_holidays = {
            'US': [
                (1, 1),   # New Year's Day
                (7, 4),   # Independence Day
                (12, 25), # Christmas
            ],
            'GB': [
                (1, 1),   # New Year's Day
                (12, 25), # Christmas
                (12, 26), # Boxing Day
            ],
            # Add more countries as needed
        }
        
        # Check if the date matches any national holidays for the country
        if country_code in national_holidays:
            if (transaction_date.month, transaction_date.day) in national_holidays[country_code]:
                return True
        
        return False
    
    def _is_special_tax_regime(
        self,
        customer_type: Optional[str],
        country_code: str,
        state_code: Optional[str],
        transaction_date: date
    ) -> bool:
        """
        Check if a transaction qualifies for a special tax regime.
        
        Special tax regimes might include:
        - Small business tax rates
        - Agricultural or manufacturing incentives
        - Free trade zones
        - Special economic zones
        - Reduced rates for specific industries
        """
        # TODO: Implement actual special regime lookup from database
        # This is a simplified implementation
        
        # Example: Check for small business exemption
        if customer_type == 'SMALL_BUSINESS':
            return True
            
        # Example: Check for special economic zones
        special_zones = {
            'CN': ['SH', 'SZ', 'GZ'],  # Special Economic Zones in China
            'AE': ['DXB', 'AUH'],       # Free zones in UAE
            'MY': ['PJY', 'KUL'],       # Special zones in Malaysia
        }
        
        if country_code in special_zones and state_code in special_zones[country_code]:
            return True
            
        return False
    
    def _get_special_tax_rate(
        self,
        customer_type: Optional[str],
        country_code: str,
        state_code: Optional[str],
        transaction_date: date
    ) -> Optional[float]:
        """
        Get the special tax rate for a transaction, if applicable.
        
        Returns:
            Optional[float]: The special tax rate as a decimal (e.g., 0.05 for 5%),
                            or None if no special rate applies.
        """
        # TODO: Implement actual special rate lookup from database
        # This is a simplified implementation
        
        # Example: Reduced rate for small businesses
        if customer_type == 'SMALL_BUSINESS':
            return 0.03  # 3% reduced rate
            
        # Example: Special rates for economic zones
        special_zone_rates = {
            'CN': {'SH': 0.15, 'SZ': 0.15, 'GZ': 0.15},  # 15% in Chinese SEZs
            'AE': {'DXB': 0.00, 'AUH': 0.00},            # 0% in UAE free zones
            'MY': {'PJY': 0.05, 'KUL': 0.05},            # 5% in Malaysian special zones
        }
        
        if country_code in special_zone_rates:
            if state_code in special_zone_rates[country_code]:
                return special_zone_rates[country_code][state_code]
        
        # No special rate applies
        return None
    
    def _apply_transaction_adjustments(
        self,
        response: TaxCalculationResponse,
        request: TaxCalculationRequest
    ) -> TaxCalculationResponse:
        """
        Apply transaction-level tax adjustments.
        
        Handles:
        - Rounding rules based on jurisdiction
        - Minimum/maximum tax amounts
        - Tax holidays and special regimes
        - Tax-inclusive vs tax-exclusive adjustments
        """
        try:
            # Check for tax holidays first
            if self._is_tax_holiday(request.transaction_date, request.billing_country, request.billing_state):
                response.tax_amount = Decimal('0')
                response.total = response.subtotal
                response.is_exempt = True
                response.metadata['exemption_reason'] = 'tax_holiday'
                return response
                
            # Apply minimum/maximum tax rules
            min_tax = request.metadata.get('minimum_tax')
            max_tax = request.metadata.get('maximum_tax')
            
            if min_tax is not None and response.tax_amount < Decimal(str(min_tax)):
                response.tax_amount = Decimal(str(min_tax))
                response.metadata['applied_min_tax'] = True
                
            if max_tax is not None and response.tax_amount > Decimal(str(max_tax)):
                response.tax_amount = Decimal(str(max_tax))
                response.metadata['applied_max_tax'] = True
            
            # Apply any special tax regimes
            if self._is_special_tax_regime(
                request.customer_type,
                request.billing_country,
                request.billing_state,
                request.transaction_date
            ):
                special_rate = self._get_special_tax_rate(
                    request.customer_type,
                    request.billing_country,
                    request.billing_state,
                    request.transaction_date
                )
                if special_rate is not None:
                    # Recalculate tax using special rate
                    response.tax_amount = (response.subtotal * Decimal(str(special_rate))).quantize(
                        Decimal('0.01'), 
                        rounding=ROUND_HALF_UP
                    )
                    response.metadata['special_tax_regime'] = True
                    response.metadata['special_tax_rate'] = float(special_rate)
            
            # Recalculate total after adjustments
            response.total = response.subtotal + response.tax_amount
            
            return response
            
        except Exception as e:
            logger.error(f"Error applying transaction adjustments: {str(e)}", exc_info=True)
            return response
    
    def _round_amounts(
        self,
        response: TaxCalculationResponse,
        currency: str
    ) -> TaxCalculationResponse:
        """Round monetary amounts according to currency rules"""
        # Get currency precision (default to 2 decimal places)
        precision = 2
        if currency in ['JPY', 'KRW', 'ISK', 'HUF']:
            precision = 0
        
        # Round amounts
        response.subtotal = response.subtotal.quantize(
            Decimal('0.' + '0' * precision), 
            rounding=ROUND_HALF_UP
        )
        response.tax_amount = response.tax_amount.quantize(
            Decimal('0.' + '0' * precision), 
            rounding=ROUND_HALF_UP
        )
        response.total = response.total.quantize(
            Decimal('0.' + '0' * precision), 
            rounding=ROUND_HALF_UP
        )
        
        # Round line item amounts
        for item in response.line_items:
            item['amount'] = Decimal(str(item['amount'])).quantize(
                Decimal('0.' + '0' * precision), 
                rounding=ROUND_HALF_UP
            )
            if 'tax_amount' in item:
                item['tax_amount'] = Decimal(str(item['tax_amount'])).quantize(
                    Decimal('0.' + '0' * precision), 
                    rounding=ROUND_HALF_UP
                )
            
            # Round tax breakdown amounts
            for tax in item.get('tax_breakdown', []):
                if 'amount' in tax:
                    tax['amount'] = float(Decimal(str(tax['amount'])).quantize(
                        Decimal('0.' + '0' * precision), 
                        rounding=ROUND_HALF_UP
                    ))
        
        return response
    
    def _generate_transaction_id(self) -> str:
        """Generate a unique transaction ID"""
        import uuid
        return f"txn_{uuid.uuid4().hex[:12]}"


# Singleton instance
tax_calculation_service = TaxCalculationService()
