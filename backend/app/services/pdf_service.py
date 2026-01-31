"""
PDF generation service for the application.
"""
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from typing import Dict, Any, Optional
import os

from io import BytesIO



class PDFService:
    """Service for generating PDF documents."""
    
    def __init__(self):
        # Register fonts
        self._register_fonts()
        
        # Define styles
        self.styles = getSampleStyleSheet()
        self._define_custom_styles()
    
    def _register_fonts(self):
        # Try to register common font paths
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            'C:/Windows/Fonts/arialbd.ttf',
            'C:/Windows/Fonts/arial.ttf',
            '/Library/Fonts/Arial Bold.ttf',
            '/Library/Fonts/Arial.ttf',
        ]
        
        # Register bold and regular fonts
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('Arial-Bold', font_path.replace('ttf', 'ttf').replace('TTF', 'ttf').replace('Arial', 'Arial-Bold')))
                    pdfmetrics.registerFont(TTFont('Arial', font_path.replace('ttf', 'ttf').replace('TTF', 'ttf')))
                    break
                except Exception as e:
                    print(f"Error registering font {font_path}: {e}")
        else:
            # Fallback to built-in fonts
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'Helvetica-Bold'))
            pdfmetrics.registerFont(TTFont('Arial', 'Helvetica'))
    
    def _define_custom_styles(self):
        # Title style
        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Heading1'],
            fontName='Arial-Bold',
            fontSize=16,
            spaceAfter=12,
            alignment=1,  # Center aligned
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontName='Arial-Bold',
            fontSize=12,
            spaceAfter=6,
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontName='Arial',
            fontSize=10,
            spaceAfter=6,
        ))
        
        # Small text style
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Italic'],
            fontName='Arial',
            fontSize=8,
            spaceAfter=6,
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Italic'],
            fontName='Arial',
            fontSize=8,
            spaceBefore=12,
            textColor=colors.grey,
            alignment=1,  # Center aligned
        ))
    
    def generate_tax_exemption_certificate(self, certificate_data: Dict[str, Any]) -> BytesIO:
        """
        Generate a tax exemption certificate PDF.
        
        Args:
            certificate_data: Dictionary containing certificate data
            
        Returns:
            BytesIO: In-memory PDF file
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )
        
        # Prepare the content
        elements = []
        
        # Add title
        elements.append(Paragraph("TAX EXEMPTION CERTIFICATE", self.styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Add certificate info
        info_data = [
            ["Certificate Number:", certificate_data.get('certificate_number', 'N/A')],
            ["Issue Date:", self._format_date(certificate_data.get('issue_date'))],
            ["Expiry Date:", self._format_date(certificate_data.get('expiry_date'))],
            ["Status:", "Active" if certificate_data.get('is_active', False) else "Inactive"],
        ]
        
        info_table = Table(info_data, colWidths=[120, 300])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Arial-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 24))
        
        # Add customer info
        elements.append(Paragraph("CUSTOMER INFORMATION", self.styles['Subtitle']))
        elements.append(Spacer(1, 6))
        
        customer_data = [
            ["Customer Name:", certificate_data.get('customer_name', 'N/A')],
            ["Tax ID:", certificate_data.get('customer_tax_id', 'N/A')],
            ["Exemption Type:", certificate_data.get('exemption_type', 'N/A')],
            ["Issuing Jurisdiction:", certificate_data.get('issuing_jurisdiction', 'N/A')],
        ]
        
        customer_table = Table(customer_data, colWidths=[120, 300])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Arial-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(customer_table)
        elements.append(Spacer(1, 24))
        
        # Add tax codes
        tax_codes = certificate_data.get('tax_codes', [])
        if tax_codes:
            elements.append(Paragraph("APPLICABLE TAX CODES", self.styles['Subtitle']))
            elements.append(Spacer(1, 6))
            
            tax_code_data = [["Tax Code"]]
            for code in tax_codes:
                tax_code_data.append([code])
            
            tax_code_table = Table(tax_code_data, colWidths=[420])
            tax_code_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Arial-Bold'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(tax_code_table)
            elements.append(Spacer(1, 24))
        
        # Add notes if available
        notes = certificate_data.get('notes')
        if notes:
            elements.append(Paragraph("NOTES", self.styles['Subtitle']))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(notes, self.styles['BodyText']))
            elements.append(Spacer(1, 12))
        
        # Add footer
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Paksa Financial System",
            self.styles['Footer']
        ))
        
        # Build the PDF
        doc.build(elements)
        
        # Reset buffer position to the beginning
        buffer.seek(0)
        return buffer
    
    def _format_date(self, date_str: Optional[str]) -> str:
        if not date_str:
            return 'N/A'
        try:
            # Try to parse ISO format date
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%B %d, %Y')
        except (ValueError, AttributeError):
            return str(date_str)

# Create a singleton instance
pdf_service = PDFService()
