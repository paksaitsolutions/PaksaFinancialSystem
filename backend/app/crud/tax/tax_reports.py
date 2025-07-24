"""
CRUD operations for tax reporting.
"""
from typing import List, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tax.tax_rate import TaxRate, TaxExemption

class TaxReportsCRUD:
    """CRUD operations for tax reports."""
    
    async def get_tax_summary_report(
        self, 
        db: AsyncSession,
        *,
        from_date: date,
        to_date: date,
        tax_type: str = None
    ) -> Dict[str, Any]:
        """Generate tax summary report."""
        # This would integrate with actual transaction data
        # For now, returning mock structure
        
        query = select(TaxRate).where(TaxRate.is_active == True)
        if tax_type:
            query = query.where(TaxRate.tax_type == tax_type)
        
        result = await db.execute(query)
        tax_rates = result.scalars().all()
        
        summary = {
            "period": {
                "from_date": from_date.isoformat(),
                "to_date": to_date.isoformat()
            },
            "total_tax_collected": Decimal("15000.00"),
            "total_tax_paid": Decimal("12000.00"),
            "net_tax_liability": Decimal("3000.00"),
            "by_tax_type": [
                {
                    "tax_type": "sales",
                    "collected": Decimal("8000.00"),
                    "paid": Decimal("6000.00"),
                    "net": Decimal("2000.00")
                },
                {
                    "tax_type": "vat",
                    "collected": Decimal("7000.00"),
                    "paid": Decimal("6000.00"),
                    "net": Decimal("1000.00")
                }
            ],
            "active_rates": len(tax_rates)
        }
        
        return summary
    
    async def get_exemption_report(self, db: AsyncSession) -> Dict[str, Any]:
        """Generate tax exemption report."""
        # Active exemptions
        active_query = select(func.count()).select_from(TaxExemption).where(
            TaxExemption.is_active == True
        )
        active_result = await db.execute(active_query)
        active_count = active_result.scalar() or 0
        
        # Expiring soon (next 30 days)
        expiring_date = date.today() + timedelta(days=30)
        expiring_query = select(func.count()).select_from(TaxExemption).where(
            and_(
                TaxExemption.is_active == True,
                TaxExemption.expiry_date <= expiring_date,
                TaxExemption.expiry_date > date.today()
            )
        )
        expiring_result = await db.execute(expiring_query)
        expiring_count = expiring_result.scalar() or 0
        
        return {
            "active_exemptions": active_count,
            "expiring_soon": expiring_count,
            "total_tax_saved": Decimal("5000.00"),  # Mock data
            "by_type": [
                {"type": "resale", "count": 15, "saved": Decimal("3000.00")},
                {"type": "nonprofit", "count": 8, "saved": Decimal("2000.00")}
            ]
        }

# Create an instance for dependency injection
tax_reports_crud = TaxReportsCRUD()