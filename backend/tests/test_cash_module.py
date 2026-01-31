"""
Tests for Cash Management module endpoints.
"""
import pytest
from tests.conftest import assert_success_response, assert_paginated_response, TEST_COMPANY_ID

class TestCashManagementEndpoints:
    """Test class for Cash Management endpoints"""
    
    def test_get_cash_dashboard(self, client, test_db):
        """Test cash management dashboard endpoint"""
        response = client.get("/cash/dashboard")
        data = assert_success_response(response)
        
        assert "data" in data
        dashboard = data["data"]
        assert "total_balance" in dashboard
        assert "account_count" in dashboard
        assert "monthly_inflow" in dashboard
        assert "monthly_outflow" in dashboard
        assert "cash_flow_trend" in dashboard
        assert "liquidity_ratio" in dashboard
    
    def test_get_bank_accounts_paginated(self, client, test_db):
        """Test bank accounts list with pagination"""
        response = client.get("/cash/accounts?page=1&page_size=10")
        data = assert_paginated_response(response)
        
        assert isinstance(data["data"], list)
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 10
        
        # Check account structure
        if data["data"]:
            account = data["data"][0]
            assert "id" in account
            assert "name" in account
            assert "account_number" in account
            assert "bank_name" in account
            assert "current_balance" in account
    
    def test_create_bank_account(self, client, test_db):
        """Test bank account creation"""
        account_data = {
            "name": "Test Checking Account",
            "account_number": "1234567890",
            "bank_name": "Test Bank",
            "account_type": "checking",
            "currency": "USD"
        }
        
        response = client.post("/cash/accounts", json=account_data)
        data = assert_success_response(response)
        
        assert "data" in data
        account = data["data"]
        assert account["name"] == account_data["name"]
        assert account["current_balance"] == 0.00
        assert account["is_active"] == True
        assert "id" in account
    
    def test_get_transactions_paginated(self, client, test_db):
        """Test transactions list with pagination"""
        response = client.get("/cash/transactions?page=1&page_size=15")
        data = assert_paginated_response(response)
        
        assert isinstance(data["data"], list)
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 15
        
        # Check transaction structure
        if data["data"]:
            transaction = data["data"][0]
            assert "id" in transaction
            assert "account_id" in transaction
            assert "transaction_date" in transaction
            assert "transaction_type" in transaction
            assert "amount" in transaction
    
    def test_create_transaction(self, client, test_db):
        """Test transaction creation"""
        transaction_data = {
            "account_id": "acc_001",
            "transaction_type": "deposit",
            "amount": 1000.00,
            "memo": "Test deposit",
            "reference": "DEP-TEST-001"
        }
        
        response = client.post("/cash/transactions", json=transaction_data)
        data = assert_success_response(response)
        
        assert "data" in data
        transaction = data["data"]
        assert transaction["amount"] == transaction_data["amount"]
        assert transaction["transaction_type"] == transaction_data["transaction_type"]
        assert "id" in transaction
        assert "transaction_date" in transaction
    
    def test_get_cash_flow_forecast(self, client, test_db):
        """Test cash flow forecasting"""
        response = client.get("/cash/forecast?days=30")
        data = assert_success_response(response)
        
        assert "data" in data
        forecasts = data["data"]
        assert isinstance(forecasts, list)
        
        if forecasts:
            forecast = forecasts[0]
            assert "period" in forecast
            assert "projected_inflow" in forecast
            assert "projected_outflow" in forecast
            assert "net_cash_flow" in forecast
            assert "confidence_level" in forecast
    
    def test_reconcile_account(self, client, test_db):
        """Test bank account reconciliation"""
        reconciliation_data = {
            "transaction_count": 25,
            "statement_balance": 15000.00,
            "book_balance": 15000.00
        }
        
        response = client.post("/cash/accounts/acc_001/reconcile", json=reconciliation_data)
        data = assert_success_response(response)
        
        assert "data" in data
        result = data["data"]
        assert result["success"] == True
        assert "reconciled_transactions" in result
        assert "reconciliation_date" in result
    
    def test_get_liquidity_analysis(self, client, test_db):
        """Test liquidity analysis"""
        response = client.get("/cash/analytics/liquidity")
        data = assert_success_response(response)
        
        assert "data" in data
        analysis = data["data"]
        assert "current_ratio" in analysis
        assert "quick_ratio" in analysis
        assert "cash_ratio" in analysis
        assert "working_capital" in analysis
        assert "days_cash_on_hand" in analysis
    
    def test_get_cash_variance_analysis(self, client, test_db):
        """Test cash variance analysis"""
        response = client.get("/cash/analytics/variance")
        data = assert_success_response(response)
        
        assert "data" in data
        variance = data["data"]
        assert "period" in variance
        assert "budgeted_inflow" in variance
        assert "actual_inflow" in variance
        assert "inflow_variance" in variance
        assert "net_variance" in variance

class TestCashManagementValidation:
    """Test validation and error handling for Cash Management endpoints"""
    
    def test_invalid_account_data(self, client, test_db):
        """Test account creation with invalid data"""
        invalid_data = {
            "name": "",  # Empty name
            "account_type": "invalid_type"  # Invalid account type
        }
        
        response = client.post("/cash/accounts", json=invalid_data)
        # Should handle validation gracefully
        assert response.status_code in [400, 422]
    
    def test_invalid_transaction_data(self, client, test_db):
        """Test transaction creation with invalid data"""
        invalid_data = {
            "account_id": "",  # Empty account ID
            "amount": -100.00,  # Negative amount might be invalid
            "transaction_type": "invalid_type"
        }
        
        response = client.post("/cash/transactions", json=invalid_data)
        # Should handle validation gracefully
        assert response.status_code in [400, 422]