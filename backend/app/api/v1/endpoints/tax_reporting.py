from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse, JSONResponse

from app.core.tax.tax_calculation_service import tax_calculation_service
from app.core.tax.tax_policy_service import tax_policy_service
from app.core.tax.tax_reporting_service import tax_reporting_service
from app.core.auth import get_current_user
from app.db.session import get_db
from app.schemas.tax import (
    TaxPolicy, TaxRate, TaxExemption, 
    TaxCalculationRequest, TaxCalculationResponse
)
from app.models.user import User

router = APIRouter(tags=["Tax Reporting"])

class TaxLiabilityReportRequest(BaseModel):
    start_date: date
    end_date: date
    tax_types: Optional[List[str]] = None
    jurisdiction_codes: Optional[List[str]] = None
    group_by: str = "month"
    page: int = 1
    page_size: int = 1000

class TaxLiabilityReportResponse(BaseModel):
    company_id: str
    start_date: str
    end_date: str
    total_taxable_amount: str
    total_tax_amount: str
    total_transactions: int
    periods: List[Dict[str, Any]]
    pagination: Dict[str, Any]
    metadata: Dict[str, Any]
    
    class Config:
        json_encoders = {
            "decimal": lambda v: str(v) if v is not None else "0.00"
        }

@router.get("/policy/current", response_model=TaxPolicy)
async def get_current_tax_policy(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the current active tax policy."""
    try:
        policy = await tax_policy_service.get_current_policy(db)
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active tax policy found"
            )
        return policy
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/policy", response_model=TaxPolicy)
async def update_tax_policy(
    policy_data: TaxPolicy,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update the current tax policy."""
    try:
        updated_policy = await tax_policy_service.update_policy(db, policy_data)
        return updated_policy
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/rates", response_model=TaxRate)
async def add_tax_rate(
    rate_data: TaxRate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a new tax rate."""
    try:
        new_rate = await tax_policy_service.add_tax_rate(db, rate_data)
        return new_rate
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/rates/{rate_id}", response_model=TaxRate)
async def update_tax_rate(
    rate_id: str,
    rate_data: TaxRate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing tax rate."""
    try:
        updated_rate = await tax_policy_service.update_tax_rate(db, rate_id, rate_data)
        return updated_rate
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/rates/{rate_id}")
async def delete_tax_rate(
    rate_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a tax rate."""
    try:
        await tax_policy_service.delete_tax_rate(db, rate_id)
        return {"message": "Tax rate deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/reports/liability", response_model=TaxLiabilityReportResponse)
async def get_tax_liability_report(
    start_date: date = Query(..., description="Start date of the reporting period"),
    end_date: date = Query(..., description="End date of the reporting period"),
    tax_types: Optional[List[str]] = Query(None, description="Filter by tax types"),
    jurisdiction_codes: Optional[List[str]] = Query(None, description="Filter by jurisdiction codes"),
    group_by: str = Query("month", description="Group results by: day, week, month, quarter, year"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(1000, ge=1, le=10000, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a tax liability report for the specified period with pagination support.
    """
    try:
        report = tax_reporting_service.generate_tax_liability_report(
            company_id=current_user.company_id,
            start_date=start_date,
            end_date=end_date,
            tax_types=tax_types,
            jurisdiction_codes=jurisdiction_codes,
            group_by=group_by,
            page=page,
            page_size=page_size
        )
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating tax liability report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating tax liability report: {str(e)}"
        )

@router.post("/reports/liability/async", response_model=Dict[str, str])
async def generate_liability_report_async(
    request: TaxLiabilityReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a tax liability report asynchronously.
    Returns a task ID that can be used to check the status of the report.
    """
    try:
        # In a real implementation, this would use Celery or similar
        # For now, we'll just run it synchronously in a background task
        report_id = str(uuid.uuid4())
        
        # In a real implementation, we would store the task ID and status in the database
        # and have a worker process handle the actual report generation
        
        # For now, we'll just run the report in a background task
        async def generate_report():
            try:
                report = tax_reporting_service.generate_tax_liability_report(
                    company_id=current_user.company_id,
                    **request.dict()
                )
                # Store the result in Redis or similar
                # redis_client.set(f"tax_report:{report_id}", json.dumps(report), ex=86400)  # 24h
                return report
            except Exception as e:
                logger.error(f"Error in background task: {str(e)}", exc_info=True)
                # Store the error
                # redis_client.set(f"tax_report:{report_id}:error", str(e), ex=86400)
        
        # Start the background task
        background_tasks.add_task(generate_report)
        
        return {
            "message": "Report generation started",
            "report_id": report_id,
            "status_endpoint": f"/api/v1/tax/reports/status/{report_id}"
        }
    except Exception as e:
        logger.error(f"Error scheduling tax report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling tax report: {str(e)}"
        )

@router.get("/reports/status/{report_id}", response_model=Dict[str, Any])
async def get_report_status(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a tax report generation task.
    """
    try:
        # In a real implementation, this would check the status in the database or Redis
        # For now, we'll just return a mock response
        # result = redis_client.get(f"tax_report:{report_id}")
        # if result:
        #     return {"status": "completed", "report": json.loads(result)}
        # 
        # error = redis_client.get(f"tax_report:{report_id}:error")
        # if error:
        #     return {"status": "failed", "error": error}
        
        return {
            "status": "in_progress",
            "progress": 50,  # This would be updated by the worker
            "message": "Report generation in progress"
        }
    except Exception as e:
        logger.error(f"Error getting report status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting report status: {str(e)}"
        )

@router.post("/exemptions", response_model=TaxExemption)
async def add_tax_exemption(
    exemption_data: TaxExemption,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a new tax exemption."""
    try:
        new_exemption = await tax_policy_service.add_tax_exemption(db, exemption_data)
        return new_exemption
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/exemptions/{exemption_id}", response_model=TaxExemption)
async def update_tax_exemption(
    exemption_id: str,
    exemption_data: TaxExemption,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing tax exemption."""
    try:
        updated_exemption = await tax_policy_service.update_tax_exemption(db, exemption_id, exemption_data)
        return updated_exemption
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/exemptions/{exemption_id}")
async def delete_tax_exemption(
    exemption_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a tax exemption."""
    try:
        success = tax_reporting_service.delete_tax_exemption(
            exemption_id=exemption_id,
            company_id=current_user.company_id,
            db=db
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax exemption not found or you don't have permission to delete it"
            )
        return {"status": "success", "message": "Tax exemption deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting tax exemption: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting tax exemption: {str(e)}"
        )

@router.get("/export/{report_type}", response_model=Dict[str, Any])
async def export_tax_report(
    report_type: str = Query(..., description="Type of report to export (liability, transactions, etc.)"),
    format_type: str = Query("csv", description="Export format (csv, excel, pdf)"),
    start_date: date = Query(..., description="Start date of the reporting period"),
    end_date: date = Query(..., description="End date of the reporting period"),
    tax_types: Optional[List[str]] = Query(None, description="Filter by tax types"),
    jurisdiction_codes: Optional[List[str]] = Query(None, description="Filter by jurisdiction codes"),
    group_by: str = Query("month", description="Group results by: day, week, month, quarter, year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export tax report in the specified format.
    
    This endpoint allows exporting tax reports in various formats (CSV, Excel, PDF).
    The report can be filtered by date range, tax types, and jurisdictions.
    """
    try:
        # Validate format_type
        if format_type not in ["csv", "excel", "pdf"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format_type. Must be one of: csv, excel, pdf"
            )
            
        # Call the reporting service to generate the export
        result = tax_reporting_service.export_tax_report(
            report_type=report_type,
            format_type=format_type,
            company_id=current_user.company_id,
            start_date=start_date,
            end_date=end_date,
            tax_types=tax_types,
            jurisdiction_codes=jurisdiction_codes,
            group_by=group_by
        )
        
        # If the result is already a Response (for streaming), return it directly
        if isinstance(result, (StreamingResponse, Response)):
            return result
            
        # Otherwise, return the result as JSON (e.g., for PDF generation)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting {report_type} report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating export: {str(e)}"
        )

@router.post("/calculate", response_model=TaxCalculationResponse)
async def calculate_taxes(
    request: TaxCalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate taxes for a given transaction."""
    try:
        result = await tax_calculation_service.calculate_taxes(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
