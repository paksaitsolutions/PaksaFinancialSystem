from fastapi import APIRouter, Depends
from .services import CashManagementService
from .schemas import BankAccountSchema, CashTransactionSchema
from typing import List

router = APIRouter()

def get_service():
    # Placeholder for dependency injection
    pass

@router.get('/bank-accounts', response_model=List[BankAccountSchema])
def list_bank_accounts(service: CashManagementService = Depends(get_service)):
    return service.get_bank_accounts()

@router.get('/cash-transactions', response_model=List[CashTransactionSchema])
def list_cash_transactions(service: CashManagementService = Depends(get_service)):
    return service.get_cash_transactions()
