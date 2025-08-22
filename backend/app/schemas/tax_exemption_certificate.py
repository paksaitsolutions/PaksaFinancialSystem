"""
Pydantic models for Tax Exemption Certificates.
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4

from app.schemas.base import BaseSchema

class JurisdictionBase(BaseModel):
    """Base model for jurisdiction information."""
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    state_code: Optional[str] = Field(None, min_length=2, max_length=10, description="State/province code")
    city: Optional[str] = Field(None, max_length=100, description="City name")
    
    @validator('country_code')
    def country_code_upper(cls, v):
        return v.upper()
    
    @validator('state_code')
    def state_code_upper(cls, v):
        return v.upper() if v else v

class TaxExemptionCertificateBase(BaseModel):
    """Base model for tax exemption certificates."""
    certificate_number: str = Field(..., max_length=100, description="Unique certificate number")
    customer_id: UUID = Field(..., description="ID of the customer this certificate belongs to")
    customer_tax_id: Optional[str] = Field(None, max_length=50, description="Customer's tax ID number")
    customer_name: str = Field(..., max_length=255, description="Name of the customer")
    
    # Certificate details
    exemption_type: str = Field(..., max_length=100, description="Type of exemption (e.g., RESALE, GOVERNMENT, NONPROFIT)")
    issuing_jurisdiction: Optional[str] = Field(None, max_length=100, description="Government entity that issued the certificate")
    issue_date: date = Field(..., description="Date when the certificate was issued")
    expiry_date: Optional[date] = Field(None, description="Expiration date of the certificate (if any)")
    is_active: bool = Field(True, description="Whether the certificate is currently active")
    
    # Tax codes this certificate applies to (empty means all)
    tax_codes: List[str] = Field(default_factory=list, description="List of tax codes this exemption applies to")
    
    # Jurisdictions where this exemption is valid
    jurisdictions: List[JurisdictionBase] = Field(
        default_factory=list,
        description="List of jurisdictions where this exemption is valid"
    )
    
    # Document reference
    document_reference: Optional[str] = Field(None, max_length=255, description="Reference to the document (e.g., file path)")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    notes: Optional[str] = Field(None, description="Additional notes or comments")
    
    @validator('tax_codes', each_item=True)
    def validate_tax_codes(cls, v):
        if not isinstance(v, str):
            raise ValueError("Tax codes must be strings")
        return v.upper()
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if v and 'issue_date' in values and v < values['issue_date']:
            raise ValueError("Expiry date must be after issue date")
        return v

class TaxExemptionCertificateCreate(TaxExemptionCertificateBase):
    """Model for creating a new tax exemption certificate."""
    pass

class TaxExemptionCertificateUpdate(BaseModel):
    """Model for updating an existing tax exemption certificate."""
    customer_tax_id: Optional[str] = Field(None, max_length=50, description="Customer's tax ID number")
    customer_name: Optional[str] = Field(None, max_length=255, description="Name of the customer")
    exemption_type: Optional[str] = Field(None, max_length=100, description="Type of exemption")
    issuing_jurisdiction: Optional[str] = Field(None, max_length=100, description="Government entity that issued the certificate")
    issue_date: Optional[date] = Field(None, description="Date when the certificate was issued")
    expiry_date: Optional[date] = Field(None, description="Expiration date of the certificate (if any)")
    is_active: Optional[bool] = Field(None, description="Whether the certificate is currently active")
    tax_codes: Optional[List[str]] = Field(None, description="List of tax codes this exemption applies to")
    jurisdictions: Optional[List[JurisdictionBase]] = Field(None, description="List of jurisdictions where this exemption is valid")
    document_reference: Optional[str] = Field(None, max_length=255, description="Reference to the document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    notes: Optional[str] = Field(None, description="Additional notes or comments")

class TaxExemptionCertificateInDBBase(TaxExemptionCertificateBase, BaseSchema):
    """Base model for tax exemption certificates in the database."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    created_by: UUID = Field(..., description="ID of the user who created the record")
    updated_by: Optional[UUID] = Field(None, description="ID of the user who last updated the record")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        orm_mode = True

class TaxExemptionCertificate(TaxExemptionCertificateInDBBase):
    """Model for tax exemption certificates returned to the client."""
    pass

class TaxExemptionCertificateInDB(TaxExemptionCertificateInDBBase):
    """Model for tax exemption certificates in the database."""
    pass

class TaxExemptionCertificateSearchResults(BaseModel):
    """Model for search results of tax exemption certificates."""
    results: List[TaxExemptionCertificate] = Field(..., description="List of matching tax exemption certificates")
    total: int = Field(..., description="Total number of results")
    skip: int = Field(0, description="Number of results skipped")
    limit: int = Field(100, description="Maximum number of results returned")
