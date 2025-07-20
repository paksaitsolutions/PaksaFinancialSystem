"""
Integration tests for Tax Reporting API endpoints.
"""

import json
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from app.main import app
from app.core.config import settings
from app.models import TaxTransaction, TaxExport, User, Company
from app.core.security import create_access_token
from app.db.session import SessionLocal

# Test client
client = TestClient(app)

# Test data
TEST_COMPANY_ID = "test_company_123"
TEST_USER_ID = "test_user_123"
TEST_TOKEN = create_access_token(
    data={"sub": TEST_USER_ID, "company_id": TEST_COMPANY_ID}
)

# Sample test data for tax transactions
TEST_TRANSACTIONS = [
    {
        "id": f"txn_{i}",
        "company_id": TEST_COMPANY_ID,
        "transaction_date": date(2023, 1, 15) + timedelta(days=i*10),
        "tax_type": "VAT",
        "jurisdiction_code": "US-CA",
        "taxable_amount": Decimal("100.00") * (i+1),
        "tax_amount": Decimal("8.25") * (i+1),
        "is_reported": False,
    }
    for i in range(5)
]

# Add some transactions with different tax types and jurisdictions
TEST_TRANSACTIONS.extend([
    {
        "id": "txn_gst_1",
        "company_id": TEST_COMPANY_ID,
        "transaction_date": date(2023, 2, 1),
        "tax_type": "GST",
        "jurisdiction_code": "CA-ON",
        "taxable_amount": Decimal("200.00"),
        "tax_amount": Decimal("26.00"),
        "is_reported": False,
    },
    {
        "id": "txn_vat_ny",
        "company_id": TEST_COMPANY_ID,
        "transaction_date": date(2023, 2, 15),
        "tax_type": "VAT",
        "jurisdiction_code": "US-NY",
        "taxable_amount": Decimal("150.00"),
        "tax_amount": Decimal("13.13"),
        "is_reported": False,
    }
])

@pytest.fixture(scope="module")
def db():
    """Create a clean test database for the test module."""
    db = SessionLocal()
    
    # Create test company
    company = Company(
        id=TEST_COMPANY_ID,
        name="Test Company",
        is_active=True
    )
    
    # Create test user
    user = User(
        id=TEST_USER_ID,
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        company_id=TEST_COMPANY_ID
    )
    
    # Add to database
    db.add(company)
    db.add(user)
    db.commit()
    
    # Add test transactions
    for txn_data in TEST_TRANSACTIONS:
        txn = TaxTransaction(**txn_data)
        db.add(txn)
    
    db.commit()
    
    yield db
    
    # Clean up
    db.query(TaxTransaction).delete()
    db.query(TaxExport).delete()
    db.query(User).delete()
    db.query(Company).delete()
    db.commit()
    db.close()

@pytest.fixture(scope="function")
auth_headers():
    """Return authentication headers with a valid token."""
    return {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }

