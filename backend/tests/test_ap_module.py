"""
Tests for Accounts Payable (AP) module endpoints.
"""
import pytest
from tests.conftest_simple import assert_success_response, assert_paginated_response, TEST_COMPANY_ID

class TestAPEndpoints:
    """Test class for AP endpoints"""
    
    def test_get_ap_dashboard_stats(self, client, test_db):
        """Test AP dashboard stats endpoint"""
        response = client.get("/api/v1/ap/dashboard/stats")
        data = assert_success_response(response)
        
        assert "data" in data
        stats = data["data"]
        assert "totalPayable" in stats
        assert "overdueBills" in stats
        assert "activeVendors" in stats
        assert "monthlyPayments" in stats
    
    def test_get_recent_bills(self, client, test_db):
        """Test recent bills endpoint"""
        response = client.get("/api/v1/ap/dashboard/recent-bills")
        data = assert_success_response(response)
        
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_get_vendors_paginated(self, client, test_db):
        """Test vendors list with pagination"""
        response = client.get("/api/v1/ap/vendors?page=1&page_size=10")
        data = assert_paginated_response(response)
        
        assert isinstance(data["data"], list)
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 10
    
    def test_get_payments_paginated(self, client, test_db):
        """Test payments list with pagination"""
        response = client.get("/api/v1/ap/payments?page=1&page_size=5")
        data = assert_paginated_response(response)
        
        assert isinstance(data["data"], list)
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 5
    
    def test_import_bills(self, client, test_db):
        """Test bills import endpoint"""
        response = client.post("/api/v1/ap/import-bills")
        data = assert_success_response(response)
        
        assert data["message"] == "Bills imported successfully"
    
    def test_batch_payments(self, client, test_db):
        """Test batch payments processing"""
        response = client.post("/api/v1/ap/batch-payments")
        data = assert_success_response(response)
        
        assert data["message"] == "Batch payments processed successfully"

class TestAPValidation:
    """Test validation and error handling for AP endpoints"""
    
    def test_invalid_pagination_params(self, client, test_db):
        """Test invalid pagination parameters"""
        # Test invalid page number
        response = client.get("/api/v1/ap/vendors?page=0")
        assert response.status_code == 422
        
        # Test invalid page size
        response = client.get("/api/v1/ap/vendors?page_size=101")
        assert response.status_code == 422