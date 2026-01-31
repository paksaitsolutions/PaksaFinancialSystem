"""
Tax Service with AP/AR Integration
"""
from decimal import Decimal
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import TaxRate, APInvoice, ARInvoice, JournalEntry, JournalEntryLine
from app.services.base import BaseService


class TaxService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, TaxRate)
    
    def calculate_tax_for_ap_invoice(self, invoice: APInvoice) -> Decimal:
        tax_rate = self.db.query(TaxRate).filter(
            TaxRate.company_id == invoice.company_id,
            TaxRate.is_active == True
        ).first()
        
        if not tax_rate:
            return Decimal('0')
        
        tax_amount = invoice.subtotal * (tax_rate.rate_percentage / 100)
        invoice.tax_amount = tax_amount
        invoice.total_amount = invoice.subtotal + tax_amount
        return tax_amount
    
    def calculate_tax_for_ar_invoice(self, invoice: ARInvoice) -> Decimal:
        tax_rate = self.db.query(TaxRate).filter(
            TaxRate.company_id == invoice.company_id,
            TaxRate.is_active == True
        ).first()
        
        if not tax_rate:
            return Decimal('0')
        
        tax_amount = invoice.subtotal * (tax_rate.rate_percentage / 100)
        invoice.tax_amount = tax_amount
        invoice.total_amount = invoice.subtotal + tax_amount
        return tax_amount