"""
Export Service

Provides consistent export functionality (Excel, CSV, PDF) across all modules.
"""
from typing import Any, Dict, List, Optional, Union, BinaryIO
from datetime import datetime
import io
import csv
import os
import logging
from enum import Enum
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak,
    ListFlowable, ListItem, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus.flowables import KeepTogether, PageBreakIfTooFull
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate, Frame
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)

class ExportFormat(str, Enum):
    EXCEL = "excel"
    CSV = "csv"
    PDF = "pdf"

class ExportService:
    """Service for exporting data in various formats."""
    
    def __init__(self, company_name: str = "Paksa Financial System"):
        self.company_name = company_name
        self._register_fonts()
    
    def _register_fonts(self):
        """Register custom fonts for PDF exports."""
        try:
            # Try to register a standard font
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
            self.font_name = 'DejaVuSans'
            self.bold_font_name = 'DejaVuSans-Bold'
        except:
            # Fall back to default fonts if custom fonts not available
            self.font_name = 'Helvetica'
            self.bold_font_name = 'Helvetica-Bold'
    
    def export(
        self,
        data: Union[List[Dict], pd.DataFrame],
        export_format: ExportFormat,
        filename: str,
        sheet_name: str = "Sheet1",
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        columns: Optional[List[Dict]] = None,
        **kwargs
    ) -> StreamingResponse:
        """
        Export data in the specified format.
        
        Args:
            data: Data to export (list of dicts or pandas DataFrame)
            export_format: Export format (excel, csv, pdf)
            filename: Base filename (without extension)
            sheet_name: Sheet name (for Excel only)
            title: Report title (for PDF only)
            subtitle: Report subtitle (for PDF only)
            columns: Column definitions (optional, for PDF only)
            **kwargs: Additional format-specific options
            
        Returns:
            StreamingResponse with the exported file
        """
        # Convert data to DataFrame if it's not already
        if not isinstance(data, pd.DataFrame):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Dispatch to the appropriate export method
        if export_format == ExportFormat.EXCEL:
            return self._export_excel(df, filename, sheet_name, **kwargs)
        elif export_format == ExportFormat.CSV:
            return self._export_csv(df, filename, **kwargs)
        elif export_format == ExportFormat.PDF:
            return self._export_pdf(df, filename, title, subtitle, columns, **kwargs)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {export_format}"
            )
    
    def _export_excel(
        self,
        df: pd.DataFrame,
        filename: str,
        sheet_name: str = "Sheet1",
        **kwargs
    ) -> StreamingResponse:
        """Export data to Excel format."""
        try:
            # Create a BytesIO buffer
            buffer = io.BytesIO()
            
            # Create Excel writer
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write data to Excel
                df.to_excel(writer, sheet_name=sheet_name, index=False, engine='xlsxwriter')
                
                # Get workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                
                # Add formats
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#2c3e50',
                    'color': 'white',
                    'border': 1
                })
                
                # Format the header row
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Auto-adjust column widths
                for i, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),  # Max length in column
                        len(str(col))  # Length of column name/header
                    )
                    # Set column width slightly larger than max length
                    worksheet.set_column(i, i, min(max_length + 2, 50))
                
                # Add a filter to the header row
                worksheet.autofilter(0, 0, 0, len(df.columns) - 1)
                
                # Freeze the header row
                worksheet.freeze_panes(1, 0)
                
                # Add company name and timestamp to footer
                worksheet.set_footer(f'&L{self.company_name} | &C{datetime.now().strftime("%Y-%m-%d %H:%M")} | &RPage &P of &N')
                
                # Close the writer to save the workbook
                writer.close()
            
            # Prepare the response
            buffer.seek(0)
            response = StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response.headers["Content-Disposition"] = f"attachment; filename={filename}.xlsx"
            response.headers["Content-Length"] = str(buffer.getbuffer().nbytes)
            
            return response
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating Excel export: {str(e)}"
            )
    
    def _export_csv(
        self,
        df: pd.DataFrame,
        filename: str,
        **kwargs
    ) -> StreamingResponse:
        """Export data to CSV format."""
        try:
            # Create a generator to stream the CSV data
            def generate_csv():
                # Create a buffer to hold CSV data
                buffer = io.StringIO()
                
                # Write the CSV data to the buffer
                df.to_csv(buffer, index=False, encoding='utf-8')
                
                # Yield the buffer contents in chunks
                buffer.seek(0)
                while True:
                    data = buffer.read(8192)  # 8KB chunks
                    if not data:
                        break
                    yield data.encode('utf-8')
            
            # Prepare the response
            response = StreamingResponse(
                generate_csv(),
                media_type="text/csv; charset=utf-8"
            )
            response.headers["Content-Disposition"] = f"attachment; filename={filename}.csv"
            
            return response
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating CSV export: {str(e)}"
            )
    
    def _export_pdf(
        self,
        df: pd.DataFrame,
        filename: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        columns: Optional[List[Dict]] = None,
        **kwargs
    ) -> StreamingResponse:
        """Export data to PDF format."""
        try:
            from io import BytesIO
            from reportlab.lib.pagesizes import landscape, A4
            from reportlab.platypus import (
                SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
                Image, PageBreak, PageTemplate, Frame, NextPageTemplate
            )
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, cm
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
            
            # Create a buffer to store the PDF
            buffer = BytesIO()
            
            # Set up the document with landscape orientation
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(A4) if kwargs.get('landscape', False) else A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=100,
                bottomMargin=60,
                title=title or "Export",
                author=self.company_name,
                subject=title or "Export",
                creator=f"{self.company_name} Export Service"
            )
            
            # Define styles
            styles = getSampleStyleSheet()
            
            # Add custom styles
            styles.add(ParagraphStyle(
                name='Title',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=12,
                textColor=colors.HexColor('#2c3e50'),
                fontName=self.bold_font_name,
                alignment=TA_CENTER
            ))
            
            styles.add(ParagraphStyle(
                name='Subtitle',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_CENTER
            ))
            
            # Create the elements list to hold all content
            elements = []
            
            # Add title and subtitle if provided
            if title:
                elements.append(Paragraph(title, styles['Title']))
            if subtitle:
                elements.append(Paragraph(subtitle, styles['Subtitle']))
            
            # Add a spacer
            elements.append(Spacer(1, 20))
            
            # Prepare table data
            table_data = [df.columns.tolist()]  # Header row
            
            # Add data rows
            for _, row in df.iterrows():
                table_data.append(row.tolist())
            
            # Create the table
            table = Table(table_data, repeatRows=1)
            
            # Add style to the table
            table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.bold_font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                
                # Data rows
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                
                # Highlight totals row if present
                ('FONTNAME', (0, -1), (-1, -1), self.bold_font_name),
            ]))
            
            # Add the table to the elements
            elements.append(table)
            
            # Build the PDF
            doc.build(elements)
            
            # Prepare the response
            buffer.seek(0)
            response = StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="application/pdf"
            )
            response.headers["Content-Disposition"] = f"attachment; filename={filename}.pdf"
            response.headers["Content-Length"] = str(buffer.getbuffer().nbytes)
            
            return response
            
        except Exception as e:
            logger.error(f"Error exporting to PDF: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating PDF export: {str(e)}"
            )

# Create a singleton instance
export_service = ExportService()
