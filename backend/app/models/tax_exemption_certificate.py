"""
Tax Exemption Certificate model for storing customer tax exemption certificates.
"""
from sqlalchemy import Column, String, Boolean, Date, JSON, ForeignKey, DateTime, Text
from app.models.base import GUID, JSONB
from sqlalchemy.sql import func
from app.core.db.base import Base
import uuid
from datetime import date
from typing import List, Optional, Dict, Any

class TaxExemptionCertificate(Base):
    """
    Represents a tax exemption certificate provided by a customer.
    """
    __tablename__ = "tax_exemption_certificates"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    certificate_number = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False, index=True)
    customer_tax_id = Column(String(50), nullable=True, index=True)
    customer_name = Column(String(255), nullable=False)
    
    # Certificate details
    exemption_type = Column(String(100), nullable=False)  # e.g., RESALE, GOVERNMENT, NONPROFIT, etc.
    issuing_jurisdiction = Column(String(100), nullable=True)  # Government entity that issued the certificate
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)  # None means no expiration
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Tax codes this certificate applies to (empty means all)
    tax_codes = Column(JSON, default=list, nullable=False)
    
    # Jurisdictions where this exemption is valid
    jurisdictions = Column(JSONB, default=list, nullable=False, server_default='[]')
    
    # Document reference (e.g., path to scanned document)
    document_reference = Column(String(255), nullable=True)
    
    # Metadata
    meta_data = Column(JSONB, default=dict, nullable=False, server_default='{}')
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    updated_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<TaxExemptionCertificate {self.certificate_number} for {self.customer_name}>"
    
    @property
    def is_valid(self) -> bool:
        """Check if the certificate is currently valid."""
        if not self.is_active:
            return False
            
        today = date.today()
        if self.issue_date > today:
            return False
            
        if self.expiry_date and self.expiry_date < today:
            return False
            
        return True
    
    def is_valid_for_jurisdiction(self, country_code: str, state_code: Optional[str] = None, city: Optional[str] = None) -> bool:
        """
        Check if this exemption is valid for the given jurisdiction.
        
        Args:
            country_code: 2-letter ISO country code
            state_code: State/province code (if applicable)
            city: City name (if applicable)
            
        Returns:
            bool: True if valid for the given jurisdiction
        """
        if not self.jurisdictions or not isinstance(self.jurisdictions, list):
            return True  # No jurisdiction restrictions
            
        for jurisdiction in self.jurisdictions:
            # Check country match
            if jurisdiction.get('country_code') and jurisdiction['country_code'] != country_code:
                continue
                
            # If state is specified, it must match
            if jurisdiction.get('state_code') and jurisdiction['state_code'] != state_code:
                continue
                
            # If city is specified, it must match (case-insensitive)
            if jurisdiction.get('city') and jurisdiction['city'].lower() != (city or '').lower():
                continue
                
            # All specified jurisdiction fields match
            return True
            
        return False
    
    def is_valid_for_tax_code(self, tax_code: str) -> bool:
        """Check if this exemption is valid for the given tax code."""
        if not self.tax_codes or not isinstance(self.tax_codes, list):
            return True  # No tax code restrictions
            
        return tax_code in self.tax_codes
