"""
Initialize tax data with sample rates and jurisdictions.
"""
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.tax_models import TaxRate, TaxJurisdiction
from app.services.tax_service import TaxService

def init_tax_data():
    """Initialize tax data with sample rates."""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_rates = db.query(TaxRate).count()
        if existing_rates > 0:
            print("Tax data already exists, skipping initialization")
            return

        # Create sample tax rates
        sample_rates = [
            {
                "name": "California Sales Tax",
                "code": "CA-SALES",
                "rate": Decimal("7.25"),
                "tax_type": "sales",
                "jurisdiction": "California",
                "country_code": "US",
                "state_code": "CA",
                "description": "California state sales tax"
            },
            {
                "name": "New York Sales Tax",
                "code": "NY-SALES", 
                "rate": Decimal("8.00"),
                "tax_type": "sales",
                "jurisdiction": "New York",
                "country_code": "US",
                "state_code": "NY",
                "description": "New York state sales tax"
            },
            {
                "name": "UK VAT Standard Rate",
                "code": "UK-VAT-STD",
                "rate": Decimal("20.00"),
                "tax_type": "vat",
                "jurisdiction": "United Kingdom",
                "country_code": "GB",
                "description": "UK VAT standard rate"
            },
            {
                "name": "Canada GST",
                "code": "CA-GST",
                "rate": Decimal("5.00"),
                "tax_type": "gst",
                "jurisdiction": "Canada",
                "country_code": "CA",
                "description": "Canada Goods and Services Tax"
            },
            {
                "name": "Texas Sales Tax",
                "code": "TX-SALES",
                "rate": Decimal("6.25"),
                "tax_type": "sales",
                "jurisdiction": "Texas",
                "country_code": "US",
                "state_code": "TX",
                "description": "Texas state sales tax"
            }
        ]

        tax_service = TaxService(db)
        
        for rate_data in sample_rates:
            tax_rate = tax_service.create_tax_rate(**rate_data)
            print(f"Created tax rate: {tax_rate.name} ({tax_rate.code})")

        # Create sample jurisdictions
        sample_jurisdictions = [
            {
                "name": "United States",
                "code": "US",
                "jurisdiction_type": "country",
                "tax_id_required": True,
                "tax_id_format": "XX-XXXXXXX",
                "filing_frequency": "quarterly"
            },
            {
                "name": "United Kingdom", 
                "code": "GB",
                "jurisdiction_type": "country",
                "tax_id_required": True,
                "tax_id_format": "GB999999999",
                "filing_frequency": "quarterly"
            },
            {
                "name": "Canada",
                "code": "CA", 
                "jurisdiction_type": "country",
                "tax_id_required": True,
                "tax_id_format": "999999999RT0001",
                "filing_frequency": "quarterly"
            }
        ]

        for jurisdiction_data in sample_jurisdictions:
            jurisdiction = TaxJurisdiction(**jurisdiction_data)
            db.add(jurisdiction)
            db.commit()
            db.refresh(jurisdiction)
            print(f"Created jurisdiction: {jurisdiction.name} ({jurisdiction.code})")

        print("Tax data initialization completed successfully!")

    except Exception as e:
        print(f"Error initializing tax data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_tax_data()