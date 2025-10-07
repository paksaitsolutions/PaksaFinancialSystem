from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.accounts_receivable.collection import Collection, CollectionActivity
from app.schemas.accounts_receivable.collection_schemas import CollectionCreate, CollectionUpdate, CollectionActivityCreate


class CollectionCRUD:
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Collection]:
        return db.query(Collection).filter(Collection.is_active == True).offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, collection_id: str) -> Optional[Collection]:
        return db.query(Collection).filter(
            and_(Collection.id == collection_id, Collection.is_active == True)
        ).first()

    def get_by_status(self, db: Session, status: str) -> List[Collection]:
        return db.query(Collection).filter(
            and_(Collection.status == status, Collection.is_active == True)
        ).all()

    def get_by_priority(self, db: Session, priority: str) -> List[Collection]:
        return db.query(Collection).filter(
            and_(Collection.priority == priority, Collection.is_active == True)
        ).all()

    def create(self, db: Session, collection_data: CollectionCreate) -> Collection:
        collection = Collection(**collection_data.model_dump())
        db.add(collection)
        db.commit()
        db.refresh(collection)
        return collection

    def update(self, db: Session, collection_id: str, collection_data: CollectionUpdate) -> Optional[Collection]:
        collection = self.get_by_id(db, collection_id)
        if not collection:
            return None
        
        update_data = collection_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(collection, field, value)
        
        db.commit()
        db.refresh(collection)
        return collection

    def delete(self, db: Session, collection_id: str) -> bool:
        collection = self.get_by_id(db, collection_id)
        if not collection:
            return False
        
        collection.is_active = False
        db.commit()
        return True


class CollectionActivityCRUD:
    def get_by_collection(self, db: Session, collection_id: str) -> List[CollectionActivity]:
        return db.query(CollectionActivity).filter(
            CollectionActivity.collection_id == collection_id
        ).order_by(desc(CollectionActivity.activity_date)).all()

    def create(self, db: Session, activity_data: CollectionActivityCreate) -> CollectionActivity:
        activity = CollectionActivity(**activity_data.model_dump())
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity


collection_crud = CollectionCRUD()
collection_activity_crud = CollectionActivityCRUD()