"""
Simple FastAPI application for Windows testing.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="Paksa Financial System - Windows Local",
    description="Financial Management System running on Windows",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Paksa Financial System - Windows Local Environment",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "platform": "Windows",
        "database": "SQLite"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "paksa-financial-system",
        "version": "1.0.0",
        "environment": "windows_local",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/companies/available")
async def get_companies():
    return [
        {
            "id": 1,
            "name": "Demo Company",
            "status": "active",
            "features": ["gl", "ap", "ar", "budget", "cash", "hrm"]
        }
    ]

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Paksa Financial System on Windows...")
    print("🌐 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)