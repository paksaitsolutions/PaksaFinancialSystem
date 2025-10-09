"""
Tax service for calculations and management.
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.tax_models import TaxRate, TaxTransaction, TaxExemption, TaxReturn, TaxJurisdiction
from app.core.database import get_db

class TaxService:
    """Service for tax calculations and management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_tax(
        self,
        amount: Decimal,
        tax_type: str,
        jurisdiction: str,
        country_code: str,
        state_code: Optional[str] = None,
        city: Optional[str] = None,
        calculation_date: Optional[date] = None,
        exemption_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate tax for a given amount and jurisdiction."""
        
        if calculation_date is None:
            calculation_date = date.today()
        
        # Check for exemption first
        if exemption_id:
            exemption = self.db.query(TaxExemption).filter(
                TaxExemption.id == exemption_id,
                TaxExemption.status == "active"
            ).first()
            
            if exemption and tax_type in exemption.tax_types:
                return {
                    "taxable_amount": amount,
                    "tax_amount": Decimal("0.00"),
                    "total_amount": amount,
                    "tax_rate": Decimal("0.00"),
                    "exemption_applied": True,
                    "exemption_certificate": exemption.certificate_number
                }
        
        # Find applicable tax rate
        query = self.db.query(TaxRate).filter(
            TaxRate.tax_type == tax_type,
            TaxRate.country_code == country_code,
            TaxRate.status == "active",
            TaxRate.effective_date <= calculation_date
        ).filter(
            or_(TaxRate.expiry_date.is_(None), TaxRate.expiry_date >= calculation_date)
        )
        
        if state_code:
            query = query.filter(TaxRate.state_code == state_code)
        if city:
            query = query.filter(TaxRate.city == city)
        
        tax_rate = query.first()
        
        if not tax_rate:
            return {
                "taxable_amount": amount,
                "tax_amount": Decimal("0.00"),
                "total_amount": amount,
                "tax_rate": Decimal("0.00"),
                "exemption_applied": False,
                "error": "No applicable tax rate found"
            }
        
        tax_amount = amount * (tax_rate.rate / 100)
        
        return {
            "taxable_amount": amount,
            "tax_amount": tax_amount,
            "total_amount": amount + tax_amount,
            "tax_rate": tax_rate.rate,
            "tax_rate_id": str(tax_rate.id),
            "tax_rate_name": tax_rate.name,
            "exemption_applied": False
        }
    
    def create_tax_transaction(
        self,
        transaction_id: str,
        entity_type: str,
        entity_id: str,
        tax_rate_id: str,
        taxable_amount: Decimal,
        tax_amount: Decimal,
        description: Optional[str] = None,
        reference: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> TaxTransaction:
        """Create a tax transaction record."""
        
        transaction = TaxTransaction(
            transaction_id=transaction_id,
            entity_type=entity_type,
            entity_id=entity_id,
            tax_rate_id=tax_rate_id,
            taxable_amount=taxable_amount,
            tax_amount=tax_amount,
            total_amount=taxable_amount + tax_amount,
            description=description,
            reference=reference,
            created_by=created_by
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def get_tax_rates(
        self,
        tax_type: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        active_only: bool = True
    ) -> List[TaxRate]:
        """Get tax rates with optional filtering."""
        
        query = self.db.query(TaxRate)
        
        if tax_type:
            query = query.filter(TaxRate.tax_type == tax_type)
        if jurisdiction:
            query = query.filter(TaxRate.jurisdiction == jurisdiction)
        if active_only:
            query = query.filter(TaxRate.status == "active")
        
        return query.all()
    
    def create_tax_rate(
        self,
        name: str,
        code: str,
        rate: Decimal,
        tax_type: str,
        jurisdiction: str,
        country_code: str,
        state_code: Optional[str] = None,
        city: Optional[str] = None,
        effective_date: Optional[date] = None,
        expiry_date: Optional[date] = None,
        description: Optional[str] = None
    ) -> TaxRate:
        """Create a new tax rate."""
        
        if effective_date is None:
            effective_date = date.today()
        
        tax_rate = TaxRate(
            name=name,
            code=code,
            rate=rate,
            tax_type=tax_type,
            jurisdiction=jurisdiction,
            country_code=country_code,
            state_code=state_code,
            city=city,
            effective_date=effective_date,
            expiry_date=expiry_date,
            description=description
        )
        
        self.db.add(tax_rate)
        self.db.commit()
        self.db.refresh(tax_rate)
        
        return tax_rate
    
    def get_tax_transactions(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[TaxTransaction]:
        """Get tax transactions with optional filtering."""
        
        query = self.db.query(TaxTransaction)
        
        if entity_type:
            query = query.filter(TaxTransaction.entity_type == entity_type)
        if entity_id:
            query = query.filter(TaxTransaction.entity_id == entity_id)
        if start_date:
            query = query.filter(TaxTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(TaxTransaction.transaction_date <= end_date)
        
        return query.order_by(TaxTransaction.transaction_date.desc()).all()
    
    def create_tax_exemption(
        self,
        certificate_number: str,
        entity_type: str,
        entity_id: str,
        exemption_type: str,
        tax_types: List[str],
        jurisdiction: Optional[str] = None,
        issue_date: Optional[date] = None,
        expiry_date: Optional[date] = None,
        issuing_authority: Optional[str] = None,
        notes: Optional[str] = None
    ) -> TaxExemption:
        """Create a tax exemption certificate."""
        
        if issue_date is None:
            issue_date = date.today()
        
        exemption = TaxExemption(
            certificate_number=certificate_number,
            entity_type=entity_type,
            entity_id=entity_id,
            exemption_type=exemption_type,
            tax_types=tax_types,
            jurisdiction=jurisdiction,
            issue_date=issue_date,
            expiry_date=expiry_date,
            issuing_authority=issuing_authority,
            notes=notes
        )
        
        self.db.add(exemption)
        self.db.commit()
        self.db.refresh(exemption)
        
        return exemption
    
    def get_tax_summary(
        self,
        start_date: date,
        end_date: date,
        tax_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get tax summary for a period."""
        
        query = self.db.query(TaxTransaction).filter(
            TaxTransaction.transaction_date >= start_date,
            TaxTransaction.transaction_date <= end_date
        )
        
        if tax_type:
            query = query.join(TaxRate).filter(TaxRate.tax_type == tax_type)
        
        transactions = query.all()
        
        total_taxable = sum(t.taxable_amount for t in transactions)
        total_tax = sum(t.tax_amount for t in transactions)
        
        # Group by tax type
        by_tax_type = {}
        for transaction in transactions:
            tax_rate = transaction.tax_rate
            if tax_rate.tax_type not in by_tax_type:
                by_tax_type[tax_rate.tax_type] = {
                    "taxable_amount": Decimal("0.00"),
                    "tax_amount": Decimal("0.00"),
                    "transaction_count": 0
                }
            
            by_tax_type[tax_rate.tax_type]["taxable_amount"] += transaction.taxable_amount
            by_tax_type[tax_rate.tax_type]["tax_amount"] += transaction.tax_amount
            by_tax_type[tax_rate.tax_type]["transaction_count"] += 1
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_taxable_amount": total_taxable,
                "total_tax_amount": total_tax,
                "transaction_count": len(transactions)
            },
            "by_tax_type": by_tax_type
        }