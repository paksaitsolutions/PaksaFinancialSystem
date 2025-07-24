"""
Data import service for handling various data formats.
"""
import csv
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Integer, JSON
from app.models.base import BaseModel


class ImportJob(BaseModel):
    """Import job tracking."""
    __tablename__ = "import_jobs"
    
    job_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    data_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_records = Column(Integer, nullable=True)
    processed_records = Column(Integer, nullable=False, default=0)
    error_records = Column(Integer, nullable=False, default=0)
    error_log = Column(JSON, nullable=True)


class DataImportService:
    """Service for importing data from various sources."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def import_csv(self, file_path: str, data_type: str, mapping: Dict[str, str]) -> ImportJob:
        """Import data from CSV file."""
        job = ImportJob(
            job_name=f"CSV Import - {data_type}",
            file_path=file_path,
            data_type=data_type,
            status="processing"
        )
        
        self.db.add(job)
        self.db.commit()
        
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                records = list(reader)
            
            job.total_records = len(records)
            
            errors = []
            for index, record in enumerate(records):
                try:
                    mapped_data = self._apply_mapping(record, mapping)
                    self._validate_record(data_type, mapped_data)
                    job.processed_records += 1
                except Exception as e:
                    job.error_records += 1
                    errors.append({"row": index, "error": str(e)})
            
            job.error_log = errors
            job.status = "completed" if job.error_records == 0 else "completed_with_errors"
            
        except Exception as e:
            job.status = "failed"
            job.error_log = [{"error": str(e)}]
        
        self.db.commit()
        return job
    
    def _apply_mapping(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """Apply field mapping to data."""
        mapped_data = {}
        for source_field, target_field in mapping.items():
            if source_field in data:
                mapped_data[target_field] = data[source_field]
        return mapped_data
    
    def _validate_record(self, data_type: str, data: Dict[str, Any]):
        """Validate record data."""
        if not data:
            raise ValueError("Empty data record")
        
        # Add validation logic based on data_type
        required_fields = {
            "vendors": ["name", "email"],
            "customers": ["name", "email"],
            "items": ["name", "price"]
        }
        
        if data_type in required_fields:
            for field in required_fields[data_type]:
                if field not in data or not data[field]:
                    raise ValueError(f"Missing required field: {field}")
    
    def get_import_jobs(self, limit: int = 50) -> List[ImportJob]:
        """Get import job history."""
        return self.db.query(ImportJob).order_by(
            ImportJob.created_at.desc()
        ).limit(limit).all()