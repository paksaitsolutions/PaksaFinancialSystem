"""
Data migration API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.services.migration.data_import_service import DataImportService
from app.services.migration.data_export_service import DataExportService
from app.services.migration.data_validation_service import DataValidationService

router = APIRouter()


@router.post(
    "/import/csv",
    summary="Import CSV data",
    description="Import data from CSV file.",
    tags=["Data Migration"]
)
async def import_csv_data(
    file: UploadFile = File(...),
    data_type: str = "vendors",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Import data from CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    # Save uploaded file
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Default mapping (can be customized)
    mapping = {
        "name": "name",
        "email": "email",
        "phone": "phone"
    }
    
    service = DataImportService(db)
    job = service.import_csv(file_path, data_type, mapping)
    
    return job


@router.post(
    "/export/csv",
    summary="Export CSV data",
    description="Export data to CSV file.",
    tags=["Data Migration"]
)
async def export_csv_data(
    data_type: str = "vendors",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Export data to CSV file."""
    # Mock data for export
    data = [
        {"name": "Vendor 1", "email": "vendor1@example.com"},
        {"name": "Vendor 2", "email": "vendor2@example.com"}
    ]
    
    file_path = f"/tmp/export_{data_type}.csv"
    
    service = DataExportService(db)
    job = service.export_to_csv(data, file_path, data_type)
    
    return job


@router.post(
    "/validate",
    summary="Validate data",
    description="Validate data before import.",
    tags=["Data Migration"]
)
async def validate_data(
    file: UploadFile = File(...),
    data_type: str = "vendors",
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Validate data before import."""
    import csv
    
    content = await file.read()
    content_str = content.decode('utf-8')
    
    # Parse CSV content
    reader = csv.DictReader(content_str.splitlines())
    records = list(reader)
    
    service = DataValidationService()
    results = service.validate_batch(data_type, records)
    
    return results


@router.get(
    "/jobs/import",
    summary="Get import jobs",
    description="Get import job history.",
    tags=["Data Migration"]
)
async def get_import_jobs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get import job history."""
    service = DataImportService(db)
    return service.get_import_jobs(limit)


@router.get(
    "/jobs/export",
    summary="Get export jobs",
    description="Get export job history.",
    tags=["Data Migration"]
)
async def get_export_jobs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get export job history."""
    service = DataExportService(db)
    return service.get_export_jobs(limit)


@router.get(
    "/schema/{data_type}",
    summary="Get validation schema",
    description="Get validation schema for data type.",
    tags=["Data Migration"]
)
async def get_validation_schema(
    data_type: str,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get validation schema for data type."""
    service = DataValidationService()
    return service.get_validation_schema(data_type)