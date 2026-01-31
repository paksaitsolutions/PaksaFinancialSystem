"""
Early payment discount automation service.
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session


class EarlyPaymentDiscountService:
    """Service for automating early payment discounts."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_discount(
        self,
        invoice_amount: Decimal,
        invoice_date: date,
        payment_date: date,
        discount_terms: str
    ) -> Dict[str, Any]:
        """Calculate early payment discount based on terms (e.g., '2/10 net 30')."""
        
        discount_percent, discount_days, net_days = self._parse_terms(discount_terms)
        
        days_diff = (payment_date - invoice_date).days
        
        if days_diff <= discount_days:
            discount_amount = invoice_amount * (discount_percent / 100)
            net_amount = invoice_amount - discount_amount
            eligible = True
        else:
            discount_amount = Decimal('0')
            net_amount = invoice_amount
            eligible = False
        
        return {
            'eligible': eligible,
            'discount_percent': float(discount_percent),
            'discount_amount': float(discount_amount),
            'net_amount': float(net_amount),
            'invoice_amount': float(invoice_amount),
            'days_to_pay': days_diff,
            'discount_deadline': invoice_date + timedelta(days=discount_days),
            'payment_deadline': invoice_date + timedelta(days=net_days)
        }
    
    def _parse_terms(self, terms: str) -> tuple:
        """Parse discount terms like '2/10 net 30'."""
        try:
            parts = terms.lower().split()
            discount_part = parts[0].split('/')
            discount_percent = Decimal(discount_part[0])
            discount_days = int(discount_part[1])
            net_days = int(parts[2])
            return discount_percent, discount_days, net_days
        except:
            return Decimal('0'), 0, 30
