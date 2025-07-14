"""
CRUD operations for Tax Exemption Certificates.
"""
from typing import Any, Dict, List, Optional, Union, cast
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.tax_exemption_certificate import TaxExemptionCertificate
from app.schemas.tax_exemption_certificate import (
    TaxExemptionCertificateCreate,
    TaxExemptionCertificateUpdate,
)
from app.core.security import get_password_hash

class CRUDTaxExemptionCertificate(CRUDBase[TaxExemptionCertificate, TaxExemptionCertificateCreate, TaxExemptionUpdate]):
    """
    CRUD operations for Tax Exemption Certificates.
    """
    
    def get_by_certificate_number(self, db: Session, *, certificate_number: str) -> Optional[TaxExemptionCertificate]:
        """Get a certificate by its certificate number."""
        return db.query(TaxExemptionCertificate).filter(
            TaxExemptionCertificate.certificate_number == certificate_number
        ).first()
    
    def get_active_certificates(
        self,
        db: Session,
        *,
        customer_id: Optional[str] = None,
        tax_code: Optional[str] = None,
        country_code: Optional[str] = None,
        state_code: Optional[str] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TaxExemptionCertificate]:
        """
        Get active tax exemption certificates with optional filters.
        
        Args:
            db: Database session
            customer_id: Filter by customer ID
            tax_code: Filter by tax code
            country_code: Filter by country code
            state_code: Filter by state/province code
            is_active: Filter by active status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching tax exemption certificates
        """
        query = db.query(TaxExemptionCertificate)
        
        # Apply filters
        if customer_id:
            query = query.filter(TaxExemptionCertificate.customer_id == customer_id)
            
        if tax_code:
            query = query.filter(
                or_(
                    TaxExemptionCertificate.tax_codes == [],  # No tax code restrictions
                    TaxExemptionCertificate.tax_codes.contains([tax_code])
                )
            )
            
        if country_code:
            # Filter for certificates with no jurisdiction restrictions or matching country
            query = query.filter(
                or_(
                    ~TaxExemptionCertificate.jurisdictions.any(),  # No jurisdiction restrictions
                    TaxExemptionCertificate.jurisdictions.any(
                        and_(
                            or_(
                                ~TaxExemptionCertificate.jurisdictions[0].has_key('country_code'),  # type: ignore
                                TaxExemptionCertificate.jurisdictions[0]['country_code'].astext == country_code
                            ),
                            or_(
                                ~TaxExemptionCertificate.jurisdictions[0].has_key('state_code'),  # type: ignore
                                TaxExemptionCertificate.jurisdictions[0]['state_code'].astext == state_code if state_code else True
                            )
                        )
                    )
                )
            )
        
        if is_active is not None:
            query = query.filter(TaxExemptionCertificate.is_active == is_active)
            
        # Apply date-based active check
        today = date.today()
        query = query.filter(
            TaxExemptionCertificate.issue_date <= today,
            or_(
                TaxExemptionCertificate.expiry_date.is_(None),
                TaxExemptionCertificate.expiry_date >= today
            )
        )
        
        return query.offset(skip).limit(limit).all()
    
    def create_with_owner(
        self, db: Session, *, obj_in: TaxExemptionCertificateCreate, created_by: str
    ) -> TaxExemptionCertificate:
        """Create a new tax exemption certificate with owner information."""
        db_obj = TaxExemptionCertificate(
            **obj_in.dict(exclude_unset=True),
            created_by=created_by,
            updated_by=created_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: TaxExemptionCertificate, 
        obj_in: Union[TaxExemptionCertificateUpdate, Dict[str, Any]], 
        updated_by: str
    ) -> TaxExemptionCertificate:
        """Update a tax exemption certificate."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        update_data["updated_by"] = updated_by
        update_data["updated_at"] = datetime.utcnow()
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def get_valid_certificate_for_transaction(
        self,
        db: Session,
        *,
        certificate_number: str,
        customer_id: Optional[str] = None,
        tax_code: Optional[str] = None,
        country_code: Optional[str] = None,
        state_code: Optional[str] = None,
    ) -> Optional[TaxExemptionCertificate]:
        """
        Get a valid tax exemption certificate for a transaction.
        
        This method checks if a certificate is valid for the given transaction
        parameters (customer, tax code, jurisdiction).
        
        Args:
            db: Database session
            certificate_number: The certificate number to validate
            customer_id: Customer ID for validation
            tax_code: Tax code for validation
            country_code: Country code for jurisdiction validation
            state_code: State/province code for jurisdiction validation
            
        Returns:
            The valid TaxExemptionCertificate or None if not valid
        """
        # First get the certificate
        cert = self.get_by_certificate_number(db, certificate_number=certificate_number)
        if not cert or not cert.is_active:
            return None
            
        # Check if certificate is valid for this customer
        if customer_id and str(cert.customer_id) != str(customer_id):
            return None
            
        # Check if certificate is valid for this tax code (if tax code is provided)
        if tax_code and not cert.is_valid_for_tax_code(tax_code):
            return None
            
        # Check if certificate is valid for this jurisdiction (if location is provided)
        if country_code and not cert.is_valid_for_jurisdiction(country_code, state_code):
            return None
            
        return cert

# Create a singleton instance
tax_exemption_certificate = CRUDTaxExemptionCertificate(TaxExemptionCertificate)
