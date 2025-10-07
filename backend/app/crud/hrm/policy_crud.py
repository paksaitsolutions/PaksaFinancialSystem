from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.hrm.policy import HRPolicy
from app.schemas.hrm.policy_schemas import PolicyCreate, PolicyUpdate


class PolicyCRUD:
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[HRPolicy]:
        return db.query(HRPolicy).filter(HRPolicy.is_active == True).offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, policy_id: str) -> Optional[HRPolicy]:
        return db.query(HRPolicy).filter(
            and_(HRPolicy.id == policy_id, HRPolicy.is_active == True)
        ).first()

    def create(self, db: Session, policy_data: PolicyCreate, created_by: Optional[str] = None) -> HRPolicy:
        policy = HRPolicy(**policy_data.model_dump())
        if created_by:
            policy.created_by = created_by
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    def update(self, db: Session, policy_id: str, policy_data: PolicyUpdate) -> Optional[HRPolicy]:
        policy = self.get_by_id(db, policy_id)
        if not policy:
            return None
        
        update_data = policy_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)
        
        db.commit()
        db.refresh(policy)
        return policy

    def delete(self, db: Session, policy_id: str) -> bool:
        policy = self.get_by_id(db, policy_id)
        if not policy:
            return False
        
        policy.is_active = False
        db.commit()
        return True


policy_crud = PolicyCRUD()