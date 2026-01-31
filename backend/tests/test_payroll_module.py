"""
Tests for Payroll module endpoints.
"""
import pytest
from tests.conftest import assert_success_response, assert_paginated_response, TEST_COMPANY_ID

class TestPayrollEndpoints:
    """Test class for Payroll endpoints"""
    
    def test_get_payroll_kpis(self, client, test_db):
        """Test payroll dashboard KPIs endpoint"""
        response = client.get("/payroll/dashboard/kpis")
        data = assert_success_response(response)
        
        assert "data" in data
        kpis = data["data"]
        assert "total_payroll" in kpis
        assert "payroll_change" in kpis
        assert "total_employees" in kpis
        assert "employee_change" in kpis
        assert "average_salary" in kpis
        assert "upcoming_payroll" in kpis
    
    def test_get_payroll_summary(self, client, test_db):
        """Test payroll summary for dashboard"""
        response = client.get("/payroll/dashboard/summary?months=6")
        data = assert_success_response(response)
        
        assert "data" in data
        summary = data["data"]
        assert "monthly_data" in summary
        assert "total_budget" in summary
        assert "total_actual" in summary
        assert isinstance(summary["monthly_data"], list)
    
    def test_get_recent_activity(self, client, test_db):
        """Test recent payroll activity"""
        response = client.get("/payroll/dashboard/activity?limit=5")
        data = assert_success_response(response)
        
        assert "data" in data
        activities = data["data"]
        assert isinstance(activities, list)
        assert len(activities) <= 5
        
        if activities:
            activity = activities[0]
            assert "id" in activity
            assert "type" in activity
            assert "title" in activity
            assert "timestamp" in activity
    
    def test_get_employees_paginated(self, client, test_db):
        """Test employees list with pagination and filters"""
        response = client.get("/payroll/employees?page=1&page_size=10")
        data = assert_paginated_response(response)
        
        assert isinstance(data["data"], list)
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 10
        
        # Test with filters
        response = client.get("/payroll/employees?page=1&page_size=10&department=Engineering")
        data = assert_paginated_response(response)
        
        # All returned employees should be from Engineering department
        for employee in data["data"]:
            assert employee["department"] == "Engineering"
    
    def test_get_employee_by_id(self, client, test_db):
        """Test getting specific employee by ID"""
        employee_id = 1
        response = client.get(f"/payroll/employees/{employee_id}")
        data = assert_success_response(response)
        
        assert "data" in data
        employee = data["data"]
        assert employee["id"] == employee_id
        assert "employee_number" in employee
        assert "full_name" in employee
        assert "department" in employee
    
    def test_create_employee(self, client, test_db):
        """Test employee creation"""
        employee_data = {
            "employee_number": "EMP999",
            "first_name": "Test",
            "last_name": "Employee",
            "email": "test.employee@company.com",
            "department": "IT",
            "position": "Software Developer",
            "hire_date": "2024-01-15",
            "employment_type": "full_time",
            "salary_type": "salary",
            "base_salary": 70000.00,
            "pay_frequency": "bi_weekly"
        }
        
        response = client.post("/payroll/employees", json=employee_data)
        data = assert_success_response(response)
        
        assert "data" in data
        employee = data["data"]
        assert employee["first_name"] == employee_data["first_name"]
        assert employee["last_name"] == employee_data["last_name"]
        assert employee["full_name"] == f"{employee_data['first_name']} {employee_data['last_name']}"
        assert "id" in employee
    
    def test_update_employee(self, client, test_db):
        """Test employee update"""
        employee_id = 1
        update_data = {
            "position": "Senior Software Developer",
            "base_salary": 85000.00,
            "department": "Engineering"
        }
        
        response = client.put(f"/payroll/employees/{employee_id}", json=update_data)
        data = assert_success_response(response)
        
        assert "data" in data
        employee = data["data"]
        assert employee["position"] == update_data["position"]
        assert employee["base_salary"] == update_data["base_salary"]
        assert employee["department"] == update_data["department"]
    
    def test_delete_employee(self, client, test_db):
        """Test employee deletion"""
        employee_id = 3  # Use an existing employee ID
        response = client.delete(f"/payroll/employees/{employee_id}")
        data = assert_success_response(response)
        
        assert data["message"] == "Employee deleted successfully"
    
    def test_get_pay_runs(self, client, test_db):
        """Test pay runs list"""
        response = client.get("/payroll/pay-runs?page=1&page_size=10")
        # Note: This endpoint might not use paginated_response format yet
        assert response.status_code == 200
        data = response.json()
        
        assert "pay_runs" in data or "data" in data
        assert "total" in data or "pagination" in data
    
    def test_create_pay_run(self, client, test_db):
        """Test pay run creation"""
        pay_run_data = {
            "pay_period_start": "2024-01-01",
            "pay_period_end": "2024-01-15",
            "pay_date": "2024-01-20",
            "description": "Bi-weekly payroll"
        }
        
        response = client.post("/payroll/pay-runs", json=pay_run_data)
        data = assert_success_response(response)
        
        assert "data" in data
        pay_run = data["data"]
        assert pay_run["pay_period_start"] == pay_run_data["pay_period_start"]
        assert pay_run["status"] == "draft"
        assert "id" in pay_run
    
    def test_process_pay_run(self, client, test_db):
        """Test pay run processing"""
        pay_run_id = 1
        response = client.post(f"/payroll/pay-runs/{pay_run_id}/process")
        data = assert_success_response(response)
        
        assert "data" in data
        pay_run = data["data"]
        assert pay_run["status"] == "processing"
        assert "total_gross_pay" in pay_run
        assert "employee_count" in pay_run
    
    def test_get_payslips(self, client, test_db):
        """Test payslips list"""
        response = client.get("/payroll/payslips?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        
        assert "payslips" in data or "data" in data
    
    def test_get_deductions_benefits(self, client, test_db):
        """Test deductions and benefits list"""
        response = client.get("/payroll/deductions-benefits")
        data = assert_success_response(response)
        
        assert "data" in data
        items = data["data"]
        assert isinstance(items, list)
        
        if items:
            item = items[0]
            assert "id" in item
            assert "name" in item
            assert "type" in item
            assert "category" in item
    
    def test_create_deduction_benefit(self, client, test_db):
        """Test deduction/benefit creation"""
        item_data = {
            "name": "Test Benefit",
            "type": "benefit",
            "category": "health",
            "calculation_type": "fixed",
            "amount": 100.00,
            "is_pre_tax": True
        }
        
        response = client.post("/payroll/deductions-benefits", json=item_data)
        data = assert_success_response(response)
        
        assert "data" in data
        item = data["data"]
        assert item["name"] == item_data["name"]
        assert item["type"] == item_data["type"]
        assert "id" in item
    
    def test_get_payroll_analytics(self, client, test_db):
        """Test payroll analytics"""
        response = client.get("/payroll/analytics?start_date=2024-01-01&end_date=2024-12-31")
        data = assert_success_response(response)
        
        assert "data" in data
        analytics = data["data"]
        assert "total_payroll" in analytics
        assert "average_salary" in analytics
        assert "by_period" in analytics
        assert "by_department" in analytics

class TestPayrollValidation:
    """Test validation and error handling for Payroll endpoints"""
    
    def test_get_nonexistent_employee(self, client, test_db):
        """Test getting an employee that doesn't exist"""
        response = client.get("/payroll/employees/99999")
        assert response.status_code == 404
    
    def test_create_employee_invalid_data(self, client, test_db):
        """Test employee creation with invalid data"""
        invalid_data = {
            "first_name": "",  # Empty name
            "email": "invalid-email",  # Invalid email
            "base_salary": -1000  # Negative salary
        }
        
        response = client.post("/payroll/employees", json=invalid_data)
        assert response.status_code in [400, 422]
    
    def test_invalid_pay_run_dates(self, client, test_db):
        """Test pay run creation with invalid dates"""
        invalid_data = {
            "pay_period_start": "2024-01-15",
            "pay_period_end": "2024-01-01",  # End before start
            "pay_date": "2023-12-31"  # Pay date before period
        }
        
        response = client.post("/payroll/pay-runs", json=invalid_data)
        assert response.status_code in [400, 422]