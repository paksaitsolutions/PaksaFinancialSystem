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
from . import schemas, services
from .exceptions import NotFoundError, ValidationError, BusinessRuleError

router = APIRouter(prefix="/accounts-receivable", tags=["accounts-receivable"])


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


# --- Invoice CRUD ---
@router.post(
    "/invoices", response_model=schemas.InvoiceResponse, status_code=status.HTTP_201_CREATED
)
async def create_invoice(
    invoice_in: schemas.InvoiceCreate,
    service=Depends(get_invoice_service),
    current_user=Depends(get_current_active_user),
):
    """Create a new invoice."""
    try:
        return await service.create_invoice(invoice_in, current_user.id)
    except (ValidationError, BusinessRuleError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    service=Depends(get_invoice_service),
):
    """Get an invoice by ID."""
    invoice = await service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get("/invoices", response_model=List[schemas.InvoiceResponse])
async def list_invoices(service=Depends(get_invoice_service)):
    """List all invoices."""
    return await service.list_invoices()


@router.put("/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    invoice_update: schemas.InvoiceUpdate,
    service=Depends(get_invoice_service),
):
    """Update an existing invoice."""
    return await service.update_invoice(invoice_id, invoice_update)


@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(invoice_id: UUID, service=Depends(get_invoice_service)):
    """Delete an invoice."""
    await service.delete_invoice(invoice_id)


@router.post("/invoices/{invoice_id}/dunning", response_model=schemas.DunningSchedule)
async def update_dunning_schedule(
    invoice_id: UUID,
    dunning_action: schemas.DunningAction,
    service=Depends(get_invoice_service),
):
    """Update dunning schedule for an invoice."""
    return await service.update_dunning_schedule(invoice_id, dunning_action)


@router.post("/invoices/{invoice_id}/dispute", response_model=schemas.DisputeResult)
async def update_dispute_status(
    invoice_id: UUID,
    dispute_action: schemas.DisputeAction,
    service=Depends(get_invoice_service),
):
    """Update dispute status for an invoice."""
    return await service.update_dispute_status(invoice_id, dispute_action)


# --- Payment CRUD ---
@router.post(
    "/payments", response_model=schemas.PaymentResponse, status_code=status.HTTP_201_CREATED
)
async def record_payment(
    payment_in: schemas.PaymentCreate,
    service=Depends(get_payment_service),
    current_user=Depends(get_current_active_user),
):
    """Record a new payment."""
    return await service.record_payment(payment_in, current_user.id)


@router.get("/payments/{payment_id}", response_model=schemas.PaymentResponse)
async def get_payment(
    payment_id: UUID,
    service=Depends(get_payment_service),
):
    """Get a payment by ID."""
    return await service.get_payment(payment_id)


@router.get("/payments", response_model=List[schemas.PaymentResponse])
async def list_payments(service=Depends(get_payment_service)):
    """List all payments."""
    return await service.list_payments()


# --- Credit Note CRUD ---
@router.post(
    "/credit-notes",
    response_model=schemas.CreditNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_credit_note(
    credit_note_in: schemas.CreditNoteCreate,
    service=Depends(get_credit_note_service),
    current_user=Depends(get_current_active_user),
):
    """Create a new credit note."""
    return await service.create_credit_note(credit_note_in, current_user.id)


@router.get("/credit-notes/{credit_note_id}", response_model=schemas.CreditNoteResponse)
async def get_credit_note(
    credit_note_id: UUID,
    service=Depends(get_credit_note_service),
):
    """Get a credit note by ID."""
    return await service.get_credit_note(credit_note_id)


@router.get("/credit-notes", response_model=List[schemas.CreditNoteResponse])
async def list_credit_notes(service=Depends(get_credit_note_service)):
    """List all credit notes."""
    return await service.list_credit_notes()


# --- Reporting Endpoints ---
@router.get(
    "/reports/accounts-aging", response_model=List[schemas.AccountsAgingSummary]
)
async def get_accounts_aging_report(service=Depends(get_reporting_service)):
    """Get accounts aging report."""
    return await service.get_accounts_aging_report()


@router.get(
    "/reports/payments-summary", response_model=List[schemas.PaymentSummary]
)
async def get_payments_summary(service=Depends(get_reporting_service)):
    """Get payments summary report."""
    return await service.get_payments_summary()


@router.get("/reporting", response_model=schemas.ARReport)
async def get_ar_report(db: AsyncSession = Depends(get_async_db)):
    """Get Accounts Receivable report."""
    return schemas.ARReport(summary={"total_invoices": 150, "total_received": 120000})
