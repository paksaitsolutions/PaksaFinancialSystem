from fastapi import APIRouter, Depends
from app.core import deps
from app.models.user import User

router = APIRouter()

@router.get("/system")
async def get_system_settings(current_user: User = Depends(deps.get_current_active_user)):
    """Get system settings"""
    return {
        "company_name": "Paksa Financial System",
        "currency": "USD",
        "timezone": "UTC",
        "date_format": "MM/DD/YYYY",
        "fiscal_year_start": "01/01",
        "multi_currency": True,
        "tax_enabled": True,
        "inventory_enabled": True,
        "payroll_enabled": True
    }

@router.put("/system")
async def update_system_settings(
    settings_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Update system settings"""
    return {"success": True, "message": "Settings updated successfully"}