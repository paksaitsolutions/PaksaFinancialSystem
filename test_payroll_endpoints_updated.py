"""
Test script to verify payroll analytics endpoints are properly registered.
"""
import sys
import os
from fastapi.testclient import TestClient

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Now import the FastAPI app
from app.main import app

# Create a test client
client = TestClient(app)

def list_routes():
    """List all registered routes in the FastAPI app."""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ", ".join(route.methods or [])
            routes.append({
                "path": route.path_format,
                "methods": methods,
                "name": getattr(route, "name", ""),
                "endpoint": getattr(route, "endpoint", "").__name__
            })
    return routes

# List all routes
print("\nAll registered routes:")
print("-" * 80)
for route in list_routes():
    print(f"{route['methods']:10} {route['path']}")

# Check for payroll analytics routes
print("\nPayroll analytics routes:")
print("-" * 80)
payroll_routes = [r for r in list_routes() if "/api/payroll/analytics" in r["path"]]
for route in payroll_routes:
    print(f"{route['methods']:10} {route['path']}")

if not payroll_routes:
    print("No payroll analytics routes found!")
else:
    # Test the endpoints
    print("\nTesting payroll analytics endpoints:")
    print("-" * 80)
    
    # Test get_payroll_trends
    try:
        response = client.get("/api/payroll/analytics/trends?period=monthly&limit=6")
        print(f"GET /api/payroll/analytics/trends - Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing /api/payroll/analytics/trends: {str(e)}")
    
    # Test detect_payroll_anomalies
    try:
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        response = client.get(f"/api/payroll/analytics/anomalies?start_date={start_date}&end_date={end_date}")
        print(f"GET /api/payroll/analytics/anomalies - Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing /api/payroll/analytics/anomalies: {str(e)}")
    
    # Test get_payroll_cost_analysis
    try:
        response = client.get("/api/payroll/analytics/cost?period=current_month&group_by=department")
        print(f"GET /api/payroll/analytics/cost - Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing /api/payroll/analytics/cost: {str(e)}")
