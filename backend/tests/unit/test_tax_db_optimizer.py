"""
Unit tests for TaxQueryOptimizer class.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.tax.db_optimizer import TaxQueryOptimizer
from app.models import Base, TaxTransaction

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sample test data
TEST_COMPANY_ID = "test_company_123"
TEST_DATA = [
    {
        "id": "txn_1",
        "company_id": TEST_COMPANY_ID,
        "transaction_date": date(2023, 1, 15),
        "tax_type": "VAT",
        "jurisdiction_code": "US-CA",
        "taxable_amount": Decimal("100.00"),
        "tax_amount": Decimal("8.25"),
        "is_reported": False,
    },
    {
        "id": "txn_2",
        "company_id": TEST_COMPANY_ID,
        "transaction_date": date(2023, 1, 20),
        "tax_type": "VAT",
        "jurisdiction_code": "US-CA",
        "taxable_amount": Decimal("200.00"),
        "tax_amount": Decimal("16.50"),
        "is_reported": False,
    },
    {
        "id": "txn_3",
        "company_id": TEST_COMPANY_ID,
        "transaction_date": date(2023, 2, 10),
        "tax_type": "GST",
        "jurisdiction_code": "CA-ON",
        "taxable_amount": Decimal("150.00"),
        "tax_amount": Decimal("19.50"),
        "is_reported": False,
    },
]

@pytest.fixture(scope="module")
def db():
    """Create a clean test database for each test module."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    db = TestingSessionLocal()
    
    # Insert test data
    for item in TEST_DATA:
        db.add(TaxTransaction(**item))
    db.commit()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

class TestTaxQueryOptimizer:
    """Test cases for TaxQueryOptimizer class."""
    
    def test_get_liability_report_data_monthly(self, db):
        """Test getting liability report data grouped by month."""
        optimizer = TaxQueryOptimizer(db)
        
        # Test with date range that includes all test data
        results, total_count = optimizer.get_liability_report_data(
            company_id=TEST_COMPANY_ID,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            group_by="month"
        )
        
        # Verify results
        assert total_count == 2  # 2 unique month/tax_type/jurisdiction combinations
        assert len(results) == 2
        
        # Check that amounts are summed correctly
        jan_txn = next(r for r in results if r["period"] == "2023-01")
        assert jan_txn["tax_type"] == "VAT"
        assert jan_txn["taxable_amount"] == Decimal("300.00")
        assert jan_txn["tax_amount"] == Decimal("24.75")
        assert jan_txn["transaction_count"] == 2
        
        feb_txn = next(r for r in results if r["period"] == "2023-02")
        assert feb_txn["tax_type"] == "GST"
        assert feb_txn["taxable_amount"] == Decimal("150.00")
        assert feb_txn["tax_amount"] == Decimal("19.50")
        assert feb_txn["transaction_count"] == 1
    
    def test_get_liability_report_data_filtered(self, db):
        """Test getting liability report data with filters."""
        optimizer = TaxQueryOptimizer(db)
        
        # Test with tax type filter
        results, total_count = optimizer.get_liability_report_data(
            company_id=TEST_COMPANY_ID,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            tax_types=["VAT"],
            group_by="month"
        )
        
        # Should only return VAT transactions
        assert total_count == 1
        assert len(results) == 1
        assert results[0]["tax_type"] == "VAT"
        assert results[0]["taxable_amount"] == Decimal("300.00")
    
    def test_get_liability_report_data_pagination(self, db):
        """Test pagination of liability report data."""
        optimizer = TaxQueryOptimizer(db)
        
        # First page
        results_page1, total_count = optimizer.get_liability_report_data(
            company_id=TEST_COMPANY_ID,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            group_by="month",
            page=1,
            page_size=1
        )
        
        # Second page
        results_page2, _ = optimizer.get_liability_report_data(
            company_id=TEST_COMPANY_ID,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            group_by="month",
            page=2,
            page_size=1
        )
        
        # Verify pagination
        assert total_count == 2
        assert len(results_page1) == 1
        assert len(results_page2) == 1
        assert results_page1[0]["period"] != results_page2[0]["period"]
    
    def test_get_liability_report_data_no_results(self, db):
        """Test getting liability report data with no matching results."""
        optimizer = TaxQueryOptimizer(db)
        
        results, total_count = optimizer.get_liability_report_data(
            company_id="nonexistent_company",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            group_by="month"
        )
        
        assert total_count == 0
        assert len(results) == 0
    
    def test_get_liability_report_data_invalid_group_by(self, db):
        """Test getting liability report data with invalid group_by parameter."""
        optimizer = TaxQueryOptimizer(db)
        
        # Should default to "month" grouping
        results, _ = optimizer.get_liability_report_data(
            company_id=TEST_COMPANY_ID,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            group_by="invalid_group"
        )
        
        # Should still return results with default grouping
        assert len(results) > 0

    def test_get_liability_report_data_different_jurisdictions(self, db):
        """Test getting liability report data with different jurisdictions."""
        optimizer = TaxQueryOptimizer(db)
        
        # Add a transaction with a different jurisdiction
        db.add(TaxTransaction(
            id="txn_4",
            company_id=TEST_COMPANY_ID,
            transaction_date=date(2023, 3, 15),
            tax_type="VAT",
            jurisdiction_code="US-NY",
            taxable_amount=Decimal("400.00"),
            tax_amount=Decimal("32.80"),
            is_reported=False
        ))
        db.commit()
        
        # Get report without jurisdiction filter
        results, total_count = optimizer.get_liability_report_data(
            company_id=TEST_COMPANY_ID,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            group_by="month"
        )
        
        # Should return all jurisdictions
        assert total_count == 3
        
        # Get report with jurisdiction filter
        results_filtered, filtered_count = optimizer.get_liability_report_data(
            company_id=TEST_COMPANY_ID,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            jurisdiction_codes=["US-NY"],
            group_by="month"
        )
        
        # Should only return the NY transaction
        assert filtered_count == 1
        assert results_filtered[0]["jurisdiction_code"] == "US-NY"
        assert results_filtered[0]["taxable_amount"] == Decimal("400.00")
