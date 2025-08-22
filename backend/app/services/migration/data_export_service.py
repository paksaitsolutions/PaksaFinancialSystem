"""
Data export service for exporting data to various formats.
"""
import csv
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Integer
from app.models.base import BaseModel


class ExportJob(BaseModel):
    """Export job tracking."""
    __tablename__ = "export_jobs"
    
    job_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    data_type = Column(String(50), nullable=False)
    format = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_records = Column(Integer, nullable=True)


class DataExportService:
    """Service for exporting data to various formats."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_to_csv(self, data: List[Dict[str, Any]], file_path: str, data_type: str) -> ExportJob:
        """Export data to CSV file."""
        job = ExportJob(
            job_name=f"CSV Export - {data_type}",
            file_path=file_path,
            data_type=data_type,
            format="csv",
            status="processing",
            total_records=len(data)
        )
        
        self.db.add(job)
        self.db.commit()
        
        try:
            if data:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            
            job.status = "completed"
            
        except Exception as e:
            job.status = "failed"
        
        self.db.commit()
        return job
    
    def export_to_json(self, data: List[Dict[str, Any]], file_path: str, data_type: str) -> ExportJob:
        """Export data to JSON file."""
        job = ExportJob(
            job_name=f"JSON Export - {data_type}",
            file_path=file_path,
            data_type=data_type,
            format="json",
            status="processing",
            total_records=len(data)
        )
        
        self.db.add(job)
        self.db.commit()
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            job.status = "completed"
            
        except Exception as e:
            job.status = "failed"
        
        self.db.commit()
        return job
    
    def get_export_jobs(self, limit: int = 50) -> List[ExportJob]:
        """Get export job history."""
        return self.db.query(ExportJob).order_by(
            ExportJob.created_at.desc()
        ).limit(limit).all()