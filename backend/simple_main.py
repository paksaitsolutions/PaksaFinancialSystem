"""
Simple FastAPI Application for Accounting Module
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.database import get_db, init_db
from app.models.accounting import *
from app.api.accounting import router as accounting_router
import sqlite3
from datetime import datetime

app = FastAPI(
    title="Paksa Financial System - Accounting",
    description="Professional Accounting Module",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include accounting router
app.include_router(accounting_router, prefix="/api/v1/accounting", tags=["accounting"])

@app.get("/")
def root():
    return {
        "message": "Paksa Financial System - Accounting Module",
        "version": "1.0.0",
        "status": "operational",
        "modules": ["GL", "AP", "AR", "Budget", "Tax"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Simple auth endpoints
@app.post("/auth/login")
def login(credentials: dict):
    if credentials.get("email") == "admin@paksa.com" and credentials.get("password") == "admin123":
        return {
            "access_token": "demo-token-12345",
            "user": {
                "id": "1",
                "email": "admin@paksa.com",
                "firstName": "System",
                "lastName": "Administrator",
                "roles": ["admin"],
                "isAdmin": True
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/auth/me")
def get_current_user():
    return {
        "id": "1",
        "email": "admin@paksa.com",
        "firstName": "System",
        "lastName": "Administrator"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Paksa Financial System - Accounting Module")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")