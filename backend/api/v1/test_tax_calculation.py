"""
Tests for tax calculation API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from app.main import app
from app.core.security import create_access_token
from app.models.user import User, UserRole

# Test client
client = TestClient(app)

# Test data
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "testpassword123",
    "role": UserRole.ADMIN,
    "is_active": True
}

# Test line items
TEST_LINE_ITEMS = [
    {
        "amount": "100.00",
        "quantity": 2,
        "tax_code": "STANDARD",
        "description": "Test Product",
        "is_taxable": True,
        "tax_included": False
    },
    {
        "amount": "50.00",
        "quantity": 1,
        "tax_code": "REDUCED",
        "description": "Test Service",
        "is_taxable": True,
        "tax_included": False
    }
]

# Helper function to get auth headers
def get_auth_headers(user: Dict[str, Any] = None) -> Dict[str, str]:
    if user is None:
        user = TEST_USER
    token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"Authorization": f"Bearer {token}"}

# Test calculate taxes endpoint
def test_calculate_taxes():
    """Test calculating taxes for a transaction."""
    # Test data
    payload = {
        "line_items": TEST_LINE_ITEMS,
        "billing_country": "US",
        "billing_state": "CA",
        "billing_city": "Los Angeles",
        "billing_zip": "90001",
        "transaction_date": "2025-01-01",
        "currency": "USD",
        "mode": "auto"
    }
    
    # Make request
    response = client.post(
        "/api/v1/tax/calculate",
        json=payload,
        headers=get_auth_headers()
    )
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert "transaction_id" in data
    assert data["currency"] == "USD"
    assert Decimal(data["subtotal"]) > 0
    assert Decimal(data["tax_amount"]) >= 0
    assert Decimal(data["total"]) >= Decimal(data["subtotal"])
    assert len(data["line_items"]) == len(TEST_LINE_ITEMS)
    
    # Check line items
    for i, item in enumerate(data["line_items"]):
        assert "tax_amount" in item
        assert "tax_rate" in item
        assert "total_amount" in item
        
        # Verify calculated amounts
        if i == 0:  # Standard rate item
            assert Decimal(item["tax_rate"]) > 0
            assert Decimal(item["tax_amount"]) > 0
        elif i == 1:  # Reduced rate item
            assert Decimal(item["tax_rate"]) > 0
            assert Decimal(item["tax_amount"]) > 0


def test_calculate_taxes_with_exemption():
    """Test tax calculation with tax exemption."""
    # Test data with exemption
    payload = {
        "line_items": TEST_LINE_ITEMS,
        "billing_country": "US",
        "billing_state": "CA",
        "customer_id": "CUST123",
        "customer_type": "BUSINESS",
        "exemption_certificate_id": "EXEMPT123",
        "exemption_reason": "Resale certificate",
        "transaction_date": "2025-01-01",
        "currency": "USD"
    }
    
    # Make request
    response = client.post(
        "/api/v1/tax/calculate",
        json=payload,
        headers=get_auth_headers()
    )
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    
    # Should be exempt from tax
    assert data["is_exempt"] is True
    assert data["exemption_certificate_id"] == "EXEMPT123"
    assert Decimal(data["tax_amount"]) == 0
    assert Decimal(data["total"]) == Decimal(data["subtotal"])


def test_calculate_taxes_invalid_data():
    """Test tax calculation with invalid data."""
    # Missing required fields
    payload = {
        "line_items": [],  # Empty line items
        "billing_country": "US"
    }
    
    response = client.post(
        "/api/v1/tax/calculate",
        json=payload,
        headers=get_auth_headers()
    )
    
    assert response.status_code == 422  # Validation error
    
    # Invalid country code
    payload = {
        "line_items": TEST_LINE_ITEMS,
        "billing_country": "INVALID",
        "billing_state": "CA"
    }
    
    response = client.post(
        "/api/v1/tax/calculate",
        json=payload,
        headers=get_auth_headers()
    )
    
    assert response.status_code == 400  # Bad request


def test_get_tax_rates():
    """Test getting tax rates for a location."""
    # Test with required country code
    response = client.get(
        "/api/v1/tax/rates?country_code=US",
        headers=get_auth_headers()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["country_code"] == "US"
    assert "rates" in data
    assert len(data["rates"]) > 0
    
    # Test with state and zip
    response = client.get(
        "/api/v1/tax/rates?country_code=US&state_code=CA&postal_code=90001",
        headers=get_auth_headers()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["state_code"] == "CA"
    assert data["postal_code"] == "90001"


def test_validate_exemption():
    """Test validating a tax exemption certificate."""
    # Test with valid exemption
    response = client.get(
        "/api/v1/tax/validate-exemption?exemption_id=EXEMPT123&country_code=US&state_code=CA",
        headers=get_auth_headers()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["exemption_id"] == "EXEMPT123"
    assert data["is_valid"] is True
    assert "valid_from" in data
    assert "valid_to" in data
    
    # Test with invalid exemption
    response = client.get(
        "/api/v1/tax/validate-exemption?exemption_id=INVALID&country_code=US",
        headers=get_auth_headers()
    )
    
    # Even with invalid ID, we return 200 but with is_valid=False
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False


def test_unauthorized_access():
    """Test that unauthorized access is denied."""
    # No auth header
    response = client.post("/api/v1/tax/calculate", json={"line_items": []})
    assert response.status_code == 401  # Unauthorized
    
    # Invalid token
    response = client.post(
        "/api/v1/tax/calculate",
        json={"line_items": []},
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401  # Unauthorized
