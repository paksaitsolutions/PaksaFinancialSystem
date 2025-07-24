"""
Script to start the FastAPI server for testing.
"""
import os
import sys
import uvicorn
from pathlib import Path

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def main():
    """Main function to start the FastAPI server."""
    print("🚀 Starting FastAPI Server")
    
    # Set default environment variables if not set
    os.environ.setdefault("ENV", "development")
    os.environ.setdefault("DEBUG", "True")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "changethis")
    os.environ.setdefault("DATABASE_URL", "sqlite:///./paksa_finance.db")
    
    # Print environment variables
    print_section("Server Configuration")
    for var in ["ENV", "DEBUG", "SECRET_KEY", "FIRST_SUPERUSER_EMAIL", 
                "FIRST_SUPERUSER_PASSWORD", "DATABASE_URL"]:
        value = os.environ.get(var, "Not set")
        if "PASSWORD" in var or "SECRET" in var:
            value = "[HIDDEN]" if value != "Not set" else value
        print(f"{var}: {value}")
    
    # Start the server
    print_section("Starting Server")
    print("🌐 Starting FastAPI server on http://localhost:8000")
    print("📚 API documentation available at http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have installed the required dependencies:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
