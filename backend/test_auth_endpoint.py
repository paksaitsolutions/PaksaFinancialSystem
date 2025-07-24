"""
Simple script to test the /auth/token endpoint.
"""
import requests

# Test user credentials
TEST_USER_EMAIL = "admin@example.com"
TEST_USER_PASSWORD = "admin123"  # In a real app, this would be hashed

def test_auth_endpoint():
    """Test the /auth/token endpoint."""
    url = "http://localhost:8000/auth/token"
    
    # Test with invalid credentials first
    print("Testing with invalid credentials...")
    response = requests.post(
        url,
        data={"username": "nonexistent@example.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Status code (should be 401): {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test with valid credentials
    print("\nTesting with valid credentials...")
    response = requests.post(
        url,
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Authentication successful!")
        print(f"Access token: {response.json()['access_token'][:50]}...")
    else:
        print("❌ Authentication failed")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_auth_endpoint()
