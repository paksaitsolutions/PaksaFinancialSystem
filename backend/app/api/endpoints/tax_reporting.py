"""
Tax Reporting API Endpoints

This module provides API endpoints for tax reporting and compliance functionality.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.core.tax import tax_reporting_service
from app.core.security import get_current_active_user
from app.core.db.session import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/tax-reports/liability", response_model=schemas.TaxLiabilityReport)
async def get_tax_liability_report(
    start_date: date = Query(..., description="Start date of the reporting period (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date of the reporting period (YYYY-MM-DD)"),
    tax_types: Optional[List[str]] = Query(None, description="Filter by tax types (e.g., sales, vat, gst)"),
    jurisdiction_codes: Optional[List[str]] = Query(None, description="Filter by jurisdiction codes"),
    group_by: str = Query("month", description="Group results by (day, week, month, quarter, year)"),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate a tax liability report for the specified period.
    """
    # Check if user has permission to view tax reports
    if not crud.user.has_permission(current_user, "tax:reports:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access tax reports"
        )
    
    try:
        # Initialize the service with the database session
        service = tax_reporting_service.TaxReportingService(db)
        
        # Generate the report
        report = service.generate_tax_liability_report(
            company_id=current_user.company_id,
            start_date=start_date,
            end_date=end_date,
            tax_types=tax_types,
            jurisdiction_codes=jurisdiction_codes,
            group_by=group_by
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating tax liability report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the tax liability report"
        )

@router.post("/tax-filings/prepare", response_model=schemas.TaxFilingResponse)
async def prepare_tax_filing(
    filing_data: schemas.TaxFilingCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Prepare a tax filing for submission to a tax authority.
    """
    # Check if user has permission to prepare tax filings
    if not crud.user.has_permission(current_user, "tax:filings:create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to prepare tax filings"
        )
    
    try:
        # Initialize the service with the database session
        service = tax_reporting_service.TaxReportingService(db)
        
        # Generate the tax filing
        filing = service.generate_tax_filing(
            company_id=current_user.company_id,
            tax_authority_id=filing_data.tax_authority_id,
            period_start=filing_data.period_start,
            period_end=filing_data.period_end,
            tax_type=filing_data.tax_type,
            jurisdiction_code=filing_data.jurisdiction_code,
            include_transactions=filing_data.include_transactions,
            mark_as_filed=False  # Just prepare, don't mark as filed yet
        )
        
        # Create a tax filing record
        filing_in = {
            "company_id": current_user.company_id,
            "tax_authority_id": filing_data.tax_authority_id,
            "tax_type": filing_data.tax_type,
            "jurisdiction_code": filing_data.jurisdiction_code,
            "period_start": filing_data.period_start,
            "period_end": filing_data.period_end,
            "filing_date": date.today(),
            "due_date": filing_data.due_date,
            "status": "prepared",
            "filing_data": filing,
            "created_by": current_user.id,
            "updated_by": current_user.id
        }
        
        db_filing = crud.tax_filing.create(db, obj_in=filing_in)
        
        return {
            "success": True,
            "message": "Tax filing prepared successfully",
            "data": db_filing
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error preparing tax filing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while preparing the tax filing"
        )

@router.post("/tax-filings/{filing_id}/submit", response_model=schemas.TaxFilingResponse)
async def submit_tax_filing(
    filing_id: str,
    submission_data: schemas.TaxFilingSubmit,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit a prepared tax filing to the tax authority.
    """
    # Check if user has permission to submit tax filings
    if not crud.user.has_permission(current_user, "tax:filings:submit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to submit tax filings"
        )
    
    try:
        # Get the tax filing
        db_filing = crud.tax_filing.get(db, id=filing_id)
        if not db_filing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax filing not found"
            )
            
        # Check if the filing belongs to the user's company
        if db_filing.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this tax filing"
            )
            
        # Check if the filing is in a valid state for submission
        if db_filing.status != "prepared":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot submit a tax filing with status '{db_filing.status}'"
            )
        
        # Initialize the service with the database session
        service = tax_reporting_service.TaxReportingService(db)
        
        # Mark the transactions as filed
        service.generate_tax_filing(
            company_id=current_user.company_id,
            tax_authority_id=db_filing.tax_authority_id,
            period_start=db_filing.period_start,
            period_end=db_filing.period_end,
            tax_type=db_filing.tax_type,
            jurisdiction_code=db_filing.jurisdiction_code,
            include_transactions=False,
            mark_as_filed=True
        )
        
        # Update the filing record
        update_data = {
            "status": "submitted",
            "submission_date": datetime.utcnow(),
            "submission_reference": submission_data.reference_number,
            "submission_notes": submission_data.notes,
            "submission_data": submission_data.submission_data,
            "updated_by": current_user.id
        }
        
        db_filing = crud.tax_filing.update(db, db_obj=db_filing, obj_in=update_data)
        
        return {
            "success": True,
            "message": "Tax filing submitted successfully",
            "data": db_filing
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting tax filing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while submitting the tax filing"
        )

