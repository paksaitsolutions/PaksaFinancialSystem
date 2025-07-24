"""
API endpoints for invoice processing.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.accounts_payable.invoice import invoice_crud
from app.schemas.accounts_payable.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceApprovalRequest,
)

router = APIRouter()

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_in: InvoiceCreate,
) -> Any:
    """
    Create a new invoice.
    """
    invoice = await invoice_crud.create(db, obj_in=invoice_in)
    return success_response(
        data=invoice,
        message="Invoice created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/", response_model=InvoiceListResponse)
async def get_invoices(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    from_date: Optional[str] = Query(None, description="Filter by invoice date (from)"),
    to_date: Optional[str] = Query(None, description="Filter by invoice date (to)"),
) -> Any:
    """
    Get list of invoices with pagination and filtering.
    """
    # Build filters
    filters = {}
    if vendor_id:
        filters["vendor_id"] = vendor_id
    if status:
        filters["status"] = status
    if from_date:
        filters["invoice_date_from"] = from_date
    if to_date:
        filters["invoice_date_to"] = to_date
    
    result = await invoice_crud.get_paginated(
        db,
        page=page,
        page_size=page_size,
        filters=filters,
        sort_by=sort_by or "invoice_date",
        sort_order=sort_order,
    )
    
    return success_response(
        data=result["items"],
        meta={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": result["pagination"]["total"],
                "pages": result["pagination"]["total_pages"],
            }
        },
    )

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_id: UUID,
) -> Any:
    """
    Get a specific invoice by ID.
    """
    invoice = await invoice_crud.get(db, id=invoice_id)
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
) -> Any:
    """
    Update an invoice.
    """
    invoice = await invoice_crud.get(db, id=invoice_id)
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if invoice can be updated (not in final status)
    if invoice.status in ["paid", "voided", "cancelled"]:
        return error_response(
            message=f"Invoice in '{invoice.status}' status cannot be updated",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    invoice = await invoice_crud.update(db, db_obj=invoice, obj_in=invoice_in)
    return success_response(
        data=invoice,
        message="Invoice updated successfully",
    )

@router.delete("/{invoice_id}", response_model=Dict[str, Any])
async def delete_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_id: UUID,
) -> Any:
    """
    Delete an invoice.
    """
    invoice = await invoice_crud.get(db, id=invoice_id)
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if invoice can be deleted (only in draft status)
    if invoice.status != "draft":
        return error_response(
            message=f"Only draft invoices can be deleted. Current status: {invoice.status}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    await invoice_crud.delete(db, id=invoice_id)
    return success_response(
        message="Invoice deleted successfully",
    )

@router.post("/{invoice_id}/submit", response_model=InvoiceResponse)
async def submit_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_id: UUID,
) -> Any:
    """
    Submit an invoice for approval.
    """
    invoice = await invoice_crud.get(db, id=invoice_id)
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if invoice can be submitted
    if invoice.status != "draft":
        return error_response(
            message=f"Only draft invoices can be submitted. Current status: {invoice.status}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    # Submit invoice
    invoice = await invoice_crud.submit(db, db_obj=invoice)
    return success_response(
        data=invoice,
        message="Invoice submitted for approval",
    )

@router.post("/{invoice_id}/approve", response_model=InvoiceResponse)
async def approve_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_id: UUID,
    approval_data: InvoiceApprovalRequest = Body(...),
) -> Any:
    """
    Approve an invoice.
    """
    invoice = await invoice_crud.get(db, id=invoice_id)
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if invoice can be approved
    if invoice.status != "pending":
        return error_response(
            message=f"Only pending invoices can be approved. Current status: {invoice.status}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    # Approve invoice
    invoice = await invoice_crud.approve(
        db, 
        db_obj=invoice, 
        approved_by_id=approval_data.approved_by_id,
        notes=approval_data.notes
    )
    return success_response(
        data=invoice,
        message="Invoice approved successfully",
    )

@router.post("/{invoice_id}/reject", response_model=InvoiceResponse)
async def reject_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_id: UUID,
    approval_data: InvoiceApprovalRequest = Body(...),
) -> Any:
    """
    Reject an invoice.
    """
    invoice = await invoice_crud.get(db, id=invoice_id)
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if invoice can be rejected
    if invoice.status != "pending":
        return error_response(
            message=f"Only pending invoices can be rejected. Current status: {invoice.status}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    # Reject invoice
    invoice = await invoice_crud.reject(
        db, 
        db_obj=invoice, 
        rejected_by_id=approval_data.approved_by_id,
        notes=approval_data.notes
    )
    return success_response(
        data=invoice,
        message="Invoice rejected",
    )

@router.post("/{invoice_id}/void", response_model=InvoiceResponse)
async def void_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_id: UUID,
    reason: str = Body(..., embed=True),
) -> Any:
    """
    Void an invoice.
    """
    invoice = await invoice_crud.get(db, id=invoice_id)
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if invoice can be voided (not paid or already voided)
    if invoice.status in ["paid", "voided", "cancelled"]:
        return error_response(
            message=f"Invoice in '{invoice.status}' status cannot be voided",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    # Void invoice
    invoice = await invoice_crud.void(db, db_obj=invoice, reason=reason)
    return success_response(
        data=invoice,
        message="Invoice voided successfully",
    )