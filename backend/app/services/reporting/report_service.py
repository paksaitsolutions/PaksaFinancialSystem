"""Advanced reporting service for generating financial and analytical reports."""
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from typing_extensions import Literal
import json
import os

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from fastapi import HTTPException
from plotly.subplots import make_subplots
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, select, and_, or_
import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import tempfile

from app.core.cache import cache
from app.core.config import settings
from app.core.notifications import NotificationService
from app.core.security import get_password_hash
from app.models import (
from app.schemas.report_schemas import (



    User, Company, GeneralLedger, Account, JournalEntry, 
    TaxTransaction, TaxRate, ComplianceCheck
)
    ReportDefinition, ReportFilter, ReportColumn, 
    ReportOutputFormat, ReportSchedule, ReportStatus
)

logger = logging.getLogger(__name__)

class ReportType(str, Enum):
    """Types of reports that can be generated."""
    FINANCIAL_STATEMENT = "financial_statement"
    TAX_COMPLIANCE = "tax_compliance"
    CASH_FLOW = "cash_flow"
    GENERAL_LEDGER = "general_ledger"
    TRIAL_BALANCE = "trial_balance"
    TAX_LIABILITY = "tax_liability"
    CUSTOM = "custom"

class ReportGranularity(str, Enum):
    """Time granularity for report data."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class ReportContext:
    """Context for report generation."""
    company_id: str
    user_id: str
    start_date: date
    end_date: date
    timezone: str = "UTC"
    currency: str = "USD"
    filters: Dict[str, Any] = field(default_factory=dict)
    format: ReportOutputFormat = ReportOutputFormat.PDF
    parameters: Dict[str, Any] = field(default_factory=dict)

class ReportService:
    """Service for generating and managing financial reports."""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService()
    
    async def generate_report(
        self,
        report_definition: ReportDefinition,
        context: ReportContext,
        async_mode: bool = True
    ) -> Dict[str, Any]:
        """Generate Report."""
        """
        Generate a report based on the provided definition and context.
        
        Args:
            report_definition: Definition of the report to generate
            context: Context for report generation
            async_mode: If True, run report generation asynchronously
            
        Returns:
            Dictionary with report ID and status
        """
        try:
            # Validate report definition
            self._validate_report_definition(report_definition)
            
            # Create report record
            report = self._create_report_record(report_definition, context)
            
            if async_mode:
                # Queue the report generation task
                # In a real implementation, this would use Celery or similar
                # For now, we'll just run it synchronously
                self._generate_report_async(report.id)
                return {
                    "report_id": str(report.id),
                    "status": ReportStatus.QUEUED,
                    "message": "Report generation has been queued"
                }
            else:
                # Generate report synchronously
                result = await self._generate_report(report.id)
                return {
                    "report_id": str(report.id),
                    "status": ReportStatus.COMPLETED,
                    "url": result.get("url"),
                    "metadata": result.get("metadata", {})
                }
                
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate report: {str(e)}"
            )
    
    async def get_report_status(self, report_id: str) -> Dict[str, Any]:
        """
        Get the status of a report.
        
        Args:
            report_id: ID of the report
            
        Returns:
            Dictionary with report status and metadata
        """
        # In a real implementation, this would check the database or task queue
        # For now, we'll just return a mock response
        return {
            "report_id": report_id,
            "status": ReportStatus.COMPLETED,
            "progress": 100,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    async def download_report(
        self, 
        report_id: str,
        format: ReportOutputFormat = ReportOutputFormat.PDF
    ) -> Tuple[bytes, str]:
        """Download Report."""
        """
        Download a generated report.
        
        Args:
            report_id: ID of the report
            format: Desired output format
            
        Returns:
            Tuple of (file_content, content_type)
        """
        # In a real implementation, this would retrieve the report from storage
        # For now, we'll generate a simple PDF report
        
        if format == ReportOutputFormat.PDF:
            # Generate a simple PDF report
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            # Create a file-like buffer to receive PDF data
            buffer = io.BytesIO()
            
            # Create the PDF object
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Container for the 'flowable' objects
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            elements.append(Paragraph("Financial Report", styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Add report metadata
            elements.append(Paragraph(f"Report ID: {report_id}", styles['Normal']))
            elements.append(Paragraph(f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']))
            elements.append(Spacer(1, 12))
            
            # Add sample data
            data = [
                ['Account', 'Debit', 'Credit', 'Balance'],
                ['1000 - Cash', '10,000.00', '', '10,000.00'],
                ['2000 - Accounts Payable', '', '5,000.00', '5,000.00'],
                ['3000 - Revenue', '', '15,000.00', '15,000.00'],
                ['4000 - Expenses', '7,500.00', '', '7,500.00'],
                ['', '17,500.00', '20,000.00', '2,500.00']
            ]
            
            # Create the table
            table = Table(data)
            
            # Add style
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
            
            # Build the PDF
            doc.build(elements)
            
            # File contents and content type
            pdf = buffer.getvalue()
            buffer.close()
            
            return pdf, "application/pdf"
            
        elif format == ReportOutputFormat.EXCEL:
            # Generate a simple Excel report
            import pandas as pd
            from io import BytesIO
            
            # Create a sample DataFrame
            data = {
                'Account': ['1000 - Cash', '2000 - Accounts Payable', '3000 - Revenue', '4000 - Expenses', 'Total'],
                'Debit': [10000.00, 0, 0, 7500.00, 17500.00],
                'Credit': [0, 5000.00, 15000.00, 0, 20000.00],
                'Balance': [10000.00, 5000.00, 15000.00, 7500.00, 2500.00]
            }
            
            df = pd.DataFrame(data)
            
            # Create Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Financial Report', index=False)
                
                # Get workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets['Financial Report']
                
                # Format header
                header_fill = 'C0C0C0'
                header_font = 'FFFFFF'
                
                for cell in worksheet[1]:
                    cell.fill = PatternFill(start_color=header_fill, end_color=header_fill, fill_type='solid')
                    cell.font = Font(color=header_font, bold=True)
                
                # Format numbers
                for row in worksheet.iter_rows(min_row=2, max_row=len(df), min_col=2, max_col=4):
                    for cell in row:
                        cell.number_format = '#,##0.00'
            
            excel_data = output.getvalue()
            output.close()
            
            return excel_data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported report format: {format}"
            )
    
    async def schedule_report(
        self,
        report_definition: ReportDefinition,
        schedule: ReportSchedule,
        recipients: List[str],
        context: ReportContext
    ) -> Dict[str, Any]:
        """Schedule Report."""
        """
        Schedule a report to be generated and delivered periodically.
        
        Args:
            report_definition: Definition of the report to schedule
            schedule: Schedule configuration
            recipients: List of email addresses to receive the report
            context: Context for report generation
            
        Returns:
            Dictionary with schedule ID and status
        """
        # In a real implementation, this would create a scheduled task
        # For now, we'll just return a mock response
        return {
            "schedule_id": f"sch_{uuid.uuid4()}",
            "status": "scheduled",
            "next_run": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "recipients": recipients
        }
    
    # --- Helper Methods ---
    
    def _validate_report_definition(self, definition: ReportDefinition) -> None:
        if not definition.name or not definition.name.strip():
            raise ValueError("Report name is required")
        
        if not definition.columns:
            raise ValueError("At least one column is required")
        
        # Add more validation as needed
    
    def _create_report_record(
        self,
        definition: ReportDefinition,
        context: ReportContext
    ) -> Dict[str, Any]:
        """ Create Report Record."""
        """Create a report record in the database."""
        # In a real implementation, this would save to the database
        # For now, we'll just return a dictionary
        return {
            "id": f"rep_{uuid.uuid4()}",
            "name": definition.name,
            "type": definition.type,
            "status": "pending",
            "created_by": context.user_id,
            "company_id": context.company_id,
            "start_date": context.start_date,
            "end_date": context.end_date,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    def _generate_report_async(self, report_id: str) -> None:
        # In a real implementation, this would queue a background task
        # For now, we'll just log a message
        logger.info(f"Starting async report generation for report {report_id}")
        
        # Simulate background processing
        import threading
        
        def process():
            try:
                # Simulate processing time
                import time
                time.sleep(5)
                
                # In a real implementation, this would update the report status
                logger.info(f"Completed async report generation for report {report_id}")
                
            except Exception as e:
                logger.error(f"Error in async report generation: {str(e)}")
        
        # Start processing in a separate thread
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
    
    async def _generate_report(self, report_id: str) -> Dict[str, Any]:
        # In a real implementation, this would generate the actual report
        # For now, we'll just return a mock response
        return {
            "report_id": report_id,
            "status": "completed",
            "url": f"https://api.example.com/reports/{report_id}/download",
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "size_bytes": 1024,
                "page_count": 1
            }
        }

# Singleton instance for dependency injection
def get_report_service(db: Session) -> ReportService:
    return ReportService(db)
