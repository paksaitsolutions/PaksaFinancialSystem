from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud.base import CRUDBase
from app.schemas.tax_return import TaxReturnLineItemCreate, TaxReturnLineItemUpdate


class CRUDTaxReturnLineItem(CRUDBase[
    models.TaxReturnLineItem, 
    TaxReturnLineItemCreate, 
    TaxReturnLineItemUpdate
]):
    """CRUD operations for TaxReturnLineItem model"""

    def get_by_tax_return(
        self, 
        db: Session, 
        *, 
        tax_return_id: UUID,
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.TaxReturnLineItem]:
        """
        Get line items for a specific tax return.
        
        Args:
            db: Database session
            tax_return_id: ID of the tax return
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tax return line items
        """
        return (
            db.query(self.model)
            .filter(self.model.tax_return_id == tax_return_id)
            .order_by(self.model.line_item_code.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def create_with_tax_return(
        self, 
        db: Session, 
        *, 
        obj_in: Union[TaxReturnLineItemCreate, Dict[str, Any]],
        tax_return_id: UUID
    ) -> models.TaxReturnLineItem:
        """
        Create a new tax return line item associated with a tax return.
        
        Args:
            db: Database session
            obj_in: Line item data to create
            tax_return_id: ID of the associated tax return
            
        Returns:
            The created tax return line item
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.dict(exclude_unset=True)
            
        db_obj = self.model(
            **create_data,
            tax_return_id=tax_return_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def remove_by_tax_return(
        self, 
        db: Session, 
        *, 
        tax_return_id: UUID
    ) -> int:
        """
        Remove all line items for a specific tax return.
        
        Args:
            db: Database session
            tax_return_id: ID of the tax return
            
        Returns:
            Number of line items deleted
        """
        result = (
            db.query(self.model)
            .filter(self.model.tax_return_id == tax_return_id)
            .delete()
        )
        db.commit()
        return result


# Create a singleton instance
tax_return_line_item = CRUDTaxReturnLineItem(models.TaxReturnLineItem)
