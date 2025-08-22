from typing import Any, Dict, List, Optional, Union
from datetime import date, datetime
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.tax_exemption import TaxExemption
from app.schemas.tax_exemption import TaxExemptionCreate, TaxExemptionUpdate
from app.core.security import get_password_hash

class CRUDTaxExemption(CRUDBase[TaxExemption, TaxExemptionCreate, TaxExemptionUpdate]):
    def get_by_code(self, db: Session, *, code: str) -> Optional[TaxExemption]:
        return db.query(TaxExemption).filter(TaxExemption.exemption_code == code).first()
    
    def get_active(
        self, db: Session, *, 
        skip: int = 0, 
        limit: int = 100,
        tax_type: Optional[str] = None,
        country_code: Optional[str] = None,
        state_code: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> List[TaxExemption]:
        query = db.query(TaxExemption).filter(
            (TaxExemption.valid_from <= date.today()) &
            ((TaxExemption.valid_to.is_(None)) | (TaxExemption.valid_to >= date.today()))
        )
        
        if tax_type:
            query = query.filter(TaxExemption.tax_types.contains([tax_type]))
            
        if country_code:
            query = query.filter(TaxExemption.jurisdictions.any({"country_code": country_code}))
            
        if state_code:
            query = query.filter(TaxExemption.jurisdictions.any({"state_code": state_code}))
            
        if company_id:
            query = query.filter(
                (TaxExemption.company_id == company_id) | 
                (TaxExemption.company_id.is_(None))
            )
        
        return query.offset(skip).limit(limit).all()
    
    def create_with_owner(
        self, db: Session, *, obj_in: TaxExemptionCreate, created_by: str
    ) -> TaxExemption:
        db_obj = TaxExemption(
            **obj_in.dict(exclude_unset=True),
            created_by=created_by,
            updated_by=created_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: TaxExemption, obj_in: Union[TaxExemptionUpdate, Dict[str, Any]], updated_by: str
    ) -> TaxExemption:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        update_data["updated_by"] = updated_by
        update_data["updated_at"] = datetime.utcnow()
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)

tax_exemption = CRUDTaxExemption(TaxExemption)
