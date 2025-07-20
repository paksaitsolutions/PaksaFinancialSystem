import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.deps import get_current_active_user, get_db
from app.core.tax.tax_filing_service import TaxFilingService
from app.core.tax.tax_return_generator import TaxReturnGenerator
from app.schemas.tax_return import (
    TaxFilingCalendarResponse,
    TaxFilingFrequency,
    TaxReturnCreate,
    TaxReturnEfileResponse,
    TaxReturnFilter,
    TaxReturnInDB,
    TaxReturnListResponse,
    TaxReturnResponse,
    TaxReturnStatus,
    TaxReturnSubmitRequest,
    TaxReturnUpdate,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=TaxReturnListResponse)
def list_tax_returns(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    status: Optional[TaxReturnStatus] = None,
    return_type: Optional[str] = None,
    filing_frequency: Optional[TaxFilingFrequency] = None,
    jurisdiction_code: Optional[str] = None,
    search: Optional[str] = None,
) -> Any:
    """
    Retrieve tax returns with optional filtering.
    """
    # Only allow admin users to access all returns
    if not current_user.is_superuser and not crud.user.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access tax returns",
        )
    
    # Build filter
    filter_params = TaxReturnFilter(
        status=status,
        return_type=return_type,
        filing_frequency=filing_frequency,
        jurisdiction_code=jurisdiction_code,
        search=search
    )
    
    # Get tax returns with filtering
    tax_returns = crud.tax_return.get_multi(
        db,
        skip=skip,
        limit=limit,
        company_id=current_user.company_id,
        filter_params=filter_params
    )
    
    # Get total count for pagination
    total = crud.tax_return.count(
        db,
        company_id=current_user.company_id,
        filter_params=filter_params
    )
    
    return {
        "data": tax_returns,
        "total": total,
        "page": skip // limit + 1,
        "limit": limit,
    }


@router.post("/generate", response_model=schemas.TaxReturnResponse, status_code=status.HTTP_201_CREATED)
async def generate_tax_return(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    tax_return_in: schemas.TaxReturnGenerate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Generate a new tax return for the specified period and jurisdiction.
    """
    # Check permissions
    if not crud.user.is_admin(current_user) and not crud.user.has_permission(
        current_user, "tax:write"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to generate tax returns",
        )

    # Initialize tax return generator
    tax_return_generator = TaxReturnGenerator(db, current_user.company_id, current_user.id)

    try:
        # Generate the tax return
        tax_return = await tax_return_generator.generate_tax_return(
            return_type=tax_return_in.return_type,
            tax_period_start=tax_return_in.tax_period_start,
            tax_period_end=tax_return_in.tax_period_end,
            jurisdiction_code=tax_return_in.jurisdiction_code,
            filing_frequency=tax_return_in.filing_frequency or "monthly",
            force_recalculation=tax_return_in.force_recalculation or False,
        )
        
        # If this is a background task, we can add additional processing here
        if tax_return_in.generate_pdf:
            background_tasks.add_task(
                tax_return_generator.generate_tax_return_pdf,
                tax_return_id=tax_return.id,
                include_attachments=tax_return_in.include_attachments or False,
            )

        return {"success": True, "data": tax_return}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error generating tax return: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the tax return",
        )


@router.post("/", response_model=TaxReturnResponse, status_code=status.HTTP_201_CREATED)
def create_tax_return(
    *,
    db: Session = Depends(get_db),
    tax_return_in: TaxReturnCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new tax return.
    """
    # Check permissions
    if not crud.user.is_admin(current_user) and not crud.user.has_permission(
        current_user, "tax:write"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create tax returns",
        )
    
    # Create the tax return
    tax_return = crud.tax_return.create_with_line_items(
        db=db,
        obj_in=tax_return_in,
        company_id=current_user.company_id,
        user_id=current_user.id
    )
    
    return {"data": tax_return}


@router.get("/{tax_return_id}", response_model=TaxReturnResponse)
def get_tax_return(
    *,
    db: Session = Depends(get_db),
    tax_return_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific tax return by ID.
    """
    tax_return = crud.tax_return.get_by_id(
        db, 
        id=tax_return_id, 
        company_id=current_user.company_id
    )
    
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )
    
    # Check permissions
    if not crud.user.is_admin(current_user) and not crud.user.has_permission(
        current_user, "tax:read"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this tax return",
        )
    
    return {"data": tax_return}


@router.put("/{tax_return_id}", response_model=TaxReturnResponse)
def update_tax_return(
    *,
    db: Session = Depends(get_db),
    tax_return_id: UUID,
    tax_return_in: TaxReturnUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a tax return.
    """
    tax_return = crud.tax_return.get_by_id(
        db, 
        id=tax_return_id, 
        company_id=current_user.company_id
    )
    
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )
    
    # Check permissions
    if not crud.user.is_admin(current_user) and not crud.user.has_permission(
        current_user, "tax:write"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this tax return",
        )
    
    # Prevent updates to filed/approved returns unless user is admin
    if tax_return.status in [TaxReturnStatus.FILED, TaxReturnStatus.PAID] and not crud.user.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a filed or paid tax return",
        )
    
    # Update the tax return
    tax_return = crud.tax_return.update_with_line_items(
        db=db,
        db_obj=tax_return,
        obj_in=tax_return_in,
        user_id=current_user.id
    )
    
    return {"data": tax_return}


@router.delete("/{tax_return_id}", response_model=schemas.Msg)
def delete_tax_return(
    *,
    db: Session = Depends(get_db),
    tax_return_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a tax return.
    """
    tax_return = crud.tax_return.get_by_id(
        db, 
        id=tax_return_id, 
        company_id=current_user.company_id
    )
    
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )
    
    # Check permissions
    if not crud.user.is_admin(current_user) and not crud.user.has_permission(
        current_user, "tax:delete"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this tax return",
        )
    
    # Prevent deletion of filed/approved returns
    if tax_return.status in [TaxReturnStatus.FILED, TaxReturnStatus.PAID]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a filed or paid tax return",
        )
    
    crud.tax_return.remove(db, id=tax_return_id)
    
    return {"msg": "Tax return deleted successfully"}


@router.get("/calendar/upcoming", response_model=TaxFilingCalendarResponse)
def get_upcoming_filings(
    *,
    db: Session = Depends(get_db),
    days_ahead: int = Query(30, description="Number of days to look ahead", ge=1, le=365),
    include_overdue: bool = Query(True, description="Include overdue filings"),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get upcoming tax filings within the specified number of days.
    """
    if not crud.user.is_admin(current_user) and not crud.user.has_permission(
        current_user, "tax:read"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view tax calendar",
        )
    
    tax_returns = crud.tax_return.get_upcoming_filings(
        db,
        company_id=current_user.company_id,
        days_ahead=days_ahead,
        include_overdue=include_overdue
    )
    
    # Format response
    today = date.today()
    calendar_entries = []
    
    for tr in tax_returns:
        is_overdue = tr.due_date < today
        is_upcoming = tr.due_date <= (today + timedelta(days=7))
        
        calendar_entries.append({
            "id": tr.id,
            "return_type": tr.return_type,
            "jurisdiction_code": tr.jurisdiction_code,
            "period_start": tr.tax_period_start,
            "period_end": tr.tax_period_end,
            "due_date": tr.due_date,
            "status": tr.status,
            "is_upcoming": is_upcoming,
            "is_overdue": is_overdue,
            "total_due": tr.total_due_amount
        })
    
    return {"data": calendar_entries}


@router.post("/{tax_return_id}/submit", response_model=TaxReturnResponse)
def submit_tax_return(
    *,
    db: Session = Depends(get_db),
    tax_return_id: UUID,
    submit_request: TaxReturnSubmitRequest,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Submit a tax return for approval or filing.
    """
    tax_return = crud.tax_return.get_by_id(
        db, 
        id=tax_return_id, 
        company_id=current_user.company_id
    )
    
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )
    
    # Check permissions
    if not crud.user.is_admin(current_user) and not crud.user.has_permission(
        current_user, "tax:write"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to submit this tax return",
        )
    
    # Validate status transition
    if tax_return.status not in [TaxReturnStatus.DRAFT, TaxReturnStatus.PENDING_APPROVAL]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit a tax return with status: {tax_return.status}",
        )
    
    # Update status and notes
    update_data = {
        "status": TaxReturnStatus.PENDING_APPROVAL,
        "notes": submit_request.notes or tax_return.notes
    }
    
    # If file_now is True and user has permission, mark as filed
    if submit_request.file_now and crud.user.has_permission(current_user, "tax:file"):
        update_data.update({
            "status": TaxReturnStatus.FILED,
            "filing_date": datetime.utcnow(),
            "filed_by": current_user.id
        })
    
    # Update the tax return
    tax_return = crud.tax_return.update(
        db,
        db_obj=tax_return,
        obj_in=update_data
    )
    
    # TODO: Send notifications to approvers if needed
    
    return {"data": tax_return}


@router.post("/{tax_return_id}/approve", response_model=TaxReturnResponse)
def approve_tax_return(
    *,
    db: Session = Depends(get_db),
    tax_return_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Approve a tax return.
    """
    tax_return = crud.tax_return.get_by_id(
        db, 
        id=tax_return_id, 
        company_id=current_user.company_id
    )
    
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )
    
    # Check permissions
    if not crud.user.is_admin(current_user) and not crud.user.has_permission(
        current_user, "tax:approve"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to approve tax returns",
        )
    
    # Validate status transition
    if tax_return.status != TaxReturnStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve a tax return with status: {tax_return.status}",
        )
    
    # Update status
    tax_return = crud.tax_return.update(
        db,
        db_obj=tax_return,
        obj_in={
            "status": TaxReturnStatus.APPROVED,
            "approved_by": current_user.id,
            "approved_at": datetime.utcnow()
        }
    )
    
    return {"data": tax_return}