@router.get("/tax-compliance/status", response_model=schemas.TaxComplianceStatus)
async def get_tax_compliance_status(
    tax_types: Optional[List[str]] = Query(None, description="Filter by tax types"),
    jurisdiction_codes: Optional[List[str]] = Query(None, description="Filter by jurisdiction codes"),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the tax compliance status for the company.
    """
    # Check if user has permission to view compliance status
    if not crud.user.has_permission(current_user, "tax:compliance:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view tax compliance status"
        )
    
    try:
        # Initialize the service with the database session
        service = tax_reporting_service.TaxReportingService(db)
        
        # Get the compliance status
        status = service.get_tax_compliance_status(
            company_id=current_user.company_id,
            tax_types=tax_types,
            jurisdiction_codes=jurisdiction_codes
        )
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tax compliance status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the tax compliance status"
        )

@router.get("/tax-filings/upcoming", response_model=List[schemas.TaxFilingUpcoming])
async def get_upcoming_tax_filings(
    days_ahead: int = Query(90, description="Number of days to look ahead for upcoming filings"),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a list of upcoming tax filings.
    """
    # Check if user has permission to view upcoming filings
    if not crud.user.has_permission(current_user, "tax:filings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view upcoming tax filings"
        )
    
    try:
        # Get the current date and calculate the end date
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        # Get tax filing frequencies for the company
        frequencies = crud.tax_filing_frequency.get_by_company(
            db, company_id=current_user.company_id
        )
        
        # Initialize the service with the database session
        service = tax_reporting_service.TaxReportingService(db)
        
        upcoming_filings = []
        
        # Check each frequency for upcoming due dates
        for freq in frequencies:
            # Get the last filing for this frequency
            last_filing = service._get_last_filing(
                company_id=current_user.company_id,
                tax_type=freq.tax_type,
                jurisdiction_code=freq.jurisdiction_code
            )
            
            # Calculate the next due date
            next_due_date = service._calculate_next_due_date(
                frequency=freq.frequency,
                last_period_end=last_filing["period_end"] if last_filing else None
            )
            
            if next_due_date and today <= next_due_date <= end_date:
                # Get the tax authority
                tax_authority = crud.tax_authority.get(
                    db, id=freq.tax_authority_id
                )
                
                # Add to upcoming filings
                upcoming_filings.append({
                    "tax_type": freq.tax_type,
                    "jurisdiction_code": freq.jurisdiction_code,
                    "tax_authority_id": freq.tax_authority_id,
                    "tax_authority_name": tax_authority.name if tax_authority else "",
                    "frequency": freq.frequency,
                    "due_date": next_due_date.isoformat(),
                    "days_until_due": (next_due_date - today).days,
                    "last_filing_date": last_filing["filing_date"].isoformat() if last_filing else None,
                    "last_filing_period": f"{last_filing['period_start'].strftime('%Y-%m-%d')} to {last_filing['period_end'].strftime('%Y-%m-%d')}" if last_filing else None
                })
        
        # Sort by due date
        upcoming_filings.sort(key=lambda x: x["due_date"])
        
        return upcoming_filings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting upcoming tax filings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving upcoming tax filings"
        )
