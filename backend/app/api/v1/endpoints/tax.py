from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import date, datetime
import logging
from enum import Enum

from ....core.security import get_current_active_user, role_required
from ....core.tax.tax_policy_service import (
    TaxType, TaxJurisdiction, TaxRate, TaxRule, TaxExemption, 
    TaxCalculationResult, tax_policy_service
)
from ....models.user import User
from ....schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()
logger = logging.getLogger(__name__)

# Request and Response Models
class TaxRuleCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, pattern=r'^[A-Z0-9-_]+$')
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
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

class TaxRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    category: Optional[str] = None
    accounting_code: Optional[str] = None
    gl_account_code: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class TaxRuleResponse(TaxRule):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

class TaxExemptionCreate(BaseModel):
    exemption_code: str = Field(..., min_length=2, max_length=50, pattern=r'^[A-Z0-9-_]+$')
    description: str
    certificate_required: bool = False
    valid_from: date = Field(default_factory=date.today)
    valid_to: Optional[date] = None
    tax_types: List[TaxType] = Field(default_factory=list)
    jurisdictions: List[TaxJurisdiction] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaxExemptionResponse(TaxExemption):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

class TaxCalculationRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to calculate tax for")
    tax_type: TaxType
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    state_code: Optional[str] = Field(None, min_length=2, max_length=3, description="State/Province code if applicable")
    city: Optional[str] = None
    is_business: bool = False
    tax_exempt: bool = False
    exemption_code: Optional[str] = None
    for_date: Optional[date] = None
    line_items: Optional[List[Dict[str, Any]]] = None
    customer_tax_id: Optional[str] = None
    customer_tax_id_type: Optional[str] = None
    customer_tax_id_valid: Optional[bool] = None
    customer_type: Optional[str] = None
    customer_country_code: Optional[str] = None
    customer_state_code: Optional[str] = None
    customer_city: Optional[str] = None
    customer_zip: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    shipping_address_same_as_billing: bool = True
    shipping_country_code: Optional[str] = None
    shipping_state_code: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_zip: Optional[str] = None
    order_id: Optional[str] = None
    order_date: Optional[date] = None
    currency: str = "USD"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaxValidationRequest(BaseModel):
    tax_id: str
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    tax_type: Optional[TaxType] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    vat_validation: bool = True

class TaxValidationResponse(BaseModel):
    valid: bool
    tax_id: str
    country_code: str
    tax_type: Optional[TaxType] = None
    normalized_tax_id: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    vies_valid: Optional[bool] = None
    vies_name: Optional[str] = None
    vies_address: Optional[str] = None
    validation_date: Optional[datetime] = None
    message: Optional[str] = None

