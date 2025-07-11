import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from .. import schemas, services
from ..exceptions import AccountsPayableException

# Routers for each resource
router_vendors = APIRouter()
router_bills = APIRouter()
router_payments = APIRouter()

# --- Dependencies ---
def get_vendor_service(db: AsyncSession = Depends(get_async_db)) -> services.VendorService:
    return services.VendorService(db)

def get_bill_service(db: AsyncSession = Depends(get_async_db)) -> services.BillService:
    return services.BillService(db)

def get_payment_service(db: AsyncSession = Depends(get_async_db)) -> services.PaymentService:
    return services.PaymentService(db)

# --- Vendor Endpoints ---
@router_vendors.post("/", response_model=schemas.Vendor, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_in: schemas.VendorCreate,
    service: services.VendorService = Depends(get_vendor_service),
):
    return await service.create_vendor(vendor_in)

@router_vendors.get("/{vendor_id}", response_model=schemas.Vendor)
async def get_vendor(
    vendor_id: uuid.UUID,
    service: services.VendorService = Depends(get_vendor_service),
):
    try:
        return await service.get_vendor_by_id(vendor_id)
    except AccountsPayableException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Bill Endpoints ---
@router_bills.post("/", response_model=schemas.Bill, status_code=status.HTTP_201_CREATED)
async def create_bill(
    bill_in: schemas.BillCreate,
    service: services.BillService = Depends(get_bill_service),
):
    try:
        return await service.create_bill(bill_in)
    except AccountsPayableException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router_bills.get("/{bill_id}", response_model=schemas.Bill)
async def get_bill(
    bill_id: uuid.UUID,
    service: services.BillService = Depends(get_bill_service),
):
    try:
        return await service.get_bill_by_id(bill_id)
    except AccountsPayableException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Bill List, Update, Delete ---
@router_bills.get("/", response_model=List[schemas.Bill])
async def list_bills(
    skip: int = 0,
    limit: int = 100,
    service: services.BillService = Depends(get_bill_service)
):
    return await service.list_bills(skip=skip, limit=limit)

@router_bills.put("/{bill_id}", response_model=schemas.Bill)
async def update_bill(
    bill_id: uuid.UUID,
    bill_update: schemas.BillUpdate,
    service: services.BillService = Depends(get_bill_service)
):
    try:
        return await service.update_bill(bill_id, bill_update)
    except AccountsPayableException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router_bills.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill(
    bill_id: uuid.UUID,
    service: services.BillService = Depends(get_bill_service)
):
    try:
        await service.delete_bill(bill_id)
    except AccountsPayableException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router_bills.post("/three-way-match", response_model=schemas.ThreeWayMatchResult)
async def three_way_match(
    match_request: schemas.ThreeWayMatchRequest,
    service: services.BillService = Depends(get_bill_service),
):
    """Validate three-way match for bill, purchase order, and receipt."""
    return await service.validate_three_way_match(
        match_request.bill_id,
        match_request.purchase_order_id,
        match_request.receipt_id
    )

# --- Payment Endpoints ---
@router_payments.post("/", response_model=schemas.Payment, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_in: schemas.PaymentCreate,
    service: services.PaymentService = Depends(get_payment_service),
):
    try:
        return await service.create_payment(payment_in)
    except AccountsPayableException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- Payment List, Update, Delete ---
@router_payments.get("/", response_model=List[schemas.Payment])
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    service: services.PaymentService = Depends(get_payment_service)
):
    return await service.list_payments(skip=skip, limit=limit)

@router_payments.put("/{payment_id}", response_model=schemas.Payment)
async def update_payment(
    payment_id: uuid.UUID,
    payment_update: schemas.PaymentUpdate,
    service: services.PaymentService = Depends(get_payment_service)
):
    try:
        return await service.update_payment(payment_id, payment_update)
    except AccountsPayableException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router_payments.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: uuid.UUID,
    service: services.PaymentService = Depends(get_payment_service)
):
    try:
        await service.delete_payment(payment_id)
    except AccountsPayableException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router_bills.get("/reporting", response_model=schemas.APReport)
async def get_ap_report(db: AsyncSession = Depends(get_async_db)):
    # Stub: Implement AP reporting logic
    return schemas.APReport(summary={"total_bills": 120, "total_paid": 90000})
