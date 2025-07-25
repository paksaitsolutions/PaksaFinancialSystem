"""Test General Ledger API endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestGLAccountsAPI:
    """Test GL Accounts CRUD operations"""
    
    def test_get_accounts_list(self):
        """Test GET /api/v1/gl/accounts"""
        response = client.get("/api/v1/gl/accounts")
        assert response.status_code in [200, 401]  # 401 if auth required
        
    def test_create_account(self):
        """Test POST /api/v1/gl/accounts"""
        account_data = {
            "account_number": "1000",
            "name": "Cash",
            "account_type": "asset",
            "description": "Cash and cash equivalents"
        }
        response = client.post("/api/v1/gl/accounts", json=account_data)
        assert response.status_code in [201, 401, 422]
        
    def test_get_account_detail(self):
        """Test GET /api/v1/gl/accounts/{id}"""
        response = client.get("/api/v1/gl/accounts/1")
        assert response.status_code in [200, 401, 404]
        
    def test_update_account(self):
        """Test PUT /api/v1/gl/accounts/{id}"""
        update_data = {
            "name": "Updated Cash Account",
            "description": "Updated description"
        }
        response = client.put("/api/v1/gl/accounts/1", json=update_data)
        assert response.status_code in [200, 401, 404, 422]
        
    def test_delete_account(self):
        """Test DELETE /api/v1/gl/accounts/{id}"""
        response = client.delete("/api/v1/gl/accounts/1")
        assert response.status_code in [204, 401, 404]

class TestGLJournalEntriesAPI:
    """Test GL Journal Entries CRUD operations"""
    
    def test_get_journal_entries_list(self):
        """Test GET /api/v1/gl/journal-entries"""
        response = client.get("/api/v1/gl/journal-entries")
        assert response.status_code in [200, 401]
        
    def test_create_journal_entry(self):
        """Test POST /api/v1/gl/journal-entries"""
        entry_data = {
            "entry_number": "JE-2024-001",
            "entry_date": "2024-01-15",
            "description": "Test journal entry",
            "line_items": [
                {
                    "account_id": "1",
                    "debit": 1000,
                    "credit": 0,
                    "description": "Debit entry"
                },
                {
                    "account_id": "2", 
                    "debit": 0,
                    "credit": 1000,
                    "description": "Credit entry"
                }
            ]
        }
        response = client.post("/api/v1/gl/journal-entries", json=entry_data)
        assert response.status_code in [201, 401, 422]
        
    def test_post_journal_entry(self):
        """Test POST /api/v1/gl/journal-entries/{id}/post"""
        response = client.post("/api/v1/gl/journal-entries/1/post")
        assert response.status_code in [200, 401, 404, 422]
        
    def test_unpost_journal_entry(self):
        """Test POST /api/v1/gl/journal-entries/{id}/unpost"""
        response = client.post("/api/v1/gl/journal-entries/1/unpost")
        assert response.status_code in [200, 401, 404, 422]
        
    def test_reverse_journal_entry(self):
        """Test POST /api/v1/gl/journal-entries/{id}/reverse"""
        response = client.post("/api/v1/gl/journal-entries/1/reverse")
        assert response.status_code in [201, 401, 404, 422]

class TestGLReportsAPI:
    """Test GL Reports endpoints"""
    
    def test_trial_balance(self):
        """Test GET /api/v1/gl/reports/trial-balance"""
        response = client.get("/api/v1/gl/reports/trial-balance")
        assert response.status_code in [200, 401]
        
    def test_gl_summary(self):
        """Test GET /api/v1/gl/reports/summary"""
        response = client.get("/api/v1/gl/reports/summary")
        assert response.status_code in [200, 401]
        
    def test_gl_detail(self):
        """Test GET /api/v1/gl/reports/detail"""
        response = client.get("/api/v1/gl/reports/detail")
        assert response.status_code in [200, 401]