from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from uuid import UUID
from ..services.super_admin_service import SuperAdminService
from ..schemas.company import Company, CompanyUsage

router = APIRouter(prefix="/super-admin", tags=["Super Admin"])

# Initialize service
super_admin_service = SuperAdminService()

@router.get("/companies", response_model=List[Company])
async def get_all_companies():
    """Get all registered companies"""
    try:
        companies = super_admin_service.get_all_companies()
        return companies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/companies/{company_id}/approve")
async def approve_company(company_id: UUID):
    """Approve a pending company"""
    try:
        company = super_admin_service.approve_company(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return {"message": "Company approved successfully", "company": company}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/companies/{company_id}/suspend")
async def suspend_company(company_id: UUID, reason: str = ""):
    """Suspend a company"""
    try:
        company = super_admin_service.suspend_company(company_id, reason)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return {"message": "Company suspended successfully", "company": company}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies/{company_id}/usage", response_model=CompanyUsage)
async def get_company_usage(company_id: UUID):
    """Get usage statistics for a company"""
    try:
        usage = super_admin_service.get_company_usage(company_id)
        if not usage:
            raise HTTPException(status_code=404, detail="Usage data not found")
        return usage
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_platform_analytics():
    """Get platform-wide analytics"""
    try:
        analytics = super_admin_service.get_platform_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-health")
async def get_system_health():
    """Get system health metrics"""
    try:
        health = super_admin_service.get_system_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_global_config():
    """Get global system configuration"""
    try:
        config = super_admin_service.get_global_config()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config")
async def update_global_config(config: Dict[str, Any]):
    """Update global system configuration"""
    try:
        updated_config = super_admin_service.update_global_config(config)
        return {"message": "Configuration updated successfully", "config": updated_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))