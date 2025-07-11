from fastapi import APIRouter, Depends
from .services import AccountsPayableService
from .schemas import VendorSchema, InvoiceSchema
from typing import List

router = APIRouter()

def get_service():
    # Placeholder for dependency injection
    pass

@router.get('/vendors', response_model=List[VendorSchema])
def list_vendors(service: AccountsPayableService = Depends(get_service)):
    return service.get_vendors()

@router.get('/invoices', response_model=List[InvoiceSchema])
def list_invoices(service: AccountsPayableService = Depends(get_service)):
    return service.get_invoices()
