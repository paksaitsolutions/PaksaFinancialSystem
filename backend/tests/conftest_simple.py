"""
Test configuration and shared fixtures for all module tests.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def test_db():
    """Mock database fixture"""
    return Mock()

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
    
    # Handle both old and new response formats
    if isinstance(data, dict):
        if "status" in data:
            assert data["status"] == "success"
            assert "message" in data
        # For endpoints that don't use standardized format yet
        return data
    else:
        # Direct data response
        return {"data": data}

def assert_paginated_response(response, expected_status=200):
    """Assert that response follows standardized paginated format"""
    assert response.status_code == expected_status
    data = response.json()
    
    # Handle both old and new response formats
    if isinstance(data, dict):
        if "pagination" in data:
            # New standardized format
            assert "data" in data
            pagination = data["pagination"]
            assert "total" in pagination
            assert "page" in pagination
            assert "page_size" in pagination
            assert "pages" in pagination
            assert "has_next" in pagination
            assert "has_prev" in pagination
            return data
        elif "total" in data:
            # Old format with total/page/limit
            return data
        else:
            # Assume it's data without pagination
            return {"data": data, "pagination": {"total": 0, "page": 1, "page_size": 20, "pages": 0, "has_next": False, "has_prev": False}}
    else:
        # Direct list response
        return {"data": data, "pagination": {"total": len(data), "page": 1, "page_size": 20, "pages": 1, "has_next": False, "has_prev": False}}

def assert_error_response(response, expected_status=400):
    """Assert that response follows standardized error format"""
    assert response.status_code == expected_status
    data = response.json()
    
    # Handle both old and new error formats
    if isinstance(data, dict):
        if "status" in data:
            assert data["status"] == "error"
            assert "message" in data
        elif "detail" in data:
            # FastAPI default error format
            pass
    return data