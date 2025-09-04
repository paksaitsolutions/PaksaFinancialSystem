import requests

try:
    # Try to access the FastAPI server
    response = requests.get("http://localhost:8000/", timeout=5)
    print(f"Server is running! Status code: {response.status_code}")
    print(f"Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Could not connect to the FastAPI server: {e}")
    print("\nPlease make sure the FastAPI server is running.")
    print("You can start it with: uvicorn app.main:app --reload --port 8000")
