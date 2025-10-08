from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from app.models.tax_return import TaxReturn
from app.schemas.tax_return import TaxReturnCreate, TaxReturnUpdate
from datetime import date

class TaxReturnCRUD:
    def get(self, db: Session, id: int) -> Optional[TaxReturn]:
        return db.query(TaxReturn).filter(TaxReturn.id == id).first()

    def get_by_return_id(self, db: Session, return_id: str) -> Optional[TaxReturn]:
        return db.query(TaxReturn).filter(TaxReturn.return_id == return_id).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        tax_year: Optional[str] = None,
        return_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[TaxReturn]:
        query = db.query(TaxReturn)
        
        if tax_year:
            query = query.filter(TaxReturn.tax_year == tax_year)
        if return_type:
            query = query.filter(TaxReturn.return_type == return_type)
        if status:
            query = query.filter(TaxReturn.status == status)
            
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: TaxReturnCreate) -> TaxReturn:
        db_obj = TaxReturn(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: TaxReturn, obj_in: TaxReturnUpdate) -> TaxReturn:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> TaxReturn:
        obj = db.query(TaxReturn).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_stats(self, db: Session) -> dict:
        today = date.today()
        
        filed = db.query(TaxReturn).filter(
            TaxReturn.status.in_(["filed", "accepted"])
        ).count()
        
        pending = db.query(TaxReturn).filter(
            TaxReturn.status == "draft"
        ).count()
        
        overdue = db.query(TaxReturn).filter(
            and_(TaxReturn.status == "draft", TaxReturn.due_date < today)
        ).count()
        
        amendments = db.query(TaxReturn).filter(
            TaxReturn.status == "amended"
        ).count()
        
        return {
            "filed": filed,
            "pending": pending,
            "overdue": overdue,
            "amendments": amendments
        }

tax_return_crud = TaxReturnCRUD()