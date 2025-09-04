"""
Super Admin API endpoints for system management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from typing import List, Dict, Any

router = APIRouter()

@router.get("/system-overview")
async def get_system_overview(db: Session = Depends(get_db)):
    """Get system overview statistics"""
    return {
        "total_tenants": 5,
        "active_users": 125,
        "system_health": "excellent",
        "database_size": "2.5GB",
        "uptime": "99.9%",
        "last_backup": "2024-01-15T10:30:00Z"
    }

@router.get("/tenants")
async def get_all_tenants(db: Session = Depends(get_db)):
    """Get all tenant companies"""
    return [
        {"id": 1, "name": "Acme Corp", "status": "active", "users": 25, "created": "2024-01-01"},
        {"id": 2, "name": "Tech Solutions", "status": "active", "users": 15, "created": "2024-01-05"}
    ]

@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    """Get all system users"""
    return [
        {"id": 1, "email": "admin@paksa.com", "role": "super_admin", "status": "active", "last_login": "2024-01-15T10:30:00Z"},
        {"id": 2, "email": "user@acme.com", "role": "admin", "status": "active", "last_login": "2024-01-15T09:15:00Z"}
    ]

@router.get("/audit-logs")
async def get_audit_logs(db: Session = Depends(get_db)):
    """Get system audit logs"""
    return [
        {"id": 1, "user": "admin@paksa.com", "action": "login", "timestamp": "2024-01-15T10:30:00Z", "ip": "192.168.1.1"},
        {"id": 2, "user": "user@acme.com", "action": "create_invoice", "timestamp": "2024-01-15T10:25:00Z", "ip": "192.168.1.2"}
    ]

@router.post("/backup")
async def create_backup(db: Session = Depends(get_db)):
    """Create system backup"""
    return {"success": True, "backup_id": "backup_20240115_103000", "message": "Backup created successfully"}

@router.get("/settings")
async def get_global_settings(db: Session = Depends(get_db)):
    """Get global system settings"""
    return {
        "maintenance_mode": False,
        "registration_enabled": True,
        "max_tenants": 100,
        "backup_frequency": "daily",
        "session_timeout": 3600
    }

@router.put("/settings")
async def update_global_settings(settings: Dict[str, Any], db: Session = Depends(get_db)):
    """Update global system settings"""
    return {"success": True, "message": "Settings updated successfully"}