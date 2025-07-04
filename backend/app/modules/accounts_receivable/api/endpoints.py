"""
API endpoints for the Accounts Receivable module.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_active_user
from . import schemas, services
from ..users.models import User

router = APIRouter()

# Invoices
@router.post("/invoices/", response_model=schemas.InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice: schemas.InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new invoice."""
    try:
        return services.InvoiceService.create_invoice(db, invoice, current_user.id)
    except services.exceptions.ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except services.exceptions.BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/invoices/", response_model=List[schemas.InvoiceResponse])
async def list_invoices(
    status: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    is_overdue: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List invoices with optional filters."""
    try:
        invoices, total = services.InvoiceService.list_invoices(
            db=db,
            status=status,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            is_overdue=is_overdue,
            page=page,
            page_size=page_size,
        )
        # TODO: Add pagination headers
        return invoices
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get an invoice by ID."""
    try:
        invoice = services.InvoiceService.get_invoice(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        return invoice
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    invoice_update: schemas.InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing invoice."""
    try:
        return services.InvoiceService.update_invoice(db, invoice_id, invoice_update, current_user.id)
    except services.exceptions.NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    except services.exceptions.ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except services.exceptions.BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/invoices/{invoice_id}/send", response_model=schemas.InvoiceResponse)
async def send_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark an invoice as sent."""
    try:
        return services.InvoiceService.send_invoice(db, invoice_id, current_user.id)
    except services.exceptions.NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    except services.exceptions.BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/invoices/{invoice_id}/void", response_model=schemas.InvoiceResponse)
async def void_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Void an invoice."""
    try:
        return services.InvoiceService.void_invoice(db, invoice_id, current_user.id)
    except services.exceptions.NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    except services.exceptions.BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Payments
@router.post("/payments/", response_model=schemas.PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record a payment."""
    try:
        return services.PaymentService.record_payment(db, payment, current_user.id)
    except services.exceptions.ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except services.exceptions.BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/payments/", response_model=List[schemas.PaymentResponse])
async def list_payments(
    invoice_id: Optional[UUID] = None,
    customer_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List payments with optional filters."""
    try:
        payments, total = services.PaymentService.list_payments(
            db=db,
            invoice_id=invoice_id,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            page=page,
            page_size=page_size,
        )
        # TODO: Add pagination headers
        return payments
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/payments/{payment_id}", response_model=schemas.PaymentResponse)
async def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a payment by ID."""
    try:
        payment = services.PaymentService.get_payment(db, payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return payment
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Credit Notes
@router.post("/credit-notes/", response_model=schemas.CreditNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_credit_note(
    credit_note: schemas.CreditNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a credit note."""
    try:
        return services.CreditNoteService.create_credit_note(db, credit_note, current_user.id)
    except services.exceptions.ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except services.exceptions.BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Reports
@router.get("/reports/accounts-aging")
async def get_accounts_aging_report(
    as_of_date: date = date.today(),
    customer_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get accounts aging report."""
    try:
        return services.ReportingService.get_accounts_aging_report(db, as_of_date, customer_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
