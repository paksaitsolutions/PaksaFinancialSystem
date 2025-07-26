<<<<<<< HEAD
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Paksa Financial System",
    description="Enterprise Financial Management Platform",
    version="1.0.0"
)

# Add CORS middleware
=======
"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router

app = FastAPI(
    title="Paksa Financial System API",
    description="A comprehensive multi-tenant financial management system",
    version="1.0.0"
)

# CORS middleware
>>>>>>> 1f165d554f9014f0b749be3a8fe06df77942d7c1
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
@app.get("/")
async def root():
    return {
        "message": "Welcome to Paksa Financial System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/companies/available")
async def get_available_companies():
    return [
        {
            "id": 1,
            "tenant_id": "demo_company_1",
            "name": "Demo Company 1",
            "email": "demo1@paksa.com",
            "status": "active",
            "subscription_plan": "enterprise",
            "features": ["budgets", "fixed_assets", "tax_management", "inventory", "payroll", "reports", "ai_features"]
        },
        {
            "id": 2,
            "tenant_id": "demo_company_2", 
            "name": "Demo Company 2",
            "email": "demo2@paksa.com",
            "status": "active",
            "subscription_plan": "professional",
            "features": ["budgets", "fixed_assets", "tax_management", "reports"]
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
=======
# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Paksa Financial System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "paksa-financial-api"}
>>>>>>> 1f165d554f9014f0b749be3a8fe06df77942d7c1
