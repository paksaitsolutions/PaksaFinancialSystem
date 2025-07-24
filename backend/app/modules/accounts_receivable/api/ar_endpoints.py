from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db
from ..services.customer_service import CustomerService
from ..services.invoice_service import InvoiceService
from ..schemas.customer import Customer, CustomerCreate, CustomerUpdate
from ..schemas.invoice import Invoice, InvoiceCreate
from ..schemas.payment import Payment, PaymentCreate

router = APIRouter()

customer_service = CustomerService()
invoice_service = InvoiceService()

@router.post("/customers/", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate):
    return customer_service.create_customer(customer)

@router.get("/customers/", response_model=List[Customer])
async def get_customers(skip: int = 0, limit: int = 100):
    return customer_service.list_customers(skip, limit)

@router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer: CustomerUpdate):
    updated = customer_service.update_customer(customer_id, customer)
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated

@router.post("/invoices/", response_model=Invoice, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice: InvoiceCreate):
    return invoice_service.create_invoice(invoice)

@router.get("/invoices/", response_model=List[Invoice])
async def get_invoices(customer_id: str = None):
    return invoice_service.list_invoices(customer_id)

@router.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    invoice = invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice