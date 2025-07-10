"""
API endpoints for the Accounts Receivable module.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core.security import get_current_active_user
from .. import exceptions, models, schemas, services
from ...users.models import User

# Routers for each resource
router_invoices = APIRouter(prefix="/invoices", tags=["Accounts Receivable - Invoices"])
router_payments = APIRouter(prefix="/payments", tags=["Accounts Receivable - Payments"])
router_credit_notes = APIRouter(
    prefix="/credit-notes", tags=["Accounts Receivable - Credit Notes"]
)
router_reports = APIRouter(prefix="/reports", tags=["Accounts Receivable - Reports"])


# --- Dependencies ---
def get_invoice_service(
    db: AsyncSession = Depends(get_async_db),
) -> services.InvoiceService:
    return services.InvoiceService(db)


def get_payment_service(
    db: AsyncSession = Depends(get_async_db),
) -> services.PaymentService:
    return services.PaymentService(db)


def get_credit_note_service(
    db: AsyncSession = Depends(get_async_db),
) -> services.CreditNoteService:
    return services.CreditNoteService(db)


def get_reporting_service(
    db: AsyncSession = Depends(get_async_db),
) -> services.ReportingService:
    return services.ReportingService(db)


# --- Invoice Endpoints ---
@router_invoices.post(
    "/", response_model=schemas.InvoiceResponse, status_code=status.HTTP_201_CREATED
)
async def create_invoice(
    invoice_in: schemas.InvoiceCreate,
    service: services.InvoiceService = Depends(get_invoice_service),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new invoice."""
    try:
        return await service.create_invoice(invoice_in, current_user.id)
    except (exceptions.ValidationError, exceptions.BusinessRuleError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router_invoices.get("/{invoice_id}", response_model=schemas.InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    service: services.InvoiceService = Depends(get_invoice_service),
):
    """Get an invoice by ID."""
    invoice = await service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )
    return invoice