# API Endpoints
@router.post("/tax/calculate", response_model=TaxCalculationResult)
async def calculate_tax(
    request: Request,
    tax_calc: TaxCalculationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate tax for a given amount and jurisdiction.
    
    This endpoint calculates the tax amount based on the provided parameters.
    It supports tax exemption validation and complex tax calculations.
    """
    try:
        # Basic permission check - allow any authenticated user to calculate tax
        # Additional permission checks can be added based on user roles if needed
        
        # Log the tax calculation request for audit purposes
        logger.info(
            f"Tax calculation request from {request.client.host} - "
            f"User: {current_user.username}, Amount: {tax_calc.amount} {tax_calc.currency}, "
            f"Country: {tax_calc.country_code}, Type: {tax_calc.tax_type}"
        )
        
        # Call the tax service to calculate the tax
        result = await tax_policy_service.calculate_tax(
            amount=tax_calc.amount,
            tax_type=tax_calc.tax_type,
            country_code=tax_calc.country_code,
            state_code=tax_calc.state_code,
            city=tax_calc.city,
            is_business=tax_calc.is_business,
            tax_exempt=tax_calc.tax_exempt,
            exemption_code=tax_calc.exemption_code,
            for_date=tax_calc.for_date or date.today()
        )
        
        # Log the result for audit purposes
        logger.info(
            f"Tax calculation result - "
            f"Taxable Amount: {result.taxable_amount}, "
            f"Tax Amount: {result.tax_amount}, "
            f"Rate: {result.tax_rate_used}%"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating tax: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while calculating tax"
        )

@router.post("/tax/validate", response_model=TaxValidationResponse)
async def validate_tax_id(
    request: Request,
    validation_request: TaxValidationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate a tax ID against the relevant tax authority.
    
    This endpoint validates tax IDs (VAT, GST, etc.) against official registries
    when available, or performs format validation based on jurisdictional rules.
    """
    try:
        # Log the validation request for audit purposes
        logger.info(
            f"Tax ID validation request from {request.client.host} - "
            f"User: {current_user.username}, "
            f"Tax ID: {validation_request.tax_id}, "
            f"Country: {validation_request.country_code}"
        )
        
        # In a real implementation, this would call an external validation service
        # For now, we'll just return a mock response
        
        # Basic format validation based on country
        tax_id = validation_request.tax_id.strip().replace(" ", "").replace("-", "").replace(".", "")
        
        # Simple validation for common tax ID formats
        is_valid = False
        normalized_id = None
        vies_valid = None
        vies_name = None
        vies_address = None
        
        if validation_request.country_code == "US":
            # US EIN format: XX-XXXXXXX
            if len(tax_id) == 9 and tax_id[:2].isdigit() and tax_id[2:].isdigit():
                is_valid = True
                normalized_id = f"{tax_id[:2]}-{tax_id[2:]}"
        elif validation_request.country_code == "GB":
            # UK VAT format: GB999 9999 73 or GB999 9999 73 001
            if tax_id.upper().startswith("GB"):
                vat_num = tax_id[2:].strip()
                if 5 <= len(vat_num) <= 12 and vat_num.isdigit():
                    is_valid = True
                    normalized_id = f"GB{vat_num}"
        elif validation_request.country_code in ["DE", "FR", "IT", "ES", "NL"]:
            # European VAT format: DE123456789
            if len(tax_id) >= 3 and tax_id[:2].isalpha() and tax_id[2:].isdigit():
                is_valid = True
                normalized_id = f"{tax_id[:2].upper()}{tax_id[2:]}"
        else:
            # Generic validation for other countries
            if len(tax_id) >= 4 and any(c.isdigit() for c in tax_id):
                is_valid = True
                normalized_id = tax_id.upper()
        
        # For EU countries, we could call the VIES service to validate VAT numbers
        if validation_request.vat_validation and validation_request.country_code in [
            "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES",
            "FI", "FR", "GB", "HR", "HU", "IE", "IT", "LT", "LU", "LV",
            "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"
        ]:
            # In a real implementation, this would call the VIES SOAP service
            # For now, we'll simulate a successful validation
            vies_valid = is_valid
            if is_valid:
                vies_name = validation_request.company_name or "Example Company Ltd"
                vies_address = "123 Example St, City, Country"
        
        response = TaxValidationResponse(
            valid=is_valid,
            tax_id=validation_request.tax_id,
            country_code=validation_request.country_code,
            tax_type=validation_request.tax_type,
            normalized_tax_id=normalized_id,
            company_name=validation_request.company_name,
            address=validation_request.address,
            city=validation_request.city,
            state=validation_request.state,
            zip=validation_request.zip,
            vies_valid=vies_valid,
            vies_name=vies_name,
            vies_address=vies_address,
            validation_date=datetime.utcnow(),
            message="Validation successful" if is_valid else "Invalid tax ID format"
        )
        
        # Log the validation result for audit purposes
        logger.info(
            f"Tax ID validation result - "
            f"Valid: {response.valid}, "
            f"Normalized ID: {response.normalized_tax_id}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error validating tax ID: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while validating the tax ID"
        )

@router.get("/tax/rules", response_model=PaginatedResponse[TaxRule])
@role_required(["admin", "accountant", "tax_manager"])
async def list_tax_rules(
    request: Request,
    tax_type: Optional[TaxType] = None,
    country_code: Optional[str] = None,
    state_code: Optional[str] = None,
    city: Optional[str] = None,
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user)
):
    """
    List tax rules with filtering and pagination.
    
    This endpoint allows filtering tax rules by various criteria such as tax type,
    jurisdiction, and active status. Results are paginated for easier consumption.
    """
    try:
        # Log the request for audit purposes
        logger.info(
            f"List tax rules request from {request.client.host} - "
            f"User: {current_user.username}, "
            f"Type: {tax_type}, Country: {country_code}"
        )
        
        # Get filtered tax rules
        rules = await tax_policy_service.search_tax_rules(
            tax_type=tax_type,
            country_code=country_code,
            state_code=state_code,
            city=city,
            is_active=is_active,
            category=category,
            tags=tags
        )
        
        # Apply pagination
        total_items = len(rules)
        total_pages = (total_items + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_rules = rules[start_idx:end_idx]
        
        # Convert to response models (in a real implementation, this would map to a database model)
        response_rules = [
            TaxRuleResponse(
                id=rule.code,
                created_at=datetime.utcnow(),  # Would come from DB in a real implementation
                updated_at=datetime.utcnow(),
                created_by=current_user.username,
                updated_by=current_user.username,
                **rule.dict()
            )
            for rule in paginated_rules
        ]
        
        # Log the response for audit purposes
        logger.info(f"Returning {len(response_rules)} of {total_items} tax rules")
        
        return PaginatedResponse[
            TaxRuleResponse
        ](
            items=response_rules,
            total=total_items,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error listing tax rules: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tax rules"
        )

@router.get("/tax/rules/{rule_id}", response_model=TaxRuleResponse)
@role_required(["admin", "accountant", "tax_manager"])
async def get_tax_rule(
    request: Request,
    rule_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific tax rule by its ID.
    
    This endpoint retrieves detailed information about a specific tax rule,
    including its rates and jurisdiction information.
    """
    try:
        # Log the request for audit purposes
        logger.info(
            f"Get tax rule request from {request.client.host} - "
            f"User: {current_user.username}, Rule ID: {rule_id}"
        )
        
        # Get the tax rule
        rule = await tax_policy_service.get_tax_rule(rule_id)
        if not rule:
            logger.warning(f"Tax rule not found: {rule_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tax rule with ID '{rule_id}' not found"
            )
        
        # Convert to response model (in a real implementation, this would map to a database model)
        response = TaxRuleResponse(
            id=rule.code,
            created_at=datetime.utcnow(),  # Would come from DB in a real implementation
            updated_at=datetime.utcnow(),
            created_by=current_user.username,
            updated_by=current_user.username,
            **rule.dict()
        )
        
        # Log the response for audit purposes
        logger.info(f"Returning tax rule: {rule_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tax rule {rule_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the tax rule"
        )

@router.post("/tax/rules", response_model=TaxRuleResponse, status_code=status.HTTP_201_CREATED)
@role_required(["admin", "tax_manager"])
async def create_tax_rule(
    request: Request,
    rule_data: TaxRuleCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new tax rule.
    
    This endpoint allows administrators to define new tax rules with specific
    rates, jurisdictions, and other relevant details.
    """
    try:
        # Log the request for audit purposes
        logger.info(
            f"Create tax rule request from {request.client.host} - "
            f"User: {current_user.username}, Code: {rule_data.code}"
        )
        
        # Check if a rule with this code already exists
        existing_rule = await tax_policy_service.get_tax_rule(rule_data.code)
        if existing_rule:
            logger.warning(f"Tax rule already exists: {rule_data.code}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A tax rule with code '{rule_data.code}' already exists"
            )
        
        # In a real implementation, this would save to a database
        # For now, we'll just add it to the in-memory cache
        new_rule = TaxRule(**rule_data.dict())
        tax_policy_service.tax_rules_cache[new_rule.code] = new_rule
        
        # Log the creation for audit purposes
        logger.info(f"Created new tax rule: {new_rule.code}")
        
        # Return the created rule
        return TaxRuleResponse(
            id=new_rule.code,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=current_user.username,
            updated_by=current_user.username,
            **new_rule.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tax rule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the tax rule"
        )

@router.put("/tax/rules/{rule_id}", response_model=TaxRuleResponse)
@role_required(["admin", "tax_manager"])
async def update_tax_rule(
    request: Request,
    rule_id: str,
    rule_data: TaxRuleUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing tax rule.
    
    This endpoint allows updating the details of an existing tax rule,
    such as its name, description, active status, and metadata.
    """
    try:
        # Log the request for audit purposes
        logger.info(
            f"Update tax rule request from {request.client.host} - "
            f"User: {current_user.username}, Rule ID: {rule_id}"
        )
        
        # Get the existing rule
        existing_rule = await tax_policy_service.get_tax_rule(rule_id)
        if not existing_rule:
            logger.warning(f"Tax rule not found for update: {rule_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tax rule with ID '{rule_id}' not found"
            )
        
        # Update the rule with the provided data
        update_data = rule_data.dict(exclude_unset=True)
        updated_rule = existing_rule.copy(update=update_data)
        
        # In a real implementation, this would save to a database
        # For now, we'll just update the in-memory cache
        tax_policy_service.tax_rules_cache[rule_id] = updated_rule
        
        # Log the update for audit purposes
        logger.info(f"Updated tax rule: {rule_id}")
        
        # Return the updated rule
        return TaxRuleResponse(
            id=updated_rule.code,
            created_at=datetime.utcnow(),  # Would come from DB in a real implementation
            updated_at=datetime.utcnow(),
            created_by=current_user.username,  # Would come from DB in a real implementation
            updated_by=current_user.username,
            **updated_rule.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tax rule {rule_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the tax rule"
        )

@router.delete("/tax/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
@role_required(["admin", "tax_manager"])
async def delete_tax_rule(
    request: Request,
    rule_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a tax rule.
    
    This endpoint allows administrators to delete an existing tax rule.
    In a production environment, you might want to implement soft delete
    or archive functionality instead of permanent deletion.
    """
    try:
        # Log the request for audit purposes
        logger.info(
            f"Delete tax rule request from {request.client.host} - "
            f"User: {current_user.username}, Rule ID: {rule_id}"
        )
        
        # Check if the rule exists
        if rule_id not in tax_policy_service.tax_rules_cache:
            logger.warning(f"Tax rule not found for deletion: {rule_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tax rule with ID '{rule_id}' not found"
            )
        
        # In a real implementation, this would delete from the database
        # For now, we'll just remove it from the in-memory cache
        del tax_policy_service.tax_rules_cache[rule_id]
        
        # Log the deletion for audit purposes
        logger.info(f"Deleted tax rule: {rule_id}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tax rule {rule_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the tax rule"
        )

# Similar endpoints for TaxExemption CRUD operations would be implemented here
# Following the same pattern as the tax rules endpoints
