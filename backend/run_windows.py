"""
Windows-compatible startup script for Paksa Financial System.
"""
import uvicorn
import os
from pathlib import Path

# Set environment variables for Windows
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./paksa_financial.db"
os.environ["ENVIRONMENT"] = "development"
os.environ["JWT_SECRET_KEY"] = "your-secret-key-here-change-in-production"

if __name__ == "__main__":
    print("🚀 Starting Paksa Financial System on Windows...")
    print("📊 Using SQLite database for local development")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )