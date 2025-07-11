from typing import List, Optional, Dict, Any
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.security import get_password_hash, verify_password
from app.core.tax.tax_policy_service import TaxType, TaxJurisdiction

class TaxExemptionService:
    def __init__(self, db: Session):
        self.db = db
    
    def validate_exemption(
        self, 
        exemption_code: str, 
        tax_type: Optional[str] = None,
        country_code: Optional[str] = None,
        state_code: Optional[str] = None,
        for_date: Optional[date] = None
    ) -> bool:
        """
        Validate if a tax exemption code is valid for the given criteria.
        """
        if not for_date:
            for_date = date.today()
            
        exemption = crud.tax_exemption.get_by_code(self.db, code=exemption_code)
        if not exemption:
            return False
            
        # Check date validity
        if exemption.valid_from > for_date or \
           (exemption.valid_to and exemption.valid_to < for_date):
            return False
            
        # Check tax type if specified
        if tax_type and tax_type not in exemption.tax_types:
            return False
            
        # Check jurisdiction if specified
        if country_code:
            jurisdiction_match = any(
                j.get("country_code") == country_code and 
                (not state_code or j.get("state_code") == state_code)
                for j in exemption.jurisdictions
            )
            if not jurisdiction_match:
                return False
                
        return True
    
    def get_available_exemptions(
        self,
        tax_type: Optional[str] = None,
        country_code: Optional[str] = None,
        state_code: Optional[str] = None,
        company_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.TaxExemption]:
        """
        Get all active tax exemptions matching the given criteria.
        """
        query = self.db.query(models.TaxExemption).filter(
            (models.TaxExemption.valid_from <= date.today()) &
            ((models.TaxExemption.valid_to.is_(None)) | 
             (models.TaxExemption.valid_to >= date.today()))
        )
        
        if tax_type:
            query = query.filter(models.TaxExemption.tax_types.contains([tax_type]))
            
        if country_code:
            jurisdiction_filter = [{"country_code": country_code}]
            if state_code:
                jurisdiction_filter[0]["state_code"] = state_code
            query = query.filter(
                models.TaxExemption.jurisdictions.contains(jurisdiction_filter)
            )
            
        if company_id is not None:
            query = query.filter(
                (models.TaxExemption.company_id == company_id) | 
                (models.TaxExemption.company_id.is_(None))
            )
            
        return query.offset(skip).limit(limit).all()
    
    def create_exemption(
        self, 
        exemption_in: schemas.TaxExemptionCreate, 
        created_by: str
    ) -> models.TaxExemption:
        """
        Create a new tax exemption.
        """
        # Check if exemption code already exists
        if crud.tax_exemption.get_by_code(self.db, code=exemption_in.exemption_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An exemption with this code already exists."
            )
            
        return crud.tax_exemption.create_with_owner(
            self.db, 
            obj_in=exemption_in, 
            created_by=created_by
        )
    
    def update_exemption(
        self, 
        exemption_id: str,
        exemption_in: schemas.TaxExemptionUpdate, 
        updated_by: str
    ) -> models.TaxExemption:
        """
        Update an existing tax exemption.
        """
        exemption = crud.tax_exemption.get(self.db, id=exemption_id)
        if not exemption:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax exemption not found"
            )
            
        return crud.tax_exemption.update(
            self.db, 
            db_obj=exemption, 
            obj_in=exemption_in,
            updated_by=updated_by
        )
    
    def delete_exemption(self, exemption_id: str) -> models.TaxExemption:
        """
        Delete a tax exemption.
        """
        exemption = crud.tax_exemption.get(self.db, id=exemption_id)
        if not exemption:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax exemption not found"
            )
            
        return crud.tax_exemption.remove(self.db, id=exemption_id)
