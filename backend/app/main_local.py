"""
Local production main application with all modules enabled.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

# Import all routers
from app.api.endpoints.auth import auth_endpoints
from app.api.endpoints.gl import gl_endpoints
from app.api.endpoints.accounts_payable import ap_endpoints
from app.api.endpoints.accounts_receivable import ar_endpoints
from app.api.endpoints.budget import budget_endpoints
from app.api.endpoints.cash_management import cash_endpoints
from app.api.endpoints.hrm import hrm_endpoints
from app.api.endpoints.inventory import item_endpoints
from app.api.endpoints.bi_ai import bi_ai_endpoints
from app.api.endpoints.ai_assistant import ai_assistant_endpoints

# Import production components
from app.core.production.error_handler import ProductionErrorHandler
from app.core.security.production_security import ProductionSecurity
from app.core.monitoring.health_check import HealthMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Paksa Financial System - Local Production",
    description="Complete Financial Management System - Local Testing Environment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize services
security_service = ProductionSecurity()
health_monitor = HealthMonitor()
error_handler = ProductionErrorHandler()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Apply security checks to all requests."""
    # Rate limiting
    if not await security_service.check_rate_limit(request):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    response = await call_next(request)
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check."""
    health_status = await health_monitor.check_system_health()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "system": health_status,
        "version": "1.0.0"
    }

# API Routes
app.include_router(auth_endpoints.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(gl_endpoints.router, prefix="/api/v1/gl", tags=["General Ledger"])
app.include_router(ap_endpoints.router, prefix="/api/v1/ap", tags=["Accounts Payable"])
app.include_router(ar_endpoints.router, prefix="/api/v1/ar", tags=["Accounts Receivable"])
app.include_router(budget_endpoints.router, prefix="/api/v1/budget", tags=["Budget Management"])
app.include_router(cash_endpoints.router, prefix="/api/v1/cash", tags=["Cash Management"])
app.include_router(hrm_endpoints.router, prefix="/api/v1/hrm", tags=["Human Resources"])
app.include_router(item_endpoints.router, prefix="/api/v1/inventory", tags=["Inventory Management"])
app.include_router(bi_ai_endpoints.router, prefix="/api/v1/bi", tags=["Business Intelligence"])
app.include_router(ai_assistant_endpoints.router, prefix="/api/v1/ai", tags=["AI Assistant"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information."""
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

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return await error_handler.general_error_handler(request, exc)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)