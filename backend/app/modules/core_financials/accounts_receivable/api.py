from fastapi import APIRouter, Depends
from .services import AccountsReceivableService
from .schemas import CustomerSchema, ARInvoiceSchema
from typing import List

router = APIRouter()

def get_service():
    """Get AR service instance."""
    raise NotImplementedError("AR service dependency injection not implemented yet")

@router.get('/customers', response_model=List[CustomerSchema])
def list_customers(service: AccountsReceivableService = Depends(get_service)):
    return service.get_customers()

@router.get('/invoices', response_model=List[ARInvoiceSchema])
def list_invoices(service: AccountsReceivableService = Depends(get_service)):
    return service.get_invoices()
