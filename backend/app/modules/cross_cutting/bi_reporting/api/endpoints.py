"""
BI Reporting endpoints for advanced dashboards and KPI tracking.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from . import services, schemas

router = APIRouter(prefix="/bi-reporting", tags=["bi-reporting"])

@router.get("/kpi", response_model=schemas.KPIReport)
async def get_kpi_report(db: AsyncSession = Depends(get_async_db)):
    return await services.BIReportingService(db).get_kpi_report()

@router.get("/dashboard", response_model=schemas.BIDashboard)
async def get_bi_dashboard(db: AsyncSession = Depends(get_async_db)):
    return await services.BIReportingService(db).get_dashboard()
