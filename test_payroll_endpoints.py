"""
Script to test the payroll analytics endpoints
"""
import os
import sys
import requests
from datetime import date, timedelta

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(endpoint, method="GET", json_data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\nTesting {method} {url}")
    print("-" * 80)
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=json_data)
        else:
            print(f"Unsupported method: {method}")
            return
            
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("Response:", response.json())
            
    except Exception as e:
        print(f"Error testing endpoint: {e}")

def main():
    """Test all payroll analytics endpoints"""
    # Test payroll analytics endpoints
    test_endpoint("/api/payroll/analytics/trends?period=monthly", "GET")
    test_endpoint("/api/payroll/analytics/anomalies", "GET")
    test_endpoint("/api/payroll/analytics/cost-analysis", "GET")

if __name__ == "__main__":
    print("Testing Payroll Analytics Endpoints")
    print("=" * 80)
    main()