@router.post("/{tax_return_id}/file", response_model=TaxReturnEfileResponse)
async def file_tax_return(
    *,
    db: Session = Depends(get_db),
    tax_return_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    E-file a tax return with the relevant tax authority.
    """
    tax_return = crud.tax_return.get_by_id(
        db, 
        id=tax_return_id, 
        company_id=current_user.company_id
    )
    
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )
    
    # Check permissions
    if not crud.user.is_admin(current_user) and not crud.user.has_permission(
        current_user, "tax:file"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to file tax returns",
        )
    
    # Validate status
    if tax_return.status not in [TaxReturnStatus.APPROVED, TaxReturnStatus.FILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot file a tax return with status: {tax_return.status}",
        )
    
    # Initialize tax filing service
    tax_filing_service = TaxFilingService(db)
    
    try:
        # Attempt to e-file the return
        filing_result = await tax_filing_service.efile_tax_return(
            tax_return=tax_return,
            user_id=current_user.id
        )
        
        # Update tax return status if filing was successful
        if filing_result.status == "accepted":
            crud.tax_return.update(
                db,
                db_obj=tax_return,
                obj_in={
                    "status": TaxReturnStatus.FILED,
                    "filing_date": datetime.utcnow(),
                    "filed_by": current_user.id,
                    "confirmation_number": filing_result.confirmation_number,
                    "filing_reference": filing_result.submission_id
                }
            )
        
        return filing_result
        
    except Exception as e:
        logger.error(f"Error e-filing tax return {tax_return_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error filing tax return: {str(e)}"
        )


@router.get("/{tax_return_id}/pdf", response_model=bytes)
def generate_tax_return_pdf(
    *,
    db: Session = Depends(get_db),
    tax_return_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Generate a PDF version of the tax return.
    """
    tax_return = crud.tax_return.get_by_id(
        db, 
        id=tax_return_id, 
        company_id=current_user.company_id
    )
    
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )
    
    # Check permissions
    if not crud.user.is_admin(current_user) and not crud.user.has_permission(
        current_user, "tax:read"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this tax return",
        )
    
    # TODO: Implement PDF generation
    # For now, return a placeholder
    pdf_content = f"PDF for Tax Return {tax_return_id}".encode()
    
    return pdf_content
