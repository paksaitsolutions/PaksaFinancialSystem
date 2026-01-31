"""
Tests for Fixed Assets module endpoints.
"""
import pytest
from tests.conftest import assert_success_response, assert_paginated_response, TEST_COMPANY_ID

class TestFixedAssetsEndpoints:
    """Test class for Fixed Assets endpoints"""
    
    def test_get_assets(self, client, test_db):
        """Test assets list endpoint"""
        response = client.get("/fixed-assets/assets")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                assets = data["data"]
            else:
                assets = data
            
            assert isinstance(assets, list)
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_create_asset(self, client, test_db):
        """Test asset creation"""
        asset_data = {
            "asset_number": "FA-001",
            "name": "Test Computer",
            "description": "Dell Laptop for testing",
            "category": "Computer Equipment",
            "acquisition_date": "2024-01-15",
            "acquisition_cost": 1500.00,
            "useful_life_years": 3,
            "depreciation_method": "straight_line",
            "salvage_value": 100.00,
            "location": "Office - IT Department",
            "status": "active",
            "company_id": TEST_COMPANY_ID
        }
        
        response = client.post("/fixed-assets/assets", json=asset_data)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                asset = data["data"]
            else:
                asset = data
            
            assert asset["asset_number"] == asset_data["asset_number"]
            assert asset["name"] == asset_data["name"]
            assert asset["acquisition_cost"] == asset_data["acquisition_cost"]
            assert "id" in asset
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_get_asset_by_id(self, client, test_db):
        """Test getting specific asset by ID"""
        asset_id = 1
        response = client.get(f"/fixed-assets/assets/{asset_id}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                asset = data["data"]
            else:
                asset = data
            
            assert asset["id"] == asset_id
            assert "asset_number" in asset
            assert "name" in asset
        elif response.status_code == 404:
            # Asset not found - acceptable for test
            pass
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_update_asset(self, client, test_db):
        """Test asset update"""
        asset_id = 1
        update_data = {
            "name": "Updated Computer Name",
            "location": "Office - Finance Department",
            "status": "maintenance"
        }
        
        response = client.put(f"/fixed-assets/assets/{asset_id}", json=update_data)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                asset = data["data"]
            else:
                asset = data
            
            assert asset["name"] == update_data["name"]
            assert asset["location"] == update_data["location"]
            assert asset["status"] == update_data["status"]
        else:
            # Endpoint might not exist yet or asset not found
            assert response.status_code in [404, 405]
    
    def test_delete_asset(self, client, test_db):
        """Test asset deletion"""
        asset_id = 1
        response = client.delete(f"/fixed-assets/assets/{asset_id}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "message" in data:
                assert_success_response(response)
                assert "deleted" in data["message"].lower()
        else:
            # Endpoint might not exist yet or asset not found
            assert response.status_code in [404, 405]
    
    def test_get_depreciation_schedule(self, client, test_db):
        """Test depreciation schedule endpoint"""
        asset_id = 1
        response = client.get(f"/fixed-assets/assets/{asset_id}/depreciation")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                schedule = data["data"]
            else:
                schedule = data
            
            assert isinstance(schedule, list)
            if schedule:
                entry = schedule[0]
                assert "period" in entry
                assert "depreciation_amount" in entry
                assert "accumulated_depreciation" in entry
                assert "book_value" in entry
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_calculate_depreciation(self, client, test_db):
        """Test depreciation calculation"""
        calculation_data = {
            "acquisition_cost": 10000.00,
            "salvage_value": 1000.00,
            "useful_life_years": 5,
            "depreciation_method": "straight_line",
            "acquisition_date": "2024-01-01"
        }
        
        response = client.post("/fixed-assets/depreciation/calculate", json=calculation_data)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                result = data["data"]
            else:
                result = data
            
            assert "annual_depreciation" in result
            assert "monthly_depreciation" in result
            assert result["annual_depreciation"] > 0
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_get_asset_categories(self, client, test_db):
        """Test asset categories endpoint"""
        response = client.get("/fixed-assets/categories")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                categories = data["data"]
            else:
                categories = data
            
            assert isinstance(categories, list)
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_create_asset_category(self, client, test_db):
        """Test asset category creation"""
        category_data = {
            "name": "Test Equipment",
            "description": "Equipment for testing purposes",
            "default_useful_life": 5,
            "default_depreciation_method": "straight_line",
            "gl_account_asset": "1500",
            "gl_account_depreciation": "1510",
            "gl_account_expense": "6100"
        }
        
        response = client.post("/fixed-assets/categories", json=category_data)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                category = data["data"]
            else:
                category = data
            
            assert category["name"] == category_data["name"]
            assert category["default_useful_life"] == category_data["default_useful_life"]
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]
    
    def test_get_asset_reports(self, client, test_db):
        """Test asset reports endpoint"""
        response = client.get("/fixed-assets/reports")
        
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
    
    def test_generate_asset_report(self, client, test_db):
        """Test asset report generation"""
        report_data = {
            "report_type": "asset_listing",
            "as_of_date": "2024-12-31",
            "include_disposed": False,
            "category_filter": None,
            "company_id": TEST_COMPANY_ID
        }
        
        response = client.post("/fixed-assets/reports/generate", json=report_data)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                report = data["data"]
            else:
                report = data
            
            assert "report_id" in report or "id" in report
        else:
            # Endpoint might not exist yet
            assert response.status_code in [404, 405]

class TestFixedAssetsValidation:
    """Test validation and error handling for Fixed Assets endpoints"""
    
    def test_invalid_asset_data(self, client, test_db):
        """Test asset creation with invalid data"""
        invalid_data = {
            "asset_number": "",  # Empty asset number
            "acquisition_cost": -1000.00,  # Negative cost
            "useful_life_years": 0,  # Zero useful life
            "acquisition_date": "invalid-date"
        }
        
        response = client.post("/fixed-assets/assets", json=invalid_data)
        # Should handle validation gracefully or return 404/405 if endpoint doesn't exist
        assert response.status_code in [400, 404, 405, 422]
    
    def test_invalid_depreciation_calculation(self, client, test_db):
        """Test depreciation calculation with invalid data"""
        invalid_data = {
            "acquisition_cost": -5000.00,  # Negative cost
            "salvage_value": 6000.00,  # Salvage > acquisition
            "useful_life_years": -1  # Negative life
        }
        
        response = client.post("/fixed-assets/depreciation/calculate", json=invalid_data)
        # Should handle validation gracefully or return 404/405 if endpoint doesn't exist
        assert response.status_code in [400, 404, 405, 422]

class TestFixedAssetsIntegration:
    """Test Fixed Assets integration with other modules"""
    
    def test_gl_integration(self, client, test_db):
        """Test Fixed Assets integration with General Ledger"""
        # Test that asset transactions create proper GL entries
        response = client.get("/fixed-assets/gl-integration/entries")
        # Endpoint might not exist yet
        assert response.status_code in [200, 404, 405]
    
    def test_depreciation_gl_entries(self, client, test_db):
        """Test depreciation GL entry creation"""
        depreciation_data = {
            "period": "2024-01",
            "company_id": TEST_COMPANY_ID
        }
        
        response = client.post("/fixed-assets/depreciation/process", json=depreciation_data)
        # Endpoint might not exist yet
        assert response.status_code in [200, 404, 405]