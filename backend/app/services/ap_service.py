from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.vendor import MainVendor as Vendor, APInvoice, APPayment
from typing import List
from uuid import uuid4

class APService:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def get_vendors(self) -> List[Vendor]:
        result = await self.db.execute(
            select(Vendor).where(Vendor.tenant_id == self.tenant_id, Vendor.is_active == True)
        )
        return result.scalars().all()
    
    async def create_vendor(self, vendor_data: dict) -> Vendor:
        vendor = Vendor(
            tenant_id=self.tenant_id,
            vendor_code=vendor_data['vendor_code'],
            vendor_name=vendor_data['vendor_name'],
            contact_person=vendor_data.get('contact_person'),
            email=vendor_data.get('email'),
            phone=vendor_data.get('phone'),
            address=vendor_data.get('address'),
            payment_terms=vendor_data.get('payment_terms', 'Net 30')
        )
        self.db.add(vendor)
        await self.db.commit()
        await self.db.refresh(vendor)
        return vendor
    
    async def create_invoice(self, invoice_data: dict) -> APInvoice:
        invoice = APInvoice(
            tenant_id=self.tenant_id,
            vendor_id=invoice_data['vendor_id'],
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
    
    async def create_payment(self, payment_data: dict) -> APPayment:
        payment = APPayment(
            tenant_id=self.tenant_id,
            vendor_id=payment_data['vendor_id'],
            payment_number=f"PAY-{uuid4().hex[:8].upper()}",
            payment_date=payment_data['payment_date'],
            amount=payment_data['amount'],
            payment_method=payment_data.get('payment_method', 'Check'),
            reference=payment_data.get('reference')
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment