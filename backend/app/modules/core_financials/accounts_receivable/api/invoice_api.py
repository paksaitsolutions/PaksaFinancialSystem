from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.db.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from ..services.invoice_service import InvoiceService

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new invoice with real database persistence"""
    invoice_service = InvoiceService()
    invoice = await invoice_service.create_invoice(db, invoice_data, current_user.id)
    return {"message": "Invoice created successfully", "data": invoice}

@router.get("/")
async def get_invoices(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all invoices with real database filtering"""
    invoice_service = InvoiceService()
    invoices = await invoice_service.get_invoices(db, skip, limit, status, customer_id)
    return {"invoices": invoices, "total": len(invoices)}

@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoice by ID with complete details"""
    invoice_service = InvoiceService()
    invoice = await invoice_service.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.post("/{invoice_id}/send")
async def send_invoice(
    invoice_id: int,
    send_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send invoice to customer"""
    invoice_service = InvoiceService()
    result = await invoice_service.send_invoice(db, invoice_id, send_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice sent successfully", "data": result}

@router.post("/{invoice_id}/payment")
async def record_payment(
    invoice_id: int,
    payment_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record payment against invoice"""
    invoice_service = InvoiceService()
    result = await invoice_service.record_payment(db, invoice_id, payment_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Payment recorded successfully", "data": result}

@router.post("/{invoice_id}/void")
async def void_invoice(
    invoice_id: int,
    void_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Void an invoice"""
    invoice_service = InvoiceService()
    result = await invoice_service.void_invoice(db, invoice_id, void_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": "Invoice voided successfully", "data": result}

@router.post("/recurring/generate")
async def generate_recurring_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate recurring invoices that are due"""
    invoice_service = InvoiceService()
    result = await invoice_service.create_recurring_invoices(db, current_user.id)
    return {"message": f"Generated {result['created_count']} recurring invoices", "data": result}

@router.get("/overdue/list")
async def get_overdue_invoices(
    days_overdue: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overdue invoices"""
    # This could be moved to collections service, but keeping here for invoice context
    from ..services.collections_service import CollectionsService
    collections_service = CollectionsService()
    overdue = await collections_service.get_overdue_invoices(db, days_overdue)
    return {"overdue_invoices": overdue}