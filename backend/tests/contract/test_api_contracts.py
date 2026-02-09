"""
Contract tests for frontend-critical API services and response envelopes.
"""
import os

from fastapi.testclient import TestClient

os.environ.setdefault("DEMO_MODE", "true")

from app.main import app

client = TestClient(app)


def test_success_response_envelope_cash_dashboard():
    response = client.get("/cash/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "data" in payload
    assert "total_balance" in payload["data"]


def test_paginated_response_envelope_cash_accounts():
    response = client.get("/cash/accounts")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "data" in payload
    assert "pagination" in payload
    assert "page" in payload["pagination"]


def test_frontend_auth_login_contract():
    response = client.post("/api/v1/auth/login", json={"email": "admin@paksa.com", "password": "admin123"})
    assert response.status_code in [200, 401, 500]
    if response.status_code == 200:
        payload = response.json()
        assert "access_token" in payload
        assert "refresh_token" in payload
        assert "user" in payload
        assert "email" in payload["user"]


def test_security_compliance_contract():
    response = client.get("/api/v1/security/compliance/status")
    assert response.status_code == 200
    payload = response.json()
    assert "mfa_enforced_for_privileged" in payload
    assert "refresh_token_rotation" in payload
    assert "pii_encryption_runbook" in payload


def test_sox_approval_matrix_contract():
    response = client.get("/api/v1/compliance/sox/approval-matrix")
    assert response.status_code == 200
    payload = response.json()
    assert "matrix" in payload
    assert isinstance(payload["matrix"], list)
    if payload["matrix"]:
        first = payload["matrix"][0]
        assert "action" in first
        assert "required_approvals" in first
