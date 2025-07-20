from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, or_, func, text, select
from sqlalchemy.orm import Session, joinedload, aliased, selectinload

from app import models, schemas
from app.core.security import get_password_hash
from app.crud.base import CRUDBase
from app.schemas.tax_return import (
    TaxReturnFilter,
    TaxReturnStatus,
    TaxReturnType,
    TaxFilingFrequency,
)
from app.schemas.tax_return_line_item import TaxReturnLineItemCreate, TaxReturnLineItemUpdate


class CRUDTaxReturn(CRUDBase[models.TaxReturn, schemas.TaxReturnCreate, schemas.TaxReturnUpdate]):
    """CRUD operations for TaxReturn model"""

    def get_by_id(
        self, 
        db: Session, 
        *, 
        id: UUID, 
        company_id: Optional[UUID] = None
    ) -> Optional[models.TaxReturn]:
        """Get a tax return by ID with optional company filter"""
        query = db.query(self.model).filter(self.model.id == id)
        if company_id:
            query = query.filter(self.model.company_id == company_id)
        return query.first()

    def get_by_period(
        self,
        db: Session,
        *,
        company_id: UUID,
        return_type: str,
        jurisdiction_code: str,
        period_start: date,
        period_end: date,
        status: Optional[TaxReturnStatus] = None,
    ) -> Optional[models.TaxReturn]:
        """
        Get a tax return for a specific period, jurisdiction, and type.
        
        Args:
            db: Database session
            company_id: Company ID
            return_type: Type of tax return (e.g., 'vat', 'gst')
            jurisdiction_code: Tax jurisdiction code
            period_start: Start date of the tax period
            period_end: End date of the tax period
            status: Optional status filter
            
        Returns:
            The matching tax return or None if not found
        """
        query = db.query(self.model).filter(
            self.model.company_id == company_id,
            self.model.return_type == return_type,
            self.model.jurisdiction_code == jurisdiction_code,
            self.model.tax_period_start == period_start,
            self.model.tax_period_end == period_end,
        )
        
        if status:
            if isinstance(status, list):
                query = query.filter(self.model.status.in_(status))
            else:
                query = query.filter(self.model.status == status)
                
        return query.first()
        
    def get_upcoming_due_returns(
        self,
        db: Session,
        *,
        company_id: UUID,
        days_ahead: int = 30,
        include_overdue: bool = True,
        return_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None,
    ) -> List[models.TaxReturn]:
        """
        Get tax returns that are due within the specified number of days.
        
        Args:
            db: Database session
            company_id: Company ID
            days_ahead: Number of days to look ahead for due dates
            include_overdue: Whether to include overdue returns
            return_types: Optional list of return types to filter by
            jurisdiction_codes: Optional list of jurisdiction codes to filter by
            
        Returns:
            List of upcoming or overdue tax returns
        """
        today = datetime.utcnow().date()
        end_date = today + timedelta(days=days_ahead)
        
        query = db.query(self.model).filter(
            self.model.company_id == company_id,
            self.model.status.in_([
                TaxReturnStatus.DRAFT,
                TaxReturnStatus.PENDING_APPROVAL,
                TaxReturnStatus.APPROVED,
            ])
        )
        
        # Filter by due date
        if include_overdue:
            query = query.filter(self.model.due_date <= end_date)
        else:
            query = query.filter(self.model.due_date.between(today, end_date))
            
        # Apply additional filters
        if return_types:
            query = query.filter(self.model.return_type.in_(return_types))
            
        if jurisdiction_codes:
            query = query.filter(self.model.jurisdiction_code.in_(jurisdiction_codes))
            
        # Order by due date (earliest first)
        query = query.order_by(self.model.due_date.asc())
        
        return query.all()
        
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        company_id: Optional[UUID] = None,
        filter_params: Optional[TaxReturnFilter] = None
    ) -> List[models.TaxReturn]:
        """Get multiple tax returns with optional filtering"""
        query = db.query(self.model)
        
        if company_id:
            query = query.filter(self.model.company_id == company_id)
            
        if filter_params:
            if filter_params.status:
                query = query.filter(self.model.status == filter_params.status)
            if filter_params.return_type:
                query = query.filter(self.model.return_type == filter_params.return_type)
            if filter_params.filing_frequency:
                query = query.filter(self.model.filing_frequency == filter_params.filing_frequency)
            if filter_params.tax_period_start:
                query = query.filter(self.model.tax_period_start >= filter_params.tax_period_start)
            if filter_params.tax_period_end:
                query = query.filter(self.model.tax_period_end <= filter_params.tax_period_end)
            if filter_params.jurisdiction_code:
                query = query.filter(self.model.jurisdiction_code == filter_params.jurisdiction_code)
            if filter_params.search:
                search = f"%{filter_params.search}%"
                query = query.filter(
                    or_(
                        self.model.filing_reference.ilike(search),
                        self.model.confirmation_number.ilike(search),
                        self.model.notes.ilike(search)
                    )
                )
        
        return query.order_by(self.model.due_date.desc()).offset(skip).limit(limit).all()
    
    def get_upcoming_filings(
        self,
        db: Session,
        *, 
        company_id: UUID,
        days_ahead: int = 30,
        include_overdue: bool = True
    ) -> List[models.TaxReturn]:
        """Get upcoming tax filings due within the specified number of days"""
        today = date.today()
        end_date = today + datetime.timedelta(days=days_ahead)
        
        query = db.query(self.model).filter(
            self.model.company_id == company_id,
            self.model.status.in_([TaxReturnStatus.DRAFT, TaxReturnStatus.PENDING_APPROVAL]),
            self.model.due_date.between(today, end_date)
        )
        
        if include_overdue:
            query = query.union(
                db.query(self.model).filter(
                    self.model.company_id == company_id,
                    self.model.status == TaxReturnStatus.OVERDUE
                )
            )
            
        return query.order_by(self.model.due_date).all()
    
    def get_with_line_items(
        self,
        db: Session,
        *,
        id: UUID,
        company_id: Optional[UUID] = None,
        include_line_items: bool = True
    ) -> Optional[models.TaxReturn]:
        """
        Get a tax return by ID with its line items.
        
        Args:
            db: Database session
            id: Tax return ID
            company_id: Optional company ID for additional filtering
            include_line_items: Whether to include line items in the result
            
        Returns:
            The tax return with line items if found, None otherwise
        """
        query = db.query(self.model).filter(self.model.id == id)
        
        if company_id:
            query = query.filter(self.model.company_id == company_id)
            
        if include_line_items:
            query = query.options(selectinload(self.model.line_items))
            
        return query.first()
        
    def get_line_items(
        self,
        db: Session,
        *,
        tax_return_id: UUID,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[UUID] = None,
    ) -> Tuple[List[models.TaxReturnLineItem], int]:
        """
        Get line items for a specific tax return with pagination.
        
        Args:
            db: Database session
            tax_return_id: ID of the tax return
            skip: Number of records to skip
            limit: Maximum number of records to return
            company_id: Optional company ID for additional filtering
            
        Returns:
            Tuple of (list of line items, total count)
        """
        # First verify the tax return exists and belongs to the company if specified
        query = db.query(self.model).filter(self.model.id == tax_return_id)
        if company_id:
            query = query.filter(self.model.company_id == company_id)
            
        tax_return = query.first()
        if not tax_return:
            return [], 0
            
        # Now get the line items
        line_items_query = db.query(models.TaxReturnLineItem).filter(
            models.TaxReturnLineItem.tax_return_id == tax_return_id
        )
        
        total = line_items_query.count()
        items = line_items_query.offset(skip).limit(limit).all()
        
        return items, total
        
    def add_line_item(
        self,
        db: Session,
        *,
        tax_return_id: UUID,
        line_item_in: TaxReturnLineItemCreate,
        user_id: Optional[UUID] = None
    ) -> models.TaxReturnLineItem:
        """
        Add a line item to a tax return.
        
        Args:
            db: Database session
            tax_return_id: ID of the tax return
            line_item_in: Line item data
            user_id: ID of the user adding the line item
            
        Returns:
            The created line item
        """
        # Verify the tax return exists
        tax_return = self.get(db=db, id=tax_return_id)
        if not tax_return:
            raise ValueError(f"Tax return with ID {tax_return_id} not found")
            
        # Create the line item
        line_item = models.TaxReturnLineItem(
            **line_item_in.dict(exclude={"tax_return_id"}),
            tax_return_id=tax_return_id,
            created_by=user_id,
            updated_by=user_id,
        )
        
        db.add(line_item)
        db.commit()
        db.refresh(line_item)
        
        # Update tax return totals
        self._update_tax_return_totals(db, tax_return)
        
        return line_item
        
    def update_line_item(
        self,
        db: Session,
        *,
        line_item_id: UUID,
        line_item_in: TaxReturnLineItemUpdate,
        user_id: Optional[UUID] = None
    ) -> Optional[models.TaxReturnLineItem]:
        """
        Update a line item.
        
        Args:
            db: Database session
            line_item_id: ID of the line item to update
            line_item_in: Updated line item data
            user_id: ID of the user updating the line item
            
        Returns:
            The updated line item if found, None otherwise
        """
        line_item = db.query(models.TaxReturnLineItem).get(line_item_id)
        if not line_item:
            return None
            
        # Update fields from the input
        for field, value in line_item_in.dict(exclude_unset=True).items():
            setattr(line_item, field, value)
            
        if user_id:
            line_item.updated_by = user_id
            line_item.updated_at = datetime.utcnow()
            
        db.add(line_item)
        db.commit()
        
        # Update tax return totals
        tax_return = self.get(db=db, id=line_item.tax_return_id)
        if tax_return:
            self._update_tax_return_totals(db, tax_return)
            
        db.refresh(line_item)
        return line_item
        
    def remove_line_item(
        self,
        db: Session,
        *,
        line_item_id: UUID
    ) -> bool:
        """
        Remove a line item.
        
        Args:
            db: Database session
            line_item_id: ID of the line item to remove
            
        Returns:
            True if the line item was deleted, False otherwise
        """
        # Get the line item to get the tax return ID
        line_item = db.query(models.TaxReturnLineItem).get(line_item_id)
        if not line_item:
            return False
            
        tax_return_id = line_item.tax_return_id
        
        # Delete the line item
        result = db.query(models.TaxReturnLineItem).filter(
            models.TaxReturnLineItem.id == line_item_id
        ).delete(synchronize_session=False)
        
        if result > 0:
            # Update tax return totals
            tax_return = self.get(db=db, id=tax_return_id)
            if tax_return:
                self._update_tax_return_totals(db, tax_return)
            
            db.commit()
            return True
            
        return False
        
    def get_tax_return_summary(
        self,
        db: Session,
        *,
        tax_return_id: UUID,
        company_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get a summary of a tax return including line item totals.
        
        Args:
            db: Database session
            tax_return_id: ID of the tax return
            company_id: Optional company ID for additional filtering
            
        Returns:
            Dictionary containing the tax return summary
        """
        # Get the tax return with line items
        query = db.query(self.model).filter(self.model.id == tax_return_id)
        if company_id:
            query = query.filter(self.model.company_id == company_id)
            
        tax_return = query.options(selectinload(self.model.line_items)).first()
        if not tax_return:
            return {}
            
        # Calculate line item totals
        taxable_amount = 0
        tax_amount = 0
        total_amount = 0
        
        for item in tax_return.line_items:
            taxable_amount += item.taxable_amount or 0
            tax_amount += item.tax_amount or 0
            total_amount += item.total_amount or 0
            
        return {
            "tax_return": tax_return,
            "summary": {
                "taxable_amount": taxable_amount,
                "tax_amount": tax_amount,
                "total_amount": total_amount,
                "line_item_count": len(tax_return.line_items)
            },
            "line_items": tax_return.line_items
        }
        
    def create_with_line_items(
        self, 
        db: Session, 
        *, 
        obj_in: schemas.TaxReturnCreate,
        company_id: UUID,
        user_id: UUID
    ) -> models.TaxReturn:
        """Create a new tax return with line items"""
        db_obj = models.TaxReturn(
            **obj_in.dict(exclude={"line_items"}, exclude_none=True),
            company_id=company_id,
            created_by=user_id,
            status=TaxReturnStatus.DRAFT,
            total_taxable_amount={},
            total_tax_amount={},
            total_paid_amount={"USD": 0.0},
            total_due_amount={}
        )
        
        db.add(db_obj)
        db.flush()  # To get the ID for line items
        
        # Add line items
        if obj_in.line_items:
            self._process_line_items(db, db_obj, obj_in.line_items)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create(
        self, 
        db: Session, 
        *, 
        obj_in: Union[schemas.TaxReturnCreate, Dict[str, Any]]
    ) -> models.TaxReturn:
        """
        Create a new tax return.
        
        Args:
            db: Database session
            obj_in: Tax return data to create
            
        Returns:
            The created tax return
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.dict(exclude_unset=True)
            
        # Ensure required fields are present
        required_fields = [
            'company_id', 'return_type', 'tax_period_start', 
            'tax_period_end', 'jurisdiction_code', 'created_by'
        ]
        for field in required_fields:
            if field not in create_data:
                raise ValueError(f"Missing required field: {field}")
                
        # Set default status if not provided
        if 'status' not in create_data:
            create_data['status'] = TaxReturnStatus.DRAFT
            
        # Create the tax return
        db_obj = self.model(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_with_line_items(
        self,
        db: Session,
        *,
        db_obj: models.TaxReturn,
        obj_in: Union[schemas.TaxReturnUpdate, Dict[str, Any]],
        user_id: UUID
    ) -> models.TaxReturn:
        """Update a tax return with line items"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Handle status changes
        if "status" in update_data:
            if update_data["status"] == TaxReturnStatus.APPROVED:
                update_data["approved_by"] = user_id
                update_data["approved_at"] = datetime.utcnow()
            elif update_data["status"] == TaxReturnStatus.FILED:
                update_data["filed_by"] = user_id
                update_data["filed_at"] = datetime.utcnow()
        
        # Update the tax return
        obj_data = jsonable_encoder(db_obj)
        for field in obj_data:
            if field in update_data and field not in ["line_items"]:
                setattr(db_obj, field, update_data[field])
        
        # Update line items if provided
        if "line_items" in update_data and update_data["line_items"] is not None:
            # Delete existing line items
            db.query(models.TaxReturnLineItem).filter(
                models.TaxReturnLineItem.tax_return_id == db_obj.id
            ).delete(synchronize_session=False)
            
            # Add new line items
            self._process_line_items(db, db_obj, update_data["line_items"])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def _process_line_items(
        self,
        db: Session,
        tax_return: models.TaxReturn,
        line_items: List[schemas.TaxReturnLineItemCreate]
    ) -> None:
        """Process and save line items for a tax return"""
        # Delete existing line items
        db.query(models.TaxReturnLineItem).filter(
            models.TaxReturnLineItem.tax_return_id == tax_return.id
        ).delete(synchronize_session=False)
        
        # Add new line items
        for item in line_items:
            db_item = models.TaxReturnLineItem(
                tax_return_id=tax_return.id,
                **item.dict(exclude_none=True)
            )
            db.add(db_item)
        
        # Update tax return totals
        self._update_tax_return_totals(db, tax_return)
    
    def _update_tax_return_totals(
        self,
        db: Session,
        tax_return: models.TaxReturn
    ) -> None:
        """Update the totals for a tax return based on its line items"""
        # Get all line items for this tax return
        line_items = db.query(models.TaxReturnLineItem).filter(
            models.TaxReturnLineItem.tax_return_id == tax_return.id
        ).all()
        
        # Calculate totals
        total_taxable = {}
        total_tax = {}
        
        for item in line_items:
            # Update taxable amount
            if item.taxable_amount is not None:
                currency = item.currency or "USD"
                total_taxable[currency] = total_taxable.get(currency, 0) + item.taxable_amount
                
            # Update tax amount
            if item.tax_amount is not None:
                currency = item.currency or "USD"
                total_tax[currency] = total_tax.get(currency, 0) + item.tax_amount
        
        # Update tax return with new totals
        tax_return.total_taxable_amount = total_taxable or {
            tax_return.currency or "USD": 0.0
        }
        tax_return.total_tax_amount = total_tax or {
            tax_return.currency or "USD": 0.0
        }
        
        # Calculate due amount
        total_due = {}
        for currency in set(total_tax.keys()) | set(tax_return.total_paid_amount.keys()):
            total_due[currency] = total_tax.get(currency, 0) - tax_return.total_paid_amount.get(currency, 0)
        
        tax_return.total_due_amount = total_due or {
            tax_return.currency or "USD": 0.0
        }
        
        # Save changes
        db.add(tax_return)
        db.commit()
        db.refresh(tax_return)
    
    def get_filing_calendar(
        self,
        db: Session,
        *,
        company_id: UUID,
        start_date: date,
        end_date: date,
        statuses: Optional[List[TaxReturnStatus]] = None
    ) -> List[models.TaxReturn]:
        """Get tax returns for the filing calendar view"""
        query = db.query(self.model).filter(
            self.model.company_id == company_id,
            self.model.due_date.between(start_date, end_date)
        )
        
        if statuses:
            query = query.filter(self.model.status.in_(statuses))
            
        return query.order_by(self.model.due_date).all()
    
    def get_return_types_for_company(
        self,
        db: Session,
        *,
        company_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get distinct return types used by a company"""
        return db.query(
            models.TaxReturn.return_type,
            models.TaxReturn.filing_frequency,
            models.TaxReturn.jurisdiction_code
        ).filter(
            models.TaxReturn.company_id == company_id
        ).distinct().all()
    
    def get_jurisdictions_for_company(
        self,
        db: Session,
        *,
        company_id: UUID
    ) -> List[str]:
        """Get distinct jurisdictions for a company's tax returns"""
        return [
            result[0] for result in db.query(
                models.TaxReturn.jurisdiction_code
            ).filter(
                models.TaxReturn.company_id == company_id
            ).distinct().all()
        ]


    def get_tax_summary(
        self,
        db: Session,
        *,
        company_id: UUID,
        start_date: date,
        end_date: date,
        return_type: Optional[str] = None,
        jurisdiction_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get a summary of tax data for the specified period.
        
        Args:
            db: Database session
            company_id: Company ID
            start_date: Start date of the period
            end_date: End date of the period
            return_type: Optional return type filter
            jurisdiction_code: Optional jurisdiction code filter
            
        Returns:
            Dictionary with tax summary data
        """
        # Base query
        query = db.query(
            models.TaxReturn.return_type,
            models.TaxReturn.jurisdiction_code,
            func.sum(models.TaxReturn.total_tax_amount).label("total_tax"),
            func.sum(models.TaxReturn.total_paid_amount).label("total_paid"),
            func.count(models.TaxReturn.id).label("return_count"),
        ).filter(
            models.TaxReturn.company_id == company_id,
            models.TaxReturn.tax_period_start >= start_date,
            models.TaxReturn.tax_period_end <= end_date,
        )
        
        # Apply filters
        if return_type:
            query = query.filter(models.TaxReturn.return_type == return_type)
            
        if jurisdiction_code:
            query = query.filter(models.TaxReturn.jurisdiction_code == jurisdiction_code)
            
        # Group and order results
        query = query.group_by(
            models.TaxReturn.return_type,
            models.TaxReturn.jurisdiction_code,
        ).order_by(
            models.TaxReturn.return_type,
            models.TaxReturn.jurisdiction_code,
        )
        
        # Execute query and format results
        results = query.all()
        
        summary = {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_tax_due": 0.0,
            "total_tax_paid": 0.0,
            "total_returns": 0,
            "by_return_type": {},
            "by_jurisdiction": {},
        }
        
        for row in results:
            return_type = row.return_type
            jurisdiction = row.jurisdiction_code
            tax_amount = float(row.total_tax or 0)
            paid_amount = float(row.total_paid or 0)
            return_count = row.return_count or 0
            
            # Update totals
            summary["total_tax_due"] += tax_amount
            summary["total_tax_paid"] += paid_amount
            summary["total_returns"] += return_count
            
            # Group by return type
            if return_type not in summary["by_return_type"]:
                summary["by_return_type"][return_type] = {
                    "total_tax_due": 0.0,
                    "total_tax_paid": 0.0,
                    "return_count": 0,
                }
                
            summary["by_return_type"][return_type]["total_tax_due"] += tax_amount
            summary["by_return_type"][return_type]["total_tax_paid"] += paid_amount
            summary["by_return_type"][return_type]["return_count"] += return_count
            
            # Group by jurisdiction
            if jurisdiction not in summary["by_jurisdiction"]:
                summary["by_jurisdiction"][jurisdiction] = {
                    "total_tax_due": 0.0,
                    "total_tax_paid": 0.0,
                    "return_count": 0,
                }
                
            summary["by_jurisdiction"][jurisdiction]["total_tax_due"] += tax_amount
            summary["by_jurisdiction"][jurisdiction]["total_tax_paid"] += paid_amount
            summary["by_jurisdiction"][jurisdiction]["return_count"] += return_count
            
        return summary


tax_return = CRUDTaxReturn(models.TaxReturn)
