"""
API endpoints for invoicing.
"""
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.db.router import db_router
from app.core.api_response import success_response, error_response
from app.core.permissions import require_permission, Permission
from app.crud.invoicing.invoice_crud import invoice_crud, invoice_template_crud
from app.schemas.invoicing.invoice_schemas import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    InvoiceTemplateCreate, InvoiceTemplateResponse,
    InvoicePaymentCreate, InvoicePaymentResponse
)

router = APIRouter()

# Mock tenant ID - in real app, get from JWT token
MOCK_TENANT_ID = UUID("12345678-1234-5678-9012-123456789012")

# Invoice endpoints
@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_in: InvoiceCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create a new invoice."""
    invoice = await invoice_crud.create_invoice(
        db, tenant_id=MOCK_TENANT_ID, obj_in=invoice_in
    )
    return success_response(
        data=invoice,
        message="Invoice created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/", response_model=List[InvoiceResponse])
async def get_invoices(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
    payment_status: Optional[str] = Query(None),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get invoices."""
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    if payment_status:
        filters["payment_status"] = payment_status
    
    invoices = await invoice_crud.get_invoices(
        db, tenant_id=MOCK_TENANT_ID, skip=skip, limit=limit, filters=filters
    )
    return success_response(data=invoices)

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    invoice_id: UUID,
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get invoice by ID."""
    invoice = await invoice_crud.get_invoice(
        db, tenant_id=MOCK_TENANT_ID, id=invoice_id
    )
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return success_response(data=invoice)

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_id: UUID,
    invoice_in: InvoiceUpdate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Update invoice."""
    invoice = await invoice_crud.get_invoice(
        db, tenant_id=MOCK_TENANT_ID, id=invoice_id
    )
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    invoice = await invoice_crud.update_invoice(db, db_obj=invoice, obj_in=invoice_in)
    return success_response(
        data=invoice,
        message="Invoice updated successfully",
    )

@router.post("/{invoice_id}/send")
async def send_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_id: UUID,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Send invoice to customer."""
    invoice = await invoice_crud.get_invoice(
        db, tenant_id=MOCK_TENANT_ID, id=invoice_id
    )
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    if invoice.status != "draft":
        return error_response(
            message="Only draft invoices can be sent",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    invoice = await invoice_crud.send_invoice(db, invoice=invoice)
    return success_response(
        data=invoice,
        message="Invoice sent successfully",
    )

@router.post("/{invoice_id}/payments", response_model=InvoicePaymentResponse)
async def add_payment(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_id: UUID,
    payment_in: InvoicePaymentCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Add payment to invoice."""
    invoice = await invoice_crud.get_invoice(
        db, tenant_id=MOCK_TENANT_ID, id=invoice_id
    )
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    payment = await invoice_crud.add_payment(
        db, invoice=invoice, payment_data=payment_in
    )
    return success_response(
        data=payment,
        message="Payment added successfully",
        status_code=status.HTTP_201_CREATED,
    )

# Template endpoints
@router.post("/templates", response_model=InvoiceTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    *,
    db: AsyncSession = Depends(get_db),
    template_in: InvoiceTemplateCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create invoice template."""
    template = await invoice_template_crud.create_template(
        db, tenant_id=MOCK_TENANT_ID, obj_in=template_in
    )
    return success_response(
        data=template,
        message="Template created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/templates", response_model=List[InvoiceTemplateResponse])
async def get_templates(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    active_only: bool = Query(True),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get invoice templates."""
    templates = await invoice_template_crud.get_templates(
        db, tenant_id=MOCK_TENANT_ID, active_only=active_only
    )
    return success_response(data=templates)