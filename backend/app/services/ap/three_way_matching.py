"""
Three-way matching service for AP (Purchase Order - Receipt - Invoice).
"""
from typing import Dict, Any
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session


class ThreeWayMatchingService:
    """Service for three-way matching validation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_match(
        self,
        po_id: UUID,
        receipt_id: UUID,
        invoice_id: UUID,
        tolerance_percent: Decimal = Decimal('5.0')
    ) -> Dict[str, Any]:
        """Validate three-way match between PO, Receipt, and Invoice."""
        
        po = self._get_purchase_order(po_id)
        receipt = self._get_receipt(receipt_id)
        invoice = self._get_invoice(invoice_id)
        
        discrepancies = []
        
        qty_match = self._validate_quantity(po, receipt, invoice, tolerance_percent)
        if not qty_match['matched']:
            discrepancies.append(qty_match)
        
        price_match = self._validate_price(po, receipt, invoice, tolerance_percent)
        if not price_match['matched']:
            discrepancies.append(price_match)
        
        amount_match = self._validate_amount(po, receipt, invoice, tolerance_percent)
        if not amount_match['matched']:
            discrepancies.append(amount_match)
        
        is_matched = len(discrepancies) == 0
        
        return {
            'matched': is_matched,
            'match_status': 'MATCHED' if is_matched else 'DISCREPANCY',
            'discrepancies': discrepancies,
            'po_id': str(po_id),
            'receipt_id': str(receipt_id),
            'invoice_id': str(invoice_id),
            'tolerance_percent': float(tolerance_percent)
        }
    
    def _validate_quantity(self, po: Dict, receipt: Dict, invoice: Dict, tolerance: Decimal) -> Dict[str, Any]:
        """Validate quantity matching."""
        po_qty = Decimal(str(po.get('quantity', 0)))
        receipt_qty = Decimal(str(receipt.get('quantity', 0)))
        invoice_qty = Decimal(str(invoice.get('quantity', 0)))
        
        variance = abs(invoice_qty - receipt_qty)
        variance_percent = (variance / receipt_qty * 100) if receipt_qty > 0 else Decimal('0')
        
        return {
            'type': 'QUANTITY',
            'matched': variance_percent <= tolerance,
            'po_value': float(po_qty),
            'receipt_value': float(receipt_qty),
            'invoice_value': float(invoice_qty),
            'variance': float(variance),
            'variance_percent': float(variance_percent)
        }
    
    def _validate_price(self, po: Dict, receipt: Dict, invoice: Dict, tolerance: Decimal) -> Dict[str, Any]:
        """Validate price matching."""
        po_price = Decimal(str(po.get('unit_price', 0)))
        invoice_price = Decimal(str(invoice.get('unit_price', 0)))
        
        variance = abs(invoice_price - po_price)
        variance_percent = (variance / po_price * 100) if po_price > 0 else Decimal('0')
        
        return {
            'type': 'PRICE',
            'matched': variance_percent <= tolerance,
            'po_value': float(po_price),
            'invoice_value': float(invoice_price),
            'variance': float(variance),
            'variance_percent': float(variance_percent)
        }
    
    def _validate_amount(self, po: Dict, receipt: Dict, invoice: Dict, tolerance: Decimal) -> Dict[str, Any]:
        """Validate total amount matching."""
        po_amount = Decimal(str(po.get('total_amount', 0)))
        invoice_amount = Decimal(str(invoice.get('total_amount', 0)))
        
        variance = abs(invoice_amount - po_amount)
        variance_percent = (variance / po_amount * 100) if po_amount > 0 else Decimal('0')
        
        return {
            'type': 'AMOUNT',
            'matched': variance_percent <= tolerance,
            'po_value': float(po_amount),
            'invoice_value': float(invoice_amount),
            'variance': float(variance),
            'variance_percent': float(variance_percent)
        }
    
    def _get_purchase_order(self, po_id: UUID) -> Dict:
        return {}
    
    def _get_receipt(self, receipt_id: UUID) -> Dict:
        return {}
    
    def _get_invoice(self, invoice_id: UUID) -> Dict:
        return {}
