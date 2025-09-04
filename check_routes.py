import requests
import json

try:
    # Get the OpenAPI schema
    response = requests.get("http://localhost:8000/openapi.json")
    
    if response.status_code == 200:
        schema = response.json()
        
        # Print all paths
        print("\nAll registered API paths:")
        print("-" * 80)
        for path in schema.get("paths", {}).keys():
            print(f"- {path}")
        
        # Check for payroll analytics paths
        print("\nPayroll analytics paths:")
        print("-" * 80)
        payroll_paths = [p for p in schema.get("paths", {}).keys() if "/api/payroll/analytics" in p]
        
        if payroll_paths:
            for path in payroll_paths:
                print(f"- {path}")
                # Print available methods
                for method, details in schema["paths"][path].items():
                    if method in ["get", "post", "put", "delete", "patch"]:
                        print(f"  {method.upper()}: {details.get('summary', 'No description')}")
        else:
            print("No payroll analytics paths found!")
            
    else:
        print(f"Failed to get OpenAPI schema. Status code: {response.status_code}")
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"Error connecting to the FastAPI server: {e}")
    print("\nPlease make sure the FastAPI server is running.")
