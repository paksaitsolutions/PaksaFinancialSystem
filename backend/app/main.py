from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="Paksa Financial System - Local Production",
    description="Complete Financial Management System - Local Testing Environment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Paksa Financial System - Local Production Environment",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "modules": [
            "General Ledger",
            "Accounts Payable", 
            "Accounts Receivable",
            "Budget Management",
            "Cash Management",
            "Human Resources",
            "Inventory Management",
            "Business Intelligence",
            "AI Assistant"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": "/api/v1"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "paksa-financial-system",
        "version": "1.0.0",
        "environment": "local_production",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/companies/available")
async def get_available_companies():
    return [
        {
            "id": 1,
            "tenant_id": "12345678-1234-5678-9012-123456789012",
            "name": "Paksa Demo Company",
            "email": "demo@paksa.com",
            "status": "active",
            "subscription_plan": "enterprise",
            "features": ["gl", "ap", "ar", "budget", "cash", "hrm", "inventory", "tax", "bi", "ai"]
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
