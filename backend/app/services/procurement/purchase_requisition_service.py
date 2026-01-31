from datetime import datetime
from typing import List, Optional, Dict, Any

from ...core.database import SessionLocal
from ...core.deps import get_current_user
from ...core.logging import logger
from ...models.user import User
from ..extended_financials.procurement.models.purchase_requisition import (
from ..extended_financials.procurement.schemas.purchase_requisition import (
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

    PurchaseRequisition, 
    RequisitionItem
)
    PurchaseRequisitionCreate,
    PurchaseRequisitionUpdate,
    PurchaseRequisitionResponse,
    RequisitionItemCreate,
    RequisitionItemUpdate,
    RequisitionStatus,
    RequisitionFilter
)

class PurchaseRequisitionService:
    """
    Service class for handling purchase requisition operations.
    """
    
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user
    
    def _generate_requisition_number(self) -> str:
        prefix = "REQ"
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        
        # Get the count of requisitions for today
        count = self.db.query(PurchaseRequisition).filter(
            PurchaseRequisition.requisition_number.like(f"{prefix}-{timestamp}-%")
        ).count()
        
        return f"{prefix}-{timestamp}-{count + 1:04d}"
    
    def _calculate_total_amount(self, items: List[RequisitionItemCreate]) -> float:
        return sum(item.quantity * item.unit_price for item in items)
    
    def create_requisition(
        self, 
        requisition_data: PurchaseRequisitionCreate
    ) -> PurchaseRequisitionResponse:
        """Create Requisition."""
        """
        Create a new purchase requisition.
        """
        try:
            # Generate requisition number
            requisition_number = self._generate_requisition_number()
            
            # Calculate total amount
            total_amount = self._calculate_total_amount(requisition_data.items)
            
            # Create requisition
            db_requisition = PurchaseRequisition(
                requisition_number=requisition_number,
                title=requisition_data.title,
                description=requisition_data.description,
                requisition_date=requisition_data.requisition_date,
                required_date=requisition_data.required_date,
                priority=requisition_data.priority,
                status=RequisitionStatus.DRAFT,
                total_amount=total_amount,
                currency=requisition_data.items[0].currency if requisition_data.items else 'USD',
                department_id=requisition_data.department_id,
                notes=requisition_data.notes,
                metadata_=requisition_data.metadata_,
                requester_id=self.current_user.id,
                created_by_id=self.current_user.id,
                updated_by_id=self.current_user.id
            )
            
            self.db.add(db_requisition)
            self.db.flush()  # To get the ID for items
            
            # Add requisition items
            for item in requisition_data.items:
                db_item = RequisitionItem(
                    requisition_id=db_requisition.id,
                    item_name=item.item_name,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.quantity * item.unit_price,
                    currency=item.currency,
                    item_code=item.item_code,
                    category_id=item.category_id,
                    project_id=item.project_id,
                    gl_account_id=item.gl_account_id,
                    status=item.status
                )
                self.db.add(db_item)
            
            self.db.commit()
            self.db.refresh(db_requisition)
            
            return db_requisition
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating purchase requisition: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create purchase requisition"
            )
    
    def get_requisition(
        self, 
        requisition_id: int
    ) -> Optional[PurchaseRequisitionResponse]:
        """Get Requisition."""
        """
        Get a purchase requisition by ID.
        """
        requisition = self.db.query(PurchaseRequisition).filter(
            PurchaseRequisition.id == requisition_id
        ).first()
        
        if not requisition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase requisition not found"
            )
            
        # Check permissions
        if (requisition.requester_id != self.current_user.id and 
            not self.current_user.is_superuser and 
            requisition.department_id not in [d.id for d in self.current_user.departments]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this requisition"
            )
            
        return requisition
    
    def list_requisitions(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[RequisitionFilter] = None
    ) -> List[PurchaseRequisitionList]:
        """List Requisitions."""
        """
        List purchase requisitions with optional filtering and pagination.
        """
        query = self.db.query(PurchaseRequisition)
        
        # Apply filters
        if filters:
            if filters.status:
                query = query.filter(PurchaseRequisition.status == filters.status)
            if filters.priority:
                query = query.filter(PurchaseRequisition.priority == filters.priority)
            if filters.requester_id:
                query = query.filter(PurchaseRequisition.requester_id == filters.requester_id)
            if filters.department_id:
                query = query.filter(PurchaseRequisition.department_id == filters.department_id)
            if filters.start_date:
                query = query.filter(PurchaseRequisition.requisition_date >= filters.start_date)
            if filters.end_date:
                query = query.filter(PurchaseRequisition.requisition_date <= filters.end_date)
            if filters.search:
                search = f"%{filters.search}%"
                query = query.filter(
                    (PurchaseRequisition.title.ilike(search)) |
                    (PurchaseRequisition.requisition_number.ilike(search)) |
                    (PurchaseRequisition.description.ilike(search))
                )
        
        # Apply permissions
        if not self.current_user.is_superuser:
            # Users can see their own requisitions or those from their departments
            query = query.filter(
                (PurchaseRequisition.requester_id == self.current_user.id) |
                (PurchaseRequisition.department_id.in_(
                    [d.id for d in self.current_user.departments]
                ) if hasattr(self.current_user, 'departments') else False)
            )
        
        # Apply pagination
        return query.offset(skip).limit(limit).all()
    
    def update_requisition(
        self, 
        requisition_id: int, 
        requisition_data: PurchaseRequisitionUpdate
    ) -> PurchaseRequisitionResponse:
        """Update Requisition."""
        """
        Update a purchase requisition.
        """
        db_requisition = self.get_requisition(requisition_id)
        
        # Check if requisition can be modified
        if db_requisition.status not in [RequisitionStatus.DRAFT, RequisitionStatus.REJECTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify a requisition that is not in draft or rejected status"
            )
        
        # Update fields
        update_data = requisition_data.dict(exclude_unset=True)
        
        # Handle items update if provided
        if 'items' in update_data:
            # Delete existing items
            self.db.query(RequisitionItem).filter(
                RequisitionItem.requisition_id == db_requisition.id
            ).delete()
            
            # Add updated items
            for item in requisition_data.items:
                db_item = RequisitionItem(
                    requisition_id=db_requisition.id,
                    **item.dict()
                )
                self.db.add(db_item)
            
            # Recalculate total amount
            total_amount = self._calculate_total_amount(requisition_data.items)
            db_requisition.total_amount = total_amount
            
            # Update currency from items if changed
            if requisition_data.items:
                db_requisition.currency = requisition_data.items[0].currency
        
        # Update other fields
        for field, value in update_data.items():
            if field != 'items' and hasattr(db_requisition, field):
                setattr(db_requisition, field, value)
        
        # Update audit fields
        db_requisition.updated_at = datetime.utcnow()
        db_requisition.updated_by_id = self.current_user.id
        
        try:
            self.db.commit()
            self.db.refresh(db_requisition)
            return db_requisition
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating purchase requisition: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update purchase requisition"
            )
    
    def submit_requisition(
        self, 
        requisition_id: int
    ) -> PurchaseRequisitionResponse:
        """Submit Requisition."""
        """
        Submit a draft requisition for approval.
        """
        db_requisition = self.get_requisition(requisition_id)
        
        # Check if requisition can be submitted
        if db_requisition.status != RequisitionStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft requisitions can be submitted"
            )
        
        # Update status
        db_requisition.status = RequisitionStatus.SUBMITTED
        db_requisition.updated_at = datetime.utcnow()
        db_requisition.updated_by_id = self.current_user.id
        
        try:
            self.db.commit()
            self.db.refresh(db_requisition)
            
            
            return db_requisition
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error submitting purchase requisition: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit purchase requisition"
            )
    
    def approve_requisition(
        self, 
        requisition_id: int,
        approval_data: RequisitionApproval
    ) -> PurchaseRequisitionResponse:
        """Approve Requisition."""
        """
        Approve or reject a submitted requisition.
        """
        db_requisition = self.get_requisition(requisition_id)
        
        # Check if requisition can be approved/rejected
        if db_requisition.status != RequisitionStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only submitted requisitions can be approved or rejected"
            )
        
        # Check if user has permission to approve
        if not self.current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to approve requisitions"
            )
        
        # Update status
        db_requisition.status = (
            RequisitionStatus.APPROVED if approval_data.approved 
            else RequisitionStatus.REJECTED
        )
        db_requisition.approver_id = self.current_user.id
        db_requisition.notes = approval_data.notes
        db_requisition.updated_at = datetime.utcnow()
        db_requisition.updated_by_id = self.current_user.id
        
        try:
            self.db.commit()
            self.db.refresh(db_requisition)
            
            
            return db_requisition
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing requisition approval: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process requisition approval"
            )
    
    def delete_requisition(
        self, 
        requisition_id: int
    ) -> bool:
        """Delete Requisition."""
        """
        Delete a purchase requisition.
        """
        db_requisition = self.get_requisition(requisition_id)
        
        # Check if requisition can be deleted
        if db_requisition.status != RequisitionStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft requisitions can be deleted"
            )
        
        # Check permissions
        if (db_requisition.requester_id != self.current_user.id and 
            not self.current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this requisition"
            )
        
        try:
            # Delete items first (cascade should handle this, but being explicit)
            self.db.query(RequisitionItem).filter(
                RequisitionItem.requisition_id == db_requisition.id
            ).delete()
            
            # Delete requisition
            self.db.delete(db_requisition)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting purchase requisition: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete purchase requisition"
            )
