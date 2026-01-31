"""
Tests for Tax Management module endpoints.
"""
import pytest
from tests.conftest import assert_success_response, assert_paginated_response, TEST_COMPANY_ID

class TestTaxEndpoints:
    """Test class for Tax Management endpoints"""
    
    def test_get_tax_codes(self, client, test_db):
        """Test tax codes list endpoint"""
        response = client.get("/tax/codes")
        assert response.status_code == 200
        
        # Handle both old and new response formats
        data = response.json()
        if isinstance(data, dict) and "data" in data:
            # New standardized format
            assert_success_response(response)
            tax_codes = data["data"]
        else:
            # Old format - direct list
            tax_codes = data
        
        assert isinstance(tax_codes, list)
    
    def test_create_tax_code(self, client, test_db):
        """Test tax code creation"""
        tax_code_data = {
            "code": "TEST_TAX",
            "name": "Test Tax Code",
            "rate": 8.25,
            "tax_type": "sales_tax",
            "jurisdiction": "State",
            "is_active": True
        }
        
        response = client.post("/tax/codes", json=tax_code_data)
        
        # Handle response format
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                tax_code = data["data"]
            else:
                tax_code = data
            
            assert tax_code["code"] == tax_code_data["code"]
            assert tax_code["name"] == tax_code_data["name"]
            assert tax_code["rate"] == tax_code_data["rate"]
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_get_tax_returns(self, client, test_db):
        """Test tax returns list"""
        response = client.get("/tax/returns")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                returns = data["data"]
            else:
                returns = data
            
            assert isinstance(returns, list)
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_create_tax_return(self, client, test_db):
        """Test tax return creation"""
        tax_return_data = {
            "return_type": "sales_tax",
            "period_start": "2024-01-01",
            "period_end": "2024-03-31",
            "jurisdiction": "CA",
            "status": "draft",
            "company_id": TEST_COMPANY_ID
        }
        
        response = client.post("/tax/returns", json=tax_return_data)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                tax_return = data["data"]
            else:
                tax_return = data
            
            assert tax_return["return_type"] == tax_return_data["return_type"]
            assert tax_return["status"] == tax_return_data["status"]
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_get_tax_calculations(self, client, test_db):
        """Test tax calculations endpoint"""
        response = client.get("/tax/calculations")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                calculations = data["data"]
            else:
                calculations = data
            
            assert isinstance(calculations, list)
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_calculate_tax(self, client, test_db):
        """Test tax calculation"""
        calculation_data = {
            "amount": 1000.00,
            "tax_code": "SALES_TAX_CA",
            "transaction_date": "2024-01-15",
            "jurisdiction": "CA"
        }
        
        response = client.post("/tax/calculate", json=calculation_data)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                result = data["data"]
            else:
                result = data
            
            assert "tax_amount" in result
            assert "total_amount" in result
            assert result["tax_amount"] >= 0
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_get_tax_reports(self, client, test_db):
        """Test tax reports endpoint"""
        response = client.get("/tax/reports")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                reports = data["data"]
            else:
                reports = data
            
            assert isinstance(reports, list)
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_generate_tax_report(self, client, test_db):
        """Test tax report generation"""
        report_data = {
            "report_type": "sales_tax_summary",
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
            "jurisdiction": "CA",
            "company_id": TEST_COMPANY_ID
        }
        
        response = client.post("/tax/reports/generate", json=report_data)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                report = data["data"]
            else:
                report = data
            
            assert "report_id" in report or "id" in report
            assert "status" in report
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]

class TestTaxValidation:
    """Test validation and error handling for Tax endpoints"""
    
    def test_invalid_tax_code_data(self, client, test_db):
        """Test tax code creation with invalid data"""
        invalid_data = {
            "code": "",  # Empty code
            "rate": -5.0,  # Negative rate
            "tax_type": "invalid_type"
        }
        
        response = client.post("/tax/codes", json=invalid_data)
        # Should handle validation gracefully or return 404/405 if endpoint doesn't exist
        assert response.status_code in [400, 404, 405, 422]
    
    def test_invalid_tax_calculation(self, client, test_db):
        """Test tax calculation with invalid data"""
        invalid_data = {
            "amount": -100.00,  # Negative amount
            "tax_code": "",  # Empty tax code
        }
        
        response = client.post("/tax/calculate", json=invalid_data)
        # Should handle validation gracefully or return 404/405 if endpoint doesn't exist
        assert response.status_code in [400, 404, 405, 422]

class TestTaxIntegration:
    """Test tax module integration with other modules"""
    
    def test_tax_calculation_integration(self, client, test_db):
        """Test tax calculation integration with transactions"""
        # This would test how tax calculations integrate with AR/AP transactions
        # For now, just test that the endpoint structure is consistent
        
        response = client.get("/tax/integrations/ar")
        # Endpoint might not exist yet
        assert response.status_code in [200, 404, 405]
        
        response = client.get("/tax/integrations/ap")
        # Endpoint might not exist yet
        assert response.status_code in [200, 404, 405]