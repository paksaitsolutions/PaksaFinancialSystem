import requests
from datetime import datetime, timedelta

def test_endpoint(url, method="get", data=None):
    try:
        if method.lower() == "get":
            response = requests.get(url, timeout=10)
        elif method.lower() == "post":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"\nTesting {url}")
        print("-" * 80)
        print(f"Status Code: {response.status_code}")
        
        try:
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        except ValueError:
            print(f"Response (text): {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing {url}: {str(e)}")
        return False

if __name__ == "__main__":
    base_url = "http://localhost:8000"
    
    # Test the root endpoint first
    test_endpoint(f"{base_url}/")
    
    # Test payroll analytics endpoints
    endpoints = [
        f"{base_url}/api/payroll/analytics/trends?period=monthly&limit=6",
        f"{base_url}/api/payroll/analytics/cost?period=current_month&group_by=department",
    ]
    
    # Add the anomalies endpoint with date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    endpoints.append(
        f"{base_url}/api/payroll/analytics/anomalies?start_date={start_date}&end_date={end_date}&min_severity=medium"
    )
    
    # Test all endpoints
    print("\n" + "="*80)
    print("TESTING PAYROLL ANALYTICS ENDPOINTS")
    print("="*80)
    
    success = True
    for endpoint in endpoints:
        if not test_endpoint(endpoint):
            success = False
    
    if success:
        print("\n✅ All payroll analytics endpoints are working!")
    else:
        print("\n❌ Some payroll analytics endpoints failed. Check the output above for details.")
