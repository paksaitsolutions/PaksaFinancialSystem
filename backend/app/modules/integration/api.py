from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.core.db.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from .cross_module_service import CrossModuleIntegrationService
from .workflow_integration_service import WorkflowIntegrationService
from .unified_reporting_service import UnifiedReportingService

router = APIRouter()

@router.get("/financial-summary/{company_id}")
async def get_integrated_financial_summary(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get integrated financial summary across all modules"""
    integration_service = CrossModuleIntegrationService()
    summary = await integration_service.get_integrated_financial_summary(db, company_id)
    return summary

@router.post("/workflows/purchase-to-payment")
async def process_purchase_to_payment(
    purchase_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process complete purchase-to-payment workflow"""
    workflow_service = WorkflowIntegrationService()
    result = await workflow_service.process_purchase_to_payment_workflow(db, purchase_data, current_user.id)
    return result

@router.post("/workflows/invoice-to-cash")
async def process_invoice_to_cash(
    invoice_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process complete invoice-to-cash workflow"""
    workflow_service = WorkflowIntegrationService()
    result = await workflow_service.process_invoice_to_cash_workflow(db, invoice_data, current_user.id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/workflows/budget-to-actual/{budget_id}")
async def process_budget_to_actual(
    budget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process budget-to-actual tracking workflow"""
    workflow_service = WorkflowIntegrationService()
    result = await workflow_service.process_budget_to_actual_workflow(db, budget_id, current_user.id)
    return result

@router.get("/reports/executive-dashboard/{company_id}")
async def get_executive_dashboard(
    company_id: int,
    period_start: date,
    period_end: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get executive dashboard with unified reporting"""
    reporting_service = UnifiedReportingService()
    dashboard = await reporting_service.generate_executive_dashboard(db, company_id, period_start, period_end)
    return dashboard

@router.get("/reports/cash-flow-statement/{company_id}")
async def get_cash_flow_statement(
    company_id: int,
    period_start: date,
    period_end: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get integrated cash flow statement"""
    reporting_service = UnifiedReportingService()
    statement = await reporting_service.generate_cash_flow_statement(db, company_id, period_start, period_end)
    return statement

@router.post("/sync/ap-to-cash/{payment_id}")
async def sync_ap_payment_to_cash(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sync AP payment to cash management"""
    integration_service = CrossModuleIntegrationService()
    result = await integration_service.sync_ap_to_cash_management(db, payment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found or not approved")
    return result

@router.post("/sync/ar-to-cash/{payment_id}")
async def sync_ar_payment_to_cash(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sync AR payment to cash management"""
    integration_service = CrossModuleIntegrationService()
    result = await integration_service.sync_ar_to_cash_management(db, payment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found or not processed")
    return result