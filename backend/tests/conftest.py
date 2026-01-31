"""
Test configuration and shared fixtures for all module tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock

from app.main import app
from app.core.database_config import Base, get_db

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_database.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override the get_db dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def test_db():
    """Test database fixture"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_user():
    """Mock user fixture"""
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.is_active = True
    return user

# Common test data
TEST_COMPANY_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_USER_ID = 1

# Response validation helpers
def assert_success_response(response, expected_status=200):
    """Assert that response follows standardized success format"""
    assert response.status_code == expected_status
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data
    return data

def assert_paginated_response(response, expected_status=200):
    """Assert that response follows standardized paginated format"""
    data = assert_success_response(response, expected_status)
    assert "data" in data
    assert "pagination" in data
    pagination = data["pagination"]
    assert "total" in pagination
    assert "page" in pagination
    assert "page_size" in pagination
    assert "pages" in pagination
    assert "has_next" in pagination
    assert "has_prev" in pagination
    return data

def assert_error_response(response, expected_status=400):
    """Assert that response follows standardized error format"""
    assert response.status_code == expected_status
    data = response.json()
    assert data["status"] == "error"
    assert "message" in data
    return data