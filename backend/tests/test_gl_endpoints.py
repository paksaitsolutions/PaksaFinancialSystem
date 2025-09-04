import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database_config import Base, get_db
from app.models.gl_models_updated import GLAccount, JournalEntry, AccountingPeriod

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_gl_database.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override the get_db dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

# Test data
TEST_ACCOUNT = {
    "account_code": "9999",
    "account_name": "Test Account",
    "account_type": "ASSET",
    "is_active": True
}

TEST_JOURNAL_ENTRY = {
    "entry_number": "TEST-001",
    "entry_date": "2023-10-15",
    "reference": "TEST-REF",
    "description": "Test journal entry",
    "lines": [
        {
            "account_id": 1,
            "line_number": 1,
            "debit_amount": 100.00,
            "credit_amount": 0.00,
            "description": "Test debit"
        },
        {
            "account_id": 2,
            "line_number": 2,
            "debit_amount": 0.00,
            "credit_amount": 100.00,
            "description": "Test credit"
        }
    ]
}

# Fixture to clear the database between tests
@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Test GL Account endpoints
def test_create_gl_account(test_db):
    """Test creating a GL account"""
    response = client.post("/gl/accounts/", json=TEST_ACCOUNT)
    assert response.status_code == 200
    data = response.json()
    assert data["account_code"] == TEST_ACCOUNT["account_code"]
    assert data["account_name"] == TEST_ACCOUNT["account_name"]
    assert data["id"] is not None

def test_list_gl_accounts(test_db):
    """Test listing GL accounts"""
    # First create a test account
    client.post("/gl/accounts/", json=TEST_ACCOUNT)
    
    # Then list accounts
    response = client.get("/gl/accounts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["account_code"] == TEST_ACCOUNT["account_code"]

# Test Journal Entry endpoints
def test_create_journal_entry(test_db):
    """Test creating a journal entry"""
    # First create required accounts
    client.post("/gl/accounts/", json={
        "account_code": "1111",
        "account_name": "Test Account 1",
        "account_type": "ASSET"
    })
    client.post("/gl/accounts/", json={
        "account_code": "2222",
        "account_name": "Test Account 2",
        "account_type": "LIABILITY"
    })
    
    # Then create journal entry
    response = client.post("/gl/journal-entries/", json=TEST_JOURNAL_ENTRY)
    assert response.status_code == 200
    data = response.json()
    assert data["entry_number"] == TEST_JOURNAL_ENTRY["entry_number"]
    assert len(data["lines"]) == 2

def test_list_journal_entries(test_db):
    """Test listing journal entries"""
    # First create a test entry
    test_create_journal_entry(test_db)
    
    # Then list entries
    response = client.get("/gl/journal-entries/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["entry_number"] == TEST_JOURNAL_ENTRY["entry_number"]

# Test Accounting Period endpoints
def test_create_accounting_period(test_db):
    """Test creating an accounting period"""
    period_data = {
        "period_name": "OCT-2023",
        "start_date": "2023-10-01",
        "end_date": "2023-10-31",
        "is_closed": False
    }
    
    response = client.post("/gl/accounting-periods/", json=period_data)
    assert response.status_code == 200
    data = response.json()
    assert data["period_name"] == period_data["period_name"]
    assert data["is_closed"] == period_data["is_closed"]

def test_trial_balance(test_db):
    """Test generating a trial balance"""
    # First create test data
    test_create_journal_entry(test_db)
    
    # Then get trial balance
    response = client.get("/gl/trial-balance/?as_of_date=2023-12-31")
    assert response.status_code == 200
    data = response.json()
    assert "accounts" in data
    assert isinstance(data["accounts"], list)
