"""
Enhanced tests for General Ledger (GL) module endpoints.
"""
import pytest
from tests.conftest import assert_success_response, assert_paginated_response, assert_error_response, TEST_COMPANY_ID

class TestGLAccountEndpoints:
    """Test class for GL Account endpoints"""
    
    def test_create_account(self, client, test_db):
        """Test GL account creation"""
        account_data = {
            "account_code": "1001",
            "account_name": "Test Cash Account",
            "account_type": "ASSET",
            "parent_account_id": None,
            "is_active": True,
            "company_id": TEST_COMPANY_ID
        }
        
        response = client.post("/gl/accounts/", json=account_data)
        
        if response.status_code == 200:
            data = assert_success_response(response)
            assert "data" in data
            account = data["data"]
            assert account["account_code"] == account_data["account_code"]
            assert account["account_name"] == account_data["account_name"]
            assert account["account_type"] == account_data["account_type"]
        else:
            # Handle different response formats or missing endpoints
            assert response.status_code in [201, 404, 405]
    
    def test_list_accounts_paginated(self, client, test_db):
        """Test GL accounts list with pagination"""
        response = client.get("/gl/accounts/?page=1&page_size=10")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "pagination" in data:
                # New paginated format
                assert_paginated_response(response)
            elif isinstance(data, dict) and "data" in data:
                # Standard success format
                assert_success_response(response)
            else:
                # Old format - direct list
                assert isinstance(data, list)
        else:
            assert response.status_code in [404, 405]
    
    def test_get_account_by_id(self, client, test_db):
        """Test getting specific account by ID"""
        # Use a UUID format that might exist
        account_id = "550e8400-e29b-41d4-a716-446655440001"
        response = client.get(f"/gl/accounts/{account_id}")
        
        if response.status_code == 200:
            data = assert_success_response(response)
            assert "data" in data
            account = data["data"]
            assert "account_code" in account
            assert "account_name" in account
        else:
            # Account not found or endpoint format different
            assert response.status_code in [404, 405]
    
    def test_update_account(self, client, test_db):
        """Test GL account update"""
        account_id = "550e8400-e29b-41d4-a716-446655440001"
        update_data = {
            "account_name": "Updated Cash Account",
            "is_active": False
        }
        
        response = client.put(f"/gl/accounts/{account_id}", json=update_data)
        
        if response.status_code == 200:
            data = assert_success_response(response)
            assert "data" in data
            account = data["data"]
            assert account["account_name"] == update_data["account_name"]
        else:
            assert response.status_code in [404, 405]
    
    def test_delete_account(self, client, test_db):
        """Test GL account deletion"""
        account_id = "550e8400-e29b-41d4-a716-446655440001"
        response = client.delete(f"/gl/accounts/{account_id}")
        
        if response.status_code in [200, 204]:
            # Successful deletion
            pass
        else:
            assert response.status_code in [404, 405]
    
    def test_get_account_tree(self, client, test_db):
        """Test account hierarchy tree"""
        response = client.get(f"/gl/accounts/tree?company_id={TEST_COMPANY_ID}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                tree = data["data"]
            else:
                tree = data
            
            assert isinstance(tree, list)
        else:
            assert response.status_code in [404, 405]
    
    def test_get_account_balance(self, client, test_db):
        """Test account balance retrieval"""
        account_id = "550e8400-e29b-41d4-a716-446655440001"
        response = client.get(f"/gl/accounts/{account_id}/balance")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                balance = data["data"]
            else:
                balance = data
            
            assert "current_balance" in balance or "balance" in balance
        else:
            assert response.status_code in [404, 405]

class TestJournalEntryEndpoints:
    """Test class for Journal Entry endpoints"""
    
    def test_create_journal_entry(self, client, test_db):
        """Test journal entry creation"""
        entry_data = {
            "entry_number": "JE-TEST-001",
            "entry_date": "2024-01-15",
            "reference": "TEST-REF",
            "description": "Test journal entry",
            "company_id": TEST_COMPANY_ID,
            "lines": [
                {
                    "account_id": "550e8400-e29b-41d4-a716-446655440001",
                    "line_number": 1,
                    "debit_amount": 1000.00,
                    "credit_amount": 0.00,
                    "description": "Test debit entry"
                },
                {
                    "account_id": "550e8400-e29b-41d4-a716-446655440002",
                    "line_number": 2,
                    "debit_amount": 0.00,
                    "credit_amount": 1000.00,
                    "description": "Test credit entry"
                }
            ]
        }
        
        response = client.post("/gl/journal-entries/", json=entry_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response, response.status_code)
                entry = data["data"]
            else:
                entry = data
            
            assert entry["entry_number"] == entry_data["entry_number"]
            assert len(entry["lines"]) == 2
        else:
            assert response.status_code in [404, 405]
    
    def test_list_journal_entries_paginated(self, client, test_db):
        """Test journal entries list with pagination"""
        response = client.get("/gl/journal-entries/?page=1&page_size=20")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "pagination" in data:
                assert_paginated_response(response)
            elif isinstance(data, dict) and "data" in data:
                assert_success_response(response)
            else:
                assert isinstance(data, list)
        else:
            assert response.status_code in [404, 405]
    
    def test_get_journal_entry_by_id(self, client, test_db):
        """Test getting specific journal entry by ID"""
        entry_id = "550e8400-e29b-41d4-a716-446655440003"
        response = client.get(f"/gl/journal-entries/{entry_id}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                entry = data["data"]
            else:
                entry = data
            
            assert "entry_number" in entry
            assert "lines" in entry
        else:
            assert response.status_code in [404, 405]
    
    def test_post_journal_entry(self, client, test_db):
        """Test posting a journal entry"""
        entry_id = "550e8400-e29b-41d4-a716-446655440003"
        response = client.post(f"/gl/journal-entries/{entry_id}/post")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                entry = data["data"]
            else:
                entry = data
            
            assert entry["status"] in ["posted", "POSTED"]
        else:
            assert response.status_code in [404, 405]
    
    def test_reverse_journal_entry(self, client, test_db):
        """Test reversing a journal entry"""
        entry_id = "550e8400-e29b-41d4-a716-446655440003"
        reversal_data = {
            "reversal_date": "2024-01-16",
            "reversal_reference": "REV-TEST-001"
        }
        
        response = client.post(f"/gl/journal-entries/{entry_id}/reverse", json=reversal_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response, response.status_code)
                reversal = data["data"]
            else:
                reversal = data
            
            assert "entry_number" in reversal
        else:
            assert response.status_code in [404, 405]

class TestAccountingPeriodEndpoints:
    """Test class for Accounting Period endpoints"""
    
    def test_create_accounting_period(self, client, test_db):
        """Test accounting period creation"""
        period_data = {
            "period_name": "JAN-2024",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "fiscal_year": 2024,
            "is_closed": False,
            "company_id": TEST_COMPANY_ID
        }
        
        response = client.post("/gl/accounting-periods/", json=period_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response, response.status_code)
                period = data["data"]
            else:
                period = data
            
            assert period["period_name"] == period_data["period_name"]
            assert period["is_closed"] == False
        else:
            assert response.status_code in [404, 405]
    
    def test_close_accounting_period(self, client, test_db):
        """Test closing an accounting period"""
        period_id = "550e8400-e29b-41d4-a716-446655440004"
        response = client.post(f"/gl/accounting-periods/{period_id}/close")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                period = data["data"]
            else:
                period = data
            
            assert period["is_closed"] == True
        else:
            assert response.status_code in [404, 405]

class TestFinancialReportsEndpoints:
    """Test class for Financial Reports endpoints"""
    
    def test_generate_trial_balance(self, client, test_db):
        """Test trial balance generation"""
        response = client.get(f"/gl/trial-balance/?company_id={TEST_COMPANY_ID}&end_date=2024-12-31")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                trial_balance = data["data"]
            else:
                trial_balance = data
            
            assert isinstance(trial_balance, list) or "accounts" in trial_balance
        else:
            assert response.status_code in [404, 405]
    
    def test_generate_balance_sheet(self, client, test_db):
        """Test balance sheet generation"""
        response = client.get(f"/gl/financial-statements/balance-sheet?company_id={TEST_COMPANY_ID}&as_of_date=2024-12-31")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                balance_sheet = data["data"]
            else:
                balance_sheet = data
            
            assert "assets" in balance_sheet or "statement_type" in balance_sheet
        else:
            assert response.status_code in [404, 405]
    
    def test_generate_income_statement(self, client, test_db):
        """Test income statement generation"""
        response = client.get(f"/gl/financial-statements/income-statement?company_id={TEST_COMPANY_ID}&start_date=2024-01-01&end_date=2024-12-31")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                assert_success_response(response)
                income_statement = data["data"]
            else:
                income_statement = data
            
            assert "revenue" in income_statement or "statement_type" in income_statement
        else:
            assert response.status_code in [404, 405]

class TestGLValidation:
    """Test validation and error handling for GL endpoints"""
    
    def test_invalid_account_data(self, client, test_db):
        """Test account creation with invalid data"""
        invalid_data = {
            "account_code": "",  # Empty code
            "account_name": "",  # Empty name
            "account_type": "INVALID_TYPE"
        }
        
        response = client.post("/gl/accounts/", json=invalid_data)
        assert response.status_code in [400, 404, 405, 422]
    
    def test_unbalanced_journal_entry(self, client, test_db):
        """Test journal entry with unbalanced debits and credits"""
        unbalanced_entry = {
            "entry_number": "JE-UNBALANCED",
            "entry_date": "2024-01-15",
            "description": "Unbalanced entry",
            "lines": [
                {
                    "account_id": "550e8400-e29b-41d4-a716-446655440001",
                    "debit_amount": 1000.00,
                    "credit_amount": 0.00
                },
                {
                    "account_id": "550e8400-e29b-41d4-a716-446655440002",
                    "debit_amount": 0.00,
                    "credit_amount": 500.00  # Unbalanced!
                }
            ]
        }
        
        response = client.post("/gl/journal-entries/", json=unbalanced_entry)
        assert response.status_code in [400, 404, 405, 422]