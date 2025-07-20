"""
Asynchronous export service for tax reports.

This module provides functionality to export tax reports in various formats
using background tasks to handle large datasets efficiently.
"""

import asyncio
import csv
import io
import json
from datetime import datetime, date
from enum import Enum
from typing import Any, Dict, List, Optional, Union, BinaryIO, AsyncGenerator
from typing_extensions import Literal

import pandas as pd
import numpy as np
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import models, crud, schemas
from app.core.config import settings
from app.core.tax.db_optimizer import TaxQueryOptimizer
from app.core.background_tasks import task_manager
from app.models.user import User

class ExportFormat(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PDF = "pdf"
    
class ExportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaxReportExporter:
    """Service for exporting tax reports in various formats."""
    
    def __init__(self, db: Session):
        self.db = db
        self.query_optimizer = TaxQueryOptimizer(db)
        
    async def export_report(
        self,
        *,
        company_id: str,
        user: User,
        report_type: str,
        format: ExportFormat,
        start_date: date,
        end_date: date,
        tax_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None,
        group_by: str = "month",
        include_metadata: bool = True,
        filename: Optional[str] = None,
        **export_options
    ) -> Dict[str, Any]:
        """
        Initiate a tax report export as a background task.
        
        Args:
            company_id: ID of the company
            user: User requesting the export
            report_type: Type of report to export
            format: Export format (CSV, Excel, JSON, PDF)
            start_date: Start date of the report
            end_date: End date of the report
            tax_types: Optional list of tax types to include
            jurisdiction_codes: Optional list of jurisdiction codes
            group_by: Time period to group by
            include_metadata: Whether to include metadata in the export
            filename: Custom filename (without extension)
            **export_options: Additional format-specific options
            
        Returns:
            Dict with task ID and status
        """
        # Validate export format
        try:
            format_enum = ExportFormat(format.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {format}. Supported formats: {', '.join(f.value for f in ExportFormat)}"
            )
        
        # Generate a task ID
        task_id = f"export_{report_type}_{int(datetime.utcnow().timestamp())}"
        
        # Default filename if not provided
        if not filename:
            filename = f"{report_type}_report_{start_date}_{end_date}"
        
        # Create export record
        export_record = models.TaxExport(
            id=task_id,
            company_id=company_id,
            user_id=user.id,
            report_type=report_type,
            export_format=format_enum.value,
            status=ExportStatus.PENDING.value,
            parameters={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "tax_types": tax_types,
                "jurisdiction_codes": jurisdiction_codes,
                "group_by": group_by,
                **export_options
            },
            filename=f"{filename}.{format_enum.value}",
            file_size=0,
            download_url=""
        )
        
        try:
            self.db.add(export_record)
            self.db.commit()
            self.db.refresh(export_record)
            
            # Start background task
            task_manager.add_task(
                task_id,
                self._process_export,
                export_id=task_id,
                company_id=company_id,
                user_id=user.id,
                report_type=report_type,
                format=format_enum,
                start_date=start_date,
                end_date=end_date,
                tax_types=tax_types,
                jurisdiction_codes=jurisdiction_codes,
                group_by=group_by,
                include_metadata=include_metadata,
                filename=filename,
                **export_options
            )
            
            return {
                "task_id": task_id,
                "status": ExportStatus.PROCESSING.value,
                "message": "Export started in the background",
                "download_url": f""
            }
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start export: {str(e)}"
            )
    
    async def _process_export(
        self,
        export_id: str,
        company_id: str,
        user_id: str,
        report_type: str,
        format: ExportFormat,
        start_date: date,
        end_date: date,
        tax_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None,
        group_by: str = "month",
        include_metadata: bool = True,
        filename: str = "tax_report",
        **export_options
    ) -> None:
        """
        Background task to process the export.
        
        This method runs in a background task and updates the export status.
        """
        from app.db.session import SessionLocal
        
        db = SessionLocal()
        export_record = None
        
        try:
            # Update status to processing
            export_record = db.query(models.TaxExport).filter(
                models.TaxExport.id == export_id
            ).first()
            
            if not export_record:
                logger.error(f"Export record {export_id} not found")
                return
                
            export_record.status = ExportStatus.PROCESSING.value
            export_record.started_at = datetime.utcnow()
            db.commit()
            
            # Generate the report data
            if report_type == "liability":
                data = await self._generate_liability_report(
                    db=db,
                    company_id=company_id,
                    start_date=start_date,
                    end_date=end_date,
                    tax_types=tax_types,
                    jurisdiction_codes=jurisdiction_codes,
                    group_by=group_by,
                    paginated=True
                )
            else:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            # Generate the export file
            file_obj, content_type, file_extension = await self._generate_export_file(
                data=data,
                format=format,
                include_metadata=include_metadata,
                company_id=company_id,
                report_type=report_type,
                start_date=start_date,
                end_date=end_date,
                **export_options
            )
            
            # Save the file to storage
            file_path = await self._save_export_file(
                file_obj=file_obj,
                filename=f"{filename}.{file_extension}",
                content_type=content_type
            )
            
            # Update export record with results
            export_record.status = ExportStatus.COMPLETED.value
            export_record.completed_at = datetime.utcnow()
            export_record.file_size = len(file_obj.getvalue())
            export_record.download_url = file_path
            export_record.processing_time = (
                export_record.completed_at - export_record.started_at
            ).total_seconds()
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Export {export_id} failed: {str(e)}", exc_info=True)
            
            if export_record:
                export_record.status = ExportStatus.FAILED.value
                export_record.error_message = str(e)
                export_record.completed_at = datetime.utcnow()
                db.commit()
                
        finally:
            db.close()
    
    async def _generate_liability_report(
        self,
        db: Session,
        company_id: str,
        start_date: date,
        end_date: date,
        tax_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None,
        group_by: str = "month",
        paginated: bool = True,
        page: int = 1,
        page_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Generate liability report data.
        
        Args:
            db: Database session
            company_id: ID of the company
            start_date: Start date of the report
            end_date: End date of the report
            tax_types: Optional list of tax types to include
            jurisdiction_codes: Optional list of jurisdiction codes
            group_by: Time period to group by
            paginated: Whether to use pagination
            page: Page number (if paginated)
            page_size: Number of items per page (if paginated)
            
        Returns:
            Dict containing report data and metadata
        """
        # Use the query optimizer for efficient data fetching
        query_optimizer = TaxQueryOptimizer(db)
        
        if paginated:
            # Get paginated results
            results, total_count = await query_optimizer.get_liability_report_data(
                company_id=company_id,
                start_date=start_date,
                end_date=end_date,
                tax_types=tax_types,
                jurisdiction_codes=jurisdiction_codes,
                group_by=group_by,
                page=page,
                page_size=page_size
            )
            
            return {
                "data": results,
                "metadata": {
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total_count + page_size - 1) // page_size,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "generated_at": datetime.utcnow().isoformat(),
                    "filters": {
                        "tax_types": tax_types,
                        "jurisdiction_codes": jurisdiction_codes,
                        "group_by": group_by
                    }
                }
            }
        else:
            # Get all results (use with caution for large datasets)
            all_results = []
            page = 1
            total_count = 0
            
            while True:
                results, count = await query_optimizer.get_liability_report_data(
                    company_id=company_id,
                    start_date=start_date,
                    end_date=end_date,
                    tax_types=tax_types,
                    jurisdiction_codes=jurisdiction_codes,
                    group_by=group_by,
                    page=page,
                    page_size=page_size
                )
                
                if not results:
                    break
                    
                all_results.extend(results)
                
                if len(results) < page_size:
                    break
                    
                page += 1
            
            return {
                "data": all_results,
                "metadata": {
                    "total_count": len(all_results),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "generated_at": datetime.utcnow().isoformat(),
                    "filters": {
                        "tax_types": tax_types,
                        "jurisdiction_codes": jurisdiction_codes,
                        "group_by": group_by
                    }
                }
            }
    
    async def _generate_export_file(
        self,
        data: Dict[str, Any],
        format: ExportFormat,
        include_metadata: bool = True,
        **kwargs
    ) -> tuple[io.BytesIO, str, str]:
        """
        Generate an export file in the specified format.
        
        Args:
            data: Report data to export
            format: Export format
            include_metadata: Whether to include metadata in the export
            **kwargs: Additional format-specific options
            
        Returns:
            Tuple of (file_obj, content_type, file_extension)
        """
        report_data = data.get("data", [])
        metadata = data.get("metadata", {}) if include_metadata else {}
        
        if format == ExportFormat.CSV:
            return self._export_to_csv(report_data, metadata, **kwargs)
        elif format == ExportFormat.EXCEL:
            return self._export_to_excel(report_data, metadata, **kwargs)
        elif format == ExportFormat.JSON:
            return self._export_to_json(report_data, metadata, **kwargs)
        elif format == ExportFormat.PDF:
            return self._export_to_pdf(report_data, metadata, **kwargs)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_csv(
        self,
        data: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        **kwargs
    ) -> tuple[io.BytesIO, str, str]:
        """Export data to CSV format."""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
        
        # Write metadata as comments
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, dict):
                    for k, v in value.items():
                        output.write(f"# {key}.{k}: {v}\n")
                else:
                    output.write(f"# {key}: {value}\n")
            output.write("\n")
        
        # Write header and data
        writer.writeheader()
        writer.writerows(data)
        
        # Convert to bytes
        output_bytes = io.BytesIO(output.getvalue().encode('utf-8-sig'))
        
        return output_bytes, 'text/csv; charset=utf-8', 'csv'
    
    def _export_to_excel(
        self,
        data: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        **kwargs
    ) -> tuple[io.BytesIO, str, str]:
        """Export data to Excel format."""
        import xlsxwriter
        
        output = io.BytesIO()
        
        # Create a workbook and add a worksheet
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Write data to Excel
            df.to_excel(writer, sheet_name='Report', index=False)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Report']
            
            # Add metadata to a separate sheet
            if metadata:
                meta_df = pd.DataFrame([
                    {"Key": key, "Value": str(value)} 
                    for key, value in metadata.items()
                ])
                meta_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            # Add some formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Format the header row
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Auto-adjust column widths
            for i, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.set_column(i, i, min(max_length + 2, 50))
        
        output.seek(0)
        return output, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx'
    
    def _export_to_json(
        self,
        data: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        **kwargs
    ) -> tuple[io.BytesIO, str, str]:
        """Export data to JSON format."""
        result = {
            "metadata": metadata,
            "data": data
        }
        
        output = io.BytesIO()
        output.write(json.dumps(result, indent=2, default=str).encode('utf-8'))
        output.seek(0)
        
        return output, 'application/json', 'json'
    
    def _export_to_pdf(
        self,
        data: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        **kwargs
    ) -> tuple[io.BytesIO, str, str]:
        """Export data to PDF format."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        output = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(letter) if kwargs.get('landscape', False) else letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )
        
        # Prepare styles
        styles = getSampleStyleSheet()
        elements = []
        
        # Add title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=1  # Center
        )
        
        title = f"{metadata.get('report_type', 'Tax Report').title()} Report"
        elements.append(Paragraph(title, title_style))
        
        # Add metadata
        meta_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12
        )
        
        meta_text = []
        for key, value in metadata.items():
            if key != 'report_type':
                meta_text.append(f"<b>{key.replace('_', ' ').title()}:</b> {value}")
        
        if meta_text:
            elements.append(Paragraph("<br/>".join(meta_text), meta_style))
        
        # Prepare table data
        if data:
            # Extract column headers
            headers = list(data[0].keys())
            table_data = [headers]
            
            # Add data rows
            for row in data:
                table_data.append([str(row.get(header, '')) for header in headers])
            
            # Create table
            table = Table(table_data)
            
            # Add style
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            # Add the table to the elements
            elements.append(table)
        else:
            elements.append(Paragraph("No data available", styles['Normal']))
        
        # Add footer
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            styles['Italic']
        ))
        
        # Build the PDF
        doc.build(elements)
        output.seek(0)
        
        return output, 'application/pdf', 'pdf'
    
    async def _save_export_file(
        self,
        file_obj: io.BytesIO,
        filename: str,
        content_type: str
    ) -> str:
        """
        Save the export file to storage.
        
        Args:
            file_obj: File-like object containing the export data
            filename: Name of the file
            content_type: MIME type of the file
            
        Returns:
            URL or path to the saved file
        """
        # In a real implementation, this would save to cloud storage (S3, GCS, etc.)
        # and return a download URL. For now, we'll just return a placeholder.
        
        # Reset file pointer to beginning
        file_obj.seek(0)
        
        # In a real implementation, you would do something like:
        # if settings.STORAGE_PROVIDER == 's3':
        #     return await self._save_to_s3(file_obj, filename, content_type)
        # elif settings.STORAGE_PROVIDER == 'local':
        #     return await self._save_to_local(file_obj, filename, content_type)
        # else:
        #     raise ValueError(f"Unsupported storage provider: {settings.STORAGE_PROVIDER}")
        
        # For now, just return a placeholder URL
        return f"/exports/tax_reports/{filename}"
    
    async def get_export_status(
        self,
        export_id: str,
        company_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get the status of an export.
        
        Args:
            export_id: ID of the export
            company_id: ID of the company
            user_id: ID of the user
            
        Returns:
            Dict with export status and metadata
        """
        export = self.db.query(models.TaxExport).filter(
            models.TaxExport.id == export_id,
            models.TaxExport.company_id == company_id,
            models.TaxExport.user_id == user_id
        ).first()
        
        if not export:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Export {export_id} not found"
            )
            
        return {
            "id": export.id,
            "status": export.status,
            "filename": export.filename,
            "file_size": export.file_size,
            "download_url": export.download_url,
            "created_at": export.created_at,
            "started_at": export.started_at,
            "completed_at": export.completed_at,
            "processing_time": export.processing_time,
            "error_message": export.error_message
        }
    
    async def get_export_file(
        self,
        export_id: str,
        company_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get the exported file.
        
        Args:
            export_id: ID of the export
            company_id: ID of the company
            user_id: ID of the user
            
        Returns:
            Dict with file data and metadata
        """
        export = self.db.query(models.TaxExport).filter(
            models.TaxExport.id == export_id,
            models.TaxExport.company_id == company_id,
            models.TaxExport.user_id == user_id
        ).first()
        
        if not export:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Export {export_id} not found"
            )
            
        if export.status != ExportStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Export {export_id} is not complete. Status: {export.status}"
            )
        
        # In a real implementation, this would retrieve the file from storage
        # For now, we'll just return a placeholder
        return {
            "id": export.id,
            "filename": export.filename,
            "content_type": self._get_content_type(export.filename),
            "file_size": export.file_size,
            "download_url": export.download_url,
            "status": export.status
        }
    
    def _get_content_type(self, filename: str) -> str:
        """Get the content type based on file extension."""
        if filename.endswith('.csv'):
            return 'text/csv'
        elif filename.endswith(('.xls', '.xlsx')):
            return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif filename.endswith('.json'):
            return 'application/json'
        elif filename.endswith('.pdf'):
            return 'application/pdf'
        else:
            return 'application/octet-stream'
