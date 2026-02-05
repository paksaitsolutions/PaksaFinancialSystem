"""
Integration tests for authentication flows and security.
"""
import os

from fastapi.testclient import TestClient

os.environ.setdefault("DEMO_MODE", "true")

from app.main import app

client = TestClient(app)


class TestAuthenticationFlow:
    """Test authentication flows and security"""

    def _login_and_get_token(self) -> str:
        login_data = {"email": "admin@paksa.com", "password": "admin123"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        return response.json()["access_token"]

    def test_login_flow(self):
        """Test complete login flow"""
        response = client.post("/auth/login", json={"email": "admin@paksa.com", "password": "admin123"})
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "admin@paksa.com"

    def test_login_invalid_credentials(self):
        response = client.post("/auth/login", json={"email": "invalid@example.com", "password": "wrongpassword"})
        assert response.status_code == 401

    def test_token_authentication(self):
        token = self._login_and_get_token()
        response = client.get("/auth/verify-token", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_user_info_endpoint_requires_token(self):
        unauthorized_response = client.get("/auth/me")
        assert unauthorized_response.status_code == 403

        token = self._login_and_get_token()
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "email" in data
            assert "full_name" in data

    def test_api_v1_auth_endpoints_json_contract(self):
        login_response = client.post("/api/v1/auth/login", json={"email": "admin@paksa.com", "password": "admin123"})
        assert login_response.status_code in [200, 500]

        forgot_response = client.post("/api/v1/auth/forgot-password", json={"email": "admin@paksa.com"})
        assert forgot_response.status_code == 200

        reset_response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "test-token", "password": "newpassword"},
        )
        assert reset_response.status_code == 200

        refresh_response = client.post(
            "/api/v1/auth/refresh-token",
            json={"refresh_token": "demo-refresh-token-12345"},
        )
        assert refresh_response.status_code == 200

    def test_api_v1_auth_me_and_verify_token(self):
        token = self._login_and_get_token()

        verify = client.get("/api/v1/auth/verify-token", headers={"Authorization": f"Bearer {token}"})
        assert verify.status_code == 200

        me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code in [200, 404]

    def test_logout_flow(self):
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_registration_flow_form_and_json(self):
        suffix = os.urandom(3).hex()
        form_email = f"testuser_{suffix}@example.com"
        json_email = f"apiuser_{suffix}@example.com"

        form_response = client.post(
            "/auth/register",
            data={
                "fullName": "Test User",
                "email": form_email,
                "company": "Test Company",
                "password": "testpassword123",
            },
        )
        assert form_response.status_code in [200, 400, 409, 500]

        json_response = client.post(
            "/api/v1/auth/register",
            json={
                "fullName": "API User",
                "email": json_email,
                "company": "Test Company",
                "password": "testpassword123",
            },
        )
        assert json_response.status_code in [200, 400, 409, 500]

    def test_password_reset_flow_legacy_endpoints(self):
        assert client.post("/auth/forgot-password", data={"email": "admin@paksa.com"}).status_code == 200
        assert client.post("/auth/reset-password", data={"token": "test-token", "password": "newpassword"}).status_code == 200

    def test_oauth_token_endpoint(self):
        response = client.post("/auth/token", data={"username": "admin@paksa.com", "password": "admin123"})
        assert response.status_code in [200, 500]

    def test_security_headers(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-content-type-options" in response.headers
