from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.customer import Customer, ARInvoice, ARPayment
from typing import List
from uuid import uuid4

class ARService:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def get_customers(self) -> List[Customer]:
        result = await self.db.execute(
            select(Customer).where(Customer.tenant_id == self.tenant_id, Customer.is_active == True)
        )
        return result.scalars().all()
    
    async def create_customer(self, customer_data: dict) -> Customer:
        customer = Customer(
            tenant_id=self.tenant_id,
            customer_code=customer_data['customer_code'],
            customer_name=customer_data['customer_name'],
            contact_person=customer_data.get('contact_person'),
            email=customer_data.get('email'),
            phone=customer_data.get('phone'),
            address=customer_data.get('address'),
            credit_limit=customer_data.get('credit_limit', 0)
        )
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer
    
    async def create_invoice(self, invoice_data: dict) -> ARInvoice:
        invoice = ARInvoice(
            tenant_id=self.tenant_id,
            customer_id=invoice_data['customer_id'],
            invoice_number=invoice_data['invoice_number'],
            invoice_date=invoice_data['invoice_date'],
            due_date=invoice_data.get('due_date'),
            total_amount=invoice_data['total_amount'],
            description=invoice_data.get('description')
        )
        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice
    
    async def create_payment(self, payment_data: dict) -> ARPayment:
        payment = ARPayment(
            tenant_id=self.tenant_id,
            customer_id=payment_data['customer_id'],
            payment_number=f"REC-{uuid4().hex[:8].upper()}",
            payment_date=payment_data['payment_date'],
            amount=payment_data['amount'],
            payment_method=payment_data.get('payment_method', 'Check'),
            reference=payment_data.get('reference')
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment