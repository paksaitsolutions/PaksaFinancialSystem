from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Customer, ARInvoice, ARPayment, JournalEntry, JournalEntryLine, ChartOfAccounts
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
            company_id=self.tenant_id,
            customer_id=invoice_data['customer_id'],
            invoice_number=invoice_data['invoice_number'],
            invoice_date=invoice_data['invoice_date'],
            due_date=invoice_data.get('due_date'),
            total_amount=invoice_data['total_amount']
        )
        self.db.add(invoice)
        await self.db.flush()
        
        # Auto-generate GL journal entry
        await self._create_ar_invoice_journal_entry(invoice, invoice_data)
        
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice
    
    async def _create_ar_invoice_journal_entry(self, invoice: ARInvoice, invoice_data: dict):
        """Create journal entry for AR invoice: Dr. Accounts Receivable, Cr. Revenue"""
        journal_entry = JournalEntry(
            company_id=self.tenant_id,
            entry_number=f"AR-{invoice.invoice_number}",
            entry_date=invoice.invoice_date,
            description=f"AR Invoice {invoice.invoice_number}",
            total_debit=invoice.total_amount,
            total_credit=invoice.total_amount,
            status='posted',
            source_module='AR'
        )
        self.db.add(journal_entry)
        await self.db.flush()
        
        # Debit accounts receivable
        ar_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=invoice_data.get('ar_account_id'),
            description=f"Accounts Receivable - {invoice.invoice_number}",
            debit_amount=invoice.total_amount,
            credit_amount=0,
            line_number=1
        )
        
        # Credit revenue account
        revenue_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=invoice_data.get('revenue_account_id'),
            description=f"Revenue - {invoice.invoice_number}",
            debit_amount=0,
            credit_amount=invoice.total_amount,
            line_number=2
        )
        
        self.db.add(ar_line)
        self.db.add(revenue_line)
    
    async def create_payment(self, payment_data: dict) -> ARPayment:
        payment = ARPayment(
            company_id=self.tenant_id,
            customer_id=payment_data['customer_id'],
            payment_number=f"REC-{uuid4().hex[:8].upper()}",
            payment_date=payment_data['payment_date'],
            amount=payment_data['amount'],
            payment_method=payment_data.get('payment_method', 'CHECK'),
            reference=payment_data.get('reference')
        )
        self.db.add(payment)
        await self.db.flush()
        
        # Auto-generate GL journal entry
        await self._create_ar_payment_journal_entry(payment, payment_data)
        
        await self.db.commit()
        await self.db.refresh(payment)
        return payment
    
    async def _create_ar_payment_journal_entry(self, payment: ARPayment, payment_data: dict):
        """Create journal entry for AR payment: Dr. Cash, Cr. Accounts Receivable"""
        journal_entry = JournalEntry(
            company_id=self.tenant_id,
            entry_number=f"REC-{payment.payment_number}",
            entry_date=payment.payment_date,
            description=f"AR Payment {payment.payment_number}",
            total_debit=payment.amount,
            total_credit=payment.amount,
            status='posted',
            source_module='AR'
        )
        self.db.add(journal_entry)
        await self.db.flush()
        
        # Debit cash account
        cash_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=payment_data.get('cash_account_id'),
            description=f"Cash Receipt - {payment.payment_number}",
            debit_amount=payment.amount,
            credit_amount=0,
            line_number=1
        )
        
        # Credit accounts receivable
        ar_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=payment_data.get('ar_account_id'),
            description=f"Accounts Receivable - {payment.payment_number}",
            debit_amount=0,
            credit_amount=payment.amount,
            line_number=2
        )
        
        self.db.add(cash_line)
        self.db.add(ar_line)