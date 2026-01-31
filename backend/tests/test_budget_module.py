"""
Tests for Budget Management module endpoints.
"""
import pytest
from tests.conftest import assert_success_response, assert_paginated_response, assert_error_response, TEST_COMPANY_ID

class TestBudgetEndpoints:
    """Test class for Budget Management endpoints"""
    
    def test_get_budgets_paginated(self, client, test_db):
        """Test budgets list with pagination"""
        response = client.get("/budgets/?page=1&page_size=10")
        data = assert_paginated_response(response)
        
        assert isinstance(data["data"], list)
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 10
    
    def test_create_budget(self, client, test_db):
        """Test budget creation"""
        budget_data = {
            "name": "Test Budget 2024",
            "fiscal_year": 2024,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "total_amount": 100000.00,
            "status": "draft",
            "company_id": TEST_COMPANY_ID
        }
        
        response = client.post("/budgets/", json=budget_data)
        data = assert_success_response(response)
        
        assert "data" in data
        budget = data["data"]
        assert budget["name"] == budget_data["name"]
        assert budget["fiscal_year"] == budget_data["fiscal_year"]
        assert "id" in budget
    
    def test_get_budget_by_id(self, client, test_db):
        """Test getting specific budget by ID"""
        # First create a budget
        budget_data = {
            "name": "Test Budget",
            "fiscal_year": 2024,
            "total_amount": 50000.00,
            "company_id": TEST_COMPANY_ID
        }
        
        create_response = client.post("/budgets/", json=budget_data)
        create_data = assert_success_response(create_response)
        budget_id = create_data["data"]["id"]
        
        # Then get it by ID
        response = client.get(f"/budgets/{budget_id}")
        data = assert_success_response(response)
        
        assert "data" in data
        budget = data["data"]
        assert budget["id"] == budget_id
        assert budget["name"] == budget_data["name"]
    
    def test_update_budget(self, client, test_db):
        """Test budget update"""
        # First create a budget
        budget_data = {
            "name": "Original Budget",
            "fiscal_year": 2024,
            "total_amount": 75000.00,
            "company_id": TEST_COMPANY_ID
        }
        
        create_response = client.post("/budgets/", json=budget_data)
        create_data = assert_success_response(create_response)
        budget_id = create_data["data"]["id"]
        
        # Then update it
        update_data = {
            "name": "Updated Budget",
            "total_amount": 85000.00
        }
        
        response = client.put(f"/budgets/{budget_id}", json=update_data)
        data = assert_success_response(response)
        
        assert "data" in data
        budget = data["data"]
        assert budget["name"] == update_data["name"]
        assert budget["total_amount"] == update_data["total_amount"]
    
    def test_delete_budget(self, client, test_db):
        """Test budget deletion"""
        # First create a budget
        budget_data = {
            "name": "Budget to Delete",
            "fiscal_year": 2024,
            "total_amount": 25000.00,
            "company_id": TEST_COMPANY_ID
        }
        
        create_response = client.post("/budgets/", json=budget_data)
        create_data = assert_success_response(create_response)
        budget_id = create_data["data"]["id"]
        
        # Then delete it
        response = client.delete(f"/budgets/{budget_id}")
        data = assert_success_response(response)
        
        assert data["message"] == "Budget deleted successfully"
    
    def test_get_budgets_by_fiscal_year(self, client, test_db):
        """Test getting budgets by fiscal year"""
        fiscal_year = 2024
        response = client.get(f"/budgets/fiscal-year/{fiscal_year}?page=1&page_size=20")
        data = assert_paginated_response(response)
        
        assert isinstance(data["data"], list)
        # All returned budgets should be for the specified fiscal year
        for budget in data["data"]:
            assert budget["fiscal_year"] == fiscal_year
    
    def test_approve_budget(self, client, test_db):
        """Test budget approval"""
        # First create a budget
        budget_data = {
            "name": "Budget for Approval",
            "fiscal_year": 2024,
            "total_amount": 60000.00,
            "company_id": TEST_COMPANY_ID
        }
        
        create_response = client.post("/budgets/", json=budget_data)
        create_data = assert_success_response(create_response)
        budget_id = create_data["data"]["id"]
        
        # Then approve it
        approval_data = {
            "approver_id": 1,
            "status": "approved",
            "comments": "Budget approved for 2024"
        }
        
        response = client.post(f"/budgets/{budget_id}/approve", json=approval_data)
        data = assert_success_response(response)
        
        assert "data" in data
        approval = data["data"]
        assert approval["status"] == approval_data["status"]
        assert approval["comments"] == approval_data["comments"]

class TestBudgetValidation:
    """Test validation and error handling for Budget endpoints"""
    
    def test_get_nonexistent_budget(self, client, test_db):
        """Test getting a budget that doesn't exist"""
        response = client.get("/budgets/99999")
        assert_error_response(response, 404)
    
    def test_create_budget_invalid_data(self, client, test_db):
        """Test budget creation with invalid data"""
        invalid_data = {
            "name": "",  # Empty name
            "fiscal_year": "invalid",  # Invalid year
            "total_amount": -1000.00  # Negative amount
        }
        
        response = client.post("/budgets/", json=invalid_data)
        # Should handle validation gracefully
        assert response.status_code in [400, 422]
    
    def test_update_nonexistent_budget(self, client, test_db):
        """Test updating a budget that doesn't exist"""
        update_data = {
            "name": "Updated Budget"
        }
        
        response = client.put("/budgets/99999", json=update_data)
        assert_error_response(response, 404)
    
    def test_delete_nonexistent_budget(self, client, test_db):
        """Test deleting a budget that doesn't exist"""
        response = client.delete("/budgets/99999")
        assert_error_response(response, 404)
    
    def test_approve_nonexistent_budget(self, client, test_db):
        """Test approving a budget that doesn't exist"""
        approval_data = {
            "approver_id": 1,
            "status": "approved"
        }
        
        response = client.post("/budgets/99999/approve", json=approval_data)
        assert_error_response(response, 404)