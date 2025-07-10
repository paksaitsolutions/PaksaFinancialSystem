import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum
import httpx
from fastapi import HTTPException, status
import yaml

# Configure logging
logger = logging.getLogger(__name__)

class TaxType(str, Enum):
    SALES = "sales"
    INCOME = "income"
    VAT = "vat"
    GST = "gst"
    WITHHOLDING = "withholding"
    EXCISE = "excise"
    CUSTOM = "custom"

class TaxJurisdiction(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    state_code: Optional[str] = Field(None, min_length=2, max_length=3, description="State/Province code if applicable")
    city: Optional[str] = None
    is_eu: bool = Field(False, description="Whether this jurisdiction is in the EU for VAT purposes")
    tax_authority: Optional[str] = None
    authority_website: Optional[HttpUrl] = None

class TaxRate(BaseModel):
    rate: float = Field(..., ge=0, le=100, description="Tax rate as a percentage (0-100)")
    effective_from: date = Field(default_factory=date.today)
    effective_to: Optional[date] = None
    description: Optional[str] = None
    is_standard_rate: bool = Field(True, description="Whether this is a standard rate (vs reduced/zero rate)")
    
    @validator('effective_to')
    def validate_effective_dates(cls, v, values):
        if v and 'effective_from' in values and v < values['effective_from']:
            raise ValueError("effective_to must be after effective_from")
        return v

class TaxRule(BaseModel):
    code: str = Field(..., description="Unique identifier for this tax rule")
    name: str
    description: str
    type: TaxType
    jurisdiction: TaxJurisdiction
    rates: List[TaxRate]
    category: Optional[str] = None
    is_active: bool = True
    requires_tax_id: bool = False
    tax_id_format: Optional[str] = None
    tax_id_validation_regex: Optional[str] = None
    accounting_code: Optional[str] = None
    gl_account_code: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_effective_rate(self, for_date: Optional[date] = None) -> Optional[TaxRate]:
        """Get the effective tax rate for a given date (defaults to today)"""
        if not for_date:
            for_date = date.today()
            
        effective_rates = [
            rate for rate in sorted(self.rates, key=lambda x: x.effective_from, reverse=True)
            if rate.effective_from <= for_date and (rate.effective_to is None or rate.effective_to >= for_date)
        ]
        
        return effective_rates[0] if effective_rates else None

class TaxExemption(BaseModel):
    exemption_code: str
    description: str
    certificate_required: bool = False
    valid_from: date = Field(default_factory=date.today)
    valid_to: Optional[date] = None
    tax_types: List[TaxType] = Field(default_factory=list)
    jurisdictions: List[TaxJurisdiction] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaxCalculationResult(BaseModel):
    taxable_amount: float
    tax_amount: float
    tax_rate_used: float
    tax_rule: TaxRule
    tax_type: TaxType
    jurisdiction: TaxJurisdiction
    is_exempt: bool = False
    exemption: Optional[TaxExemption] = None
    breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaxPolicyService:
    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self.tax_rules_cache: Dict[str, TaxRule] = {}
        self.tax_exemptions_cache: Dict[str, TaxExemption] = {}
        self.last_updated = datetime.min
        self.update_interval = 3600  # 1 hour in seconds
        self.external_sources = [
            "https://taxee.io/api/v2/global/standard_rates",
            # Add more authoritative tax rate sources here
        ]
    
    async def initialize(self):
        """Initialize the tax policy service with default rules"""
        await self._load_default_rules()
        if self.cache_enabled:
            await self._refresh_cache()
    
    async def _load_default_rules(self):
        """Load default tax rules from configuration"""
        try:
            # Load from local configuration
            default_rules_path = os.path.join(os.path.dirname(__file__), "default_tax_rules.yaml")
            if os.path.exists(default_rules_path):
                with open(default_rules_path, 'r', encoding='utf-8') as f:
                    rules_data = yaml.safe_load(f)
                    for rule_data in rules_data.get('rules', []):
                        try:
                            rule = TaxRule(**rule_data)
                            self.tax_rules_cache[rule.code] = rule
                        except Exception as e:
                            logger.error(f"Error loading tax rule {rule_data.get('code')}: {str(e)}")
            
            logger.info(f"Loaded {len(self.tax_rules_cache)} default tax rules")
            
        except Exception as e:
            logger.error(f"Error loading default tax rules: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize tax policy service"
            )
    
    async def _refresh_cache(self, force: bool = False):
        """Refresh the tax rules cache from external sources"""
        current_time = datetime.utcnow()
        
        # Only refresh if the cache is stale or forced
        if not force and (current_time - self.last_updated).total_seconds() < self.update_interval:
            return
        
        try:
            # Update from external sources
            async with httpx.AsyncClient() as client:
                for source in self.external_sources:
                    try:
                        response = await client.get(source, timeout=10.0)
                        if response.status_code == 200:
                            await self._process_external_rules(response.json())
                    except Exception as e:
                        logger.warning(f"Failed to fetch tax rules from {source}: {str(e)}")
            
            self.last_updated = datetime.utcnow()
            logger.info(f"Tax policy cache refreshed at {self.last_updated}")
            
        except Exception as e:
            logger.error(f"Error refreshing tax policy cache: {str(e)}")
            if not self.tax_rules_cache:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Tax service unavailable and no cached rules available"
                )
    
    async def _process_external_rules(self, rules_data: Dict):
        """Process rules from an external source"""
        # This is a placeholder - implement actual processing based on the external API format
        # For example, TaxJar, Avalara, or other tax API responses
        pass
    
    async def calculate_tax(
        self,
        amount: float,
        tax_type: Union[TaxType, str],
        country_code: str,
        state_code: Optional[str] = None,
        city: Optional[str] = None,
        is_business: bool = False,
        tax_exempt: bool = False,
        exemption_code: Optional[str] = None,
        for_date: Optional[date] = None
    ) -> TaxCalculationResult:
        """Calculate tax for a given amount and jurisdiction"""
        if self.cache_enabled:
            await self._refresh_cache()
        
        if isinstance(tax_type, str):
            try:
                tax_type = TaxType(tax_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid tax type: {tax_type}"
                )
        
        # Check for tax exemption
        exemption = None
        if tax_exempt and exemption_code:
            exemption = await self.get_exemption(exemption_code)
            if not exemption:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid tax exemption code: {exemption_code}"
                )
            
            if tax_type not in exemption.tax_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Exemption {exemption_code} does not apply to tax type {tax_type}"
                )
            
            # Check if exemption is valid for this jurisdiction
            jurisdiction_match = any(
                j.country_code == country_code and 
                (not j.state_code or j.state_code == state_code) and
                (not j.city or j.city == city)
                for j in exemption.jurisdictions
            )
            
            if not jurisdiction_match:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Exemption {exemption_code} is not valid for the specified jurisdiction"
                )
            
            # Return zero tax for valid exemptions
            return TaxCalculationResult(
                taxable_amount=amount,
                tax_amount=0.0,
                tax_rate_used=0.0,
                tax_rule=TaxRule(
                    code="EXEMPT",
                    name="Tax Exemption",
                    description=f"Exempt under {exemption.exemption_code}",
                    type=tax_type,
                    jurisdiction=TaxJurisdiction(country_code=country_code, state_code=state_code, city=city),
                    rates=[TaxRate(rate=0.0, description="Exempt rate")]
                ),
                tax_type=tax_type,
                jurisdiction=TaxJurisdiction(country_code=country_code, state_code=state_code, city=city),
                is_exempt=True,
                exemption=exemption
            )
        
        # Find applicable tax rules
        applicable_rules = [
            rule for rule in self.tax_rules_cache.values()
            if rule.type == tax_type and
            rule.is_active and
            rule.jurisdiction.country_code == country_code and
            (not rule.jurisdiction.state_code or rule.jurisdiction.state_code == state_code) and
            (not rule.jurisdiction.city or rule.jurisdiction.city == city) and
            (not for_date or any(
                rate.effective_from <= for_date and 
                (rate.effective_to is None or rate.effective_to >= for_date)
                for rate in rule.rates
            ))
        ]
        
        if not applicable_rules:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No tax rules found for {tax_type} in {country_code}{f'-{state_code}' if state_code else ''}{f'-{city}' if city else ''}"
            )
        
        # For simplicity, use the first matching rule with the most recent effective date
        # In a real implementation, you might need more complex rule resolution
        selected_rule = max(applicable_rules, key=lambda r: max(rate.effective_from for rate in r.rates))
        effective_rate = selected_rule.get_effective_rate(for_date)
        
        if not effective_rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No effective tax rate found for the specified date"
            )
        
        tax_amount = (amount * effective_rate.rate) / 100.0
        
        return TaxCalculationResult(
            taxable_amount=amount,
            tax_amount=tax_amount,
            tax_rate_used=effective_rate.rate,
            tax_rule=selected_rule,
            tax_type=tax_type,
            jurisdiction=selected_rule.jurisdiction,
            is_exempt=False,
            breakdown=[{
                "taxable_amount": amount,
                "rate": effective_rate.rate,
                "tax_amount": tax_amount,
                "tax_rule_code": selected_rule.code,
                "tax_rule_name": selected_rule.name,
                "jurisdiction": f"{selected_rule.jurisdiction.country_code}-{selected_rule.jurisdiction.state_code or ''}".strip('-')
            }]
        )
    
    async def get_tax_rule(self, code: str) -> Optional[TaxRule]:
        """Get a tax rule by its code"""
        if self.cache_enabled:
            await self._refresh_cache()
        return self.tax_rules_cache.get(code.upper())
    
    async def get_exemption(self, code: str) -> Optional[TaxExemption]:
        """Get a tax exemption by its code"""
        if self.cache_enabled:
            await self._refresh_cache()
        return self.tax_exemptions_cache.get(code.upper())
    
    async def search_tax_rules(
        self,
        tax_type: Optional[Union[TaxType, str]] = None,
        country_code: Optional[str] = None,
        state_code: Optional[str] = None,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[TaxRule]:
        """Search for tax rules matching the given criteria"""
        if self.cache_enabled:
            await self._refresh_cache()
        
        results = list(self.tax_rules_cache.values())
        
        if tax_type is not None:
            if isinstance(tax_type, str):
                tax_type = TaxType(tax_type.lower())
            results = [r for r in results if r.type == tax_type]
        
        if country_code is not None:
            results = [r for r in results if r.jurisdiction.country_code == country_code.upper()]
        
        if state_code is not None:
            results = [r for r in results if r.jurisdiction.state_code == state_code.upper()]
        
        if city is not None:
            results = [r for r in results if r.jurisdiction.city and r.jurisdiction.city.lower() == city.lower()]
        
        if is_active is not None:
            results = [r for r in results if r.is_active == is_active]
        
        if category is not None:
            results = [r for r in results if r.category and r.category.lower() == category.lower()]
        
        if tags:
            tag_set = {t.lower() for t in tags}
            results = [
                r for r in results 
                if any(t.lower() in tag_set for t in r.tags)
            ]
        
        return results

# Singleton instance
tax_policy_service = TaxPolicyService()