class TestTaxReportingAPI:
    """Test cases for Tax Reporting API endpoints."""
    
    def test_get_tax_liability_report(self, db, auth_headers):
        """Test getting a tax liability report."""
        # Test with date range that includes all test data
        response = client.get(
            "/api/v1/tax/reports/liability",
            params={
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "group_by": "month"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return data and pagination info
        assert "data" in data
        assert "pagination" in data
        assert "filters" in data
        
        # Should have the expected number of results
        assert len(data["data"]) > 0
        
        # Check pagination info
        assert data["pagination"]["total"] > 0
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 100  # Default page size
    
    def test_get_tax_liability_report_filtered(self, db, auth_headers):
        """Test getting a filtered tax liability report."""
        # Test with tax type filter
        response = client.get(
            "/api/v1/tax/reports/liability",
            params={
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "tax_types": ["GST"],
                "group_by": "month"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return GST transactions
        assert all(tx["tax_type"] == "GST" for tx in data["data"])
    
    def test_get_tax_liability_report_invalid_dates(self, auth_headers):
        """Test getting a tax liability report with invalid date range."""
        # End date before start date
        response = client.get(
            "/api/v1/tax/reports/liability",
            params={
                "start_date": "2023-12-31",
                "end_date": "2023-01-01",
                "group_by": "month"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Start date must be before or equal to end date" in response.text
    
    @patch("app.api.v1.endpoints.tax.reporting.TaxReportExporter")
    def test_export_tax_report(self, mock_exporter, db, auth_headers):
        """Test exporting a tax report."""
        # Setup mock
        mock_instance = mock_exporter.return_value
        mock_instance.export_report.return_value = {
            "task_id": "export_123",
            "status": "processing",
            "message": "Export started in the background",
            "download_url": ""
        }
        
        # Test export request
        export_data = {
            "report_type": "liability",
            "format": "excel",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "include_metadata": True
        }
        
        response = client.post(
            "/api/v1/tax/reports/export",
            json=export_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return task info
        assert "task_id" in data
        assert data["status"] == "processing"
        
        # Should have called export_report with correct params
        mock_instance.export_report.assert_called_once()
        call_args = mock_instance.export_report.call_args[1]
        assert call_args["company_id"] == TEST_COMPANY_ID
        assert call_args["report_type"] == "liability"
        assert call_args["format"] == "excel"
    
    @patch("app.api.v1.endpoints.tax.reporting.TaxReportExporter")
    def test_get_export_status(self, mock_exporter, auth_headers):
        """Test getting the status of an export."""
        # Setup mock
        mock_instance = mock_exporter.return_value
        mock_instance.get_export_status.return_value = {
            "id": "export_123",
            "status": "completed",
            "filename": "tax_report_2023.xlsx",
            "file_size": 1024,
            "download_url": "/exports/tax_report_2023.xlsx",
            "created_at": "2023-01-01T00:00:00",
            "started_at": "2023-01-01T00:00:01",
            "completed_at": "2023-01-01T00:00:10",
            "processing_time": 9.0
        }
        
        # Test get status
        task_id = "export_123"
        response = client.get(
            f"/api/v1/tax/reports/export/status/{task_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return export status
        assert data["id"] == task_id
        assert data["status"] == "completed"
        assert "download_url" in data
        
        # Should have called get_export_status with correct params
        mock_instance.get_export_status.assert_called_once_with(
            export_id=task_id,
            company_id=TEST_COMPANY_ID,
            user_id=TEST_USER_ID
        )
    
    @patch("app.api.v1.endpoints.tax.reporting.TaxReportExporter")
    def test_download_export(self, mock_exporter, auth_headers):
        """Test downloading an exported report."""
        # Setup mock
        mock_instance = mock_exporter.return_value
        mock_instance.get_export_file.return_value = {
            "id": "export_123",
            "filename": "tax_report_2023.xlsx",
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "file_size": 1024,
            "download_url": "/exports/tax_report_2023.xlsx",
            "status": "completed"
        }
        
        # Test download
        task_id = "export_123"
        response = client.get(
            f"/api/v1/tax/reports/export/download/{task_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return download info
        assert data["status"] == "success"
        assert "download_url" in data
        
        # Should have called get_export_file with correct params
        mock_instance.get_export_file.assert_called_once_with(
            export_id=task_id,
            company_id=TEST_COMPANY_ID,
            user_id=TEST_USER_ID
        )
    
    def test_get_export_formats(self, auth_headers):
        """Test getting supported export formats."""
        response = client.get(
            "/api/v1/tax/reports/formats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        formats = response.json()
        
        # Should return a list of supported formats
        assert isinstance(formats, list)
        assert len(formats) > 0
        
        # Each format should have required fields
        for fmt in formats:
            assert "format" in fmt
            assert "name" in fmt
            assert "description" in fmt
    
    def test_invalidate_cache_unauthorized(self, auth_headers):
        """Test cache invalidation without superuser privileges."""
        # Regular users should not be able to invalidate cache
        response = client.post(
            "/api/v1/tax/reports/cache/invalidate",
            params={"tags": ["test_tag"]},
            headers=auth_headers
        )
        
        assert response.status_code == 403  # Forbidden
    
    @patch("app.core.tax.report_cache.report_cache")
    def test_invalidate_cache_authorized(self, mock_cache, auth_headers):
        """Test cache invalidation with superuser privileges."""
        # Setup mock
        mock_cache.invalidate_by_tags.return_value = 2
        
        # Create a superuser token
        superuser_token = create_access_token(
            data={
                "sub": "superuser_123",
                "company_id": TEST_COMPANY_ID,
                "is_superuser": True
            }
        )
        
        # Test with superuser token
        response = client.post(
            "/api/v1/tax/reports/cache/invalidate",
            params={"tags": ["test_tag1", "test_tag2"]},
            headers={
                "Authorization": f"Bearer {superuser_token}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return success and count of invalidated entries
        assert data["status"] == "success"
        assert data["message"] == "Invalidated 2 cache entries"
        assert "test_tag1" in data["tags"]
        assert "test_tag2" in data["tags"]
        
        # Should have called invalidate_by_tags with correct params
        mock_cache.invalidate_by_tags.assert_called_once_with(["test_tag1", "test_tag2"])
    
    def test_unauthorized_access(self):
        """Test accessing endpoints without authentication."""
        # Test without token
        response = client.get("/api/v1/tax/reports/liability")
        assert response.status_code == 401  # Unauthorized
        
        # Test with invalid token
        response = client.get(
            "/api/v1/tax/reports/liability",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401  # Unauthorized
