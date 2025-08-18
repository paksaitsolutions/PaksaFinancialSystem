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
