"""
Tests for Accounts Receivable (AR) module endpoints.
"""
import pytest
from tests.conftest import assert_success_response, assert_paginated_response, TEST_COMPANY_ID

class TestAREndpoints:
    """Test class for AR endpoints"""
    
    def test_get_ar_analytics(self, client, test_db):
        """Test AR analytics dashboard endpoint"""
        response = client.get("/ar/analytics/dashboard")
        data = assert_success_response(response)
        
        assert "data" in data
        analytics = data["data"]
        assert "kpis" in analytics
        kpis = analytics["kpis"]
        assert "total_outstanding" in kpis
        assert "overdue_amount" in kpis
        assert "current_month_collections" in kpis
        assert "active_customers" in kpis
    
    def test_get_customers_paginated(self, client, test_db):
        """Test customers list with pagination"""
        response = client.get("/ar/customers?page=1&page_size=10")
        data = assert_paginated_response(response)
        
        assert isinstance(data["data"], list)
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 10
    
    def test_create_customer(self, client, test_db):
        """Test customer creation"""
        customer_data = {
            "name": "Test Customer",
            "email": "test@customer.com",
            "phone": "+1-555-0123",
            "address": "123 Test St",
            "creditLimit": 10000,
            "paymentTerms": "Net 30"
        }
        
        response = client.post("/ar/customers", json=customer_data)
        data = assert_success_response(response)
        
        assert "data" in data
        customer = data["data"]
        assert customer["name"] == customer_data["name"]
        assert customer["email"] == customer_data["email"]
        assert "id" in customer
    
    def test_get_invoices_paginated(self, client, test_db):
        """Test invoices list with pagination"""
        response = client.get("/ar/invoices?page=1&page_size=20")
        data = assert_paginated_response(response)
        
        assert isinstance(data["data"], list)
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 20
    
    def test_create_invoice(self, client, test_db):
        """Test invoice creation"""
        invoice_data = {
            "customer_id": "cust_001",
            "invoice_date": "2024-01-15",
            "due_date": "2024-02-14",
            "total_amount": 1500.00,
            "items": [
                {"description": "Service", "amount": 1500.00}
            ]
        }
        
        response = client.post("/ar/invoices", json=invoice_data)
        data = assert_success_response(response)
        
        assert "data" in data
        invoice = data["data"]
        assert "invoice_number" in invoice
        assert invoice["status"] == "draft"
    
    def test_record_payment(self, client, test_db):
        """Test payment recording"""
        payment_data = {
            "invoice_id": "inv_001",
            "amount": 1500.00,
            "payment_method": "check",
            "reference": "CHK-001"
        }
        
        response = client.post("/ar/payments", json=payment_data)
        data = assert_success_response(response)
        
        assert "data" in data
        payment = data["data"]
        assert "id" in payment
        assert "payment_date" in payment
    
    def test_send_payment_reminders(self, client, test_db):
        """Test sending payment reminders"""
        reminder_data = {
            "invoice_ids": ["inv_001", "inv_002"]
        }
        
        response = client.post("/ar/invoices/send-reminders", json=reminder_data)
        data = assert_success_response(response)
        
        assert "data" in data
        result = data["data"]
        assert result["success"] == True
        assert result["reminders_sent"] == 2
    
    def test_get_aging_report(self, client, test_db):
        """Test aging report generation"""
        response = client.get("/ar/aging-report")
        data = assert_success_response(response)
        
        assert "data" in data
        report = data["data"]
        assert "as_of_date" in report
        assert "aging_buckets" in report
        assert "total_outstanding" in report
    
    def test_get_collection_forecast(self, client, test_db):
        """Test collection forecast"""
        response = client.get("/ar/collection-forecast")
        data = assert_success_response(response)
        
        assert "data" in data
        forecast = data["data"]
        assert "forecast_period" in forecast
        assert "predicted_collections" in forecast
        assert "confidence_score" in forecast
    
    def test_get_dashboard_stats(self, client, test_db):
        """Test AR dashboard stats"""
        response = client.get("/ar/dashboard/stats")
        data = assert_success_response(response)
        
        assert "data" in data
        stats = data["data"]
        assert "kpis" in stats
    
    def test_get_recent_invoices_dashboard(self, client, test_db):
        """Test recent invoices for dashboard"""
        response = client.get("/ar/dashboard/recent-invoices")
        data = assert_success_response(response)
        
        assert "data" in data
        assert isinstance(data["data"], list)

class TestARValidation:
    """Test validation and error handling for AR endpoints"""
    
    def test_invalid_customer_data(self, client, test_db):
        """Test customer creation with invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail
            "email": "invalid-email"  # Invalid email format
        }
        
        response = client.post("/ar/customers", json=invalid_data)
        # Should handle validation gracefully
        assert response.status_code in [400, 422]