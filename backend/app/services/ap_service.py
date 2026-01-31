from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.models import Vendor, APInvoice, APPayment, JournalEntry, JournalEntryLine, ChartOfAccounts


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
            company_id=self.tenant_id,
            vendor_id=invoice_data['vendor_id'],
            invoice_number=invoice_data['invoice_number'],
            invoice_date=invoice_data['invoice_date'],
            due_date=invoice_data.get('due_date'),
            total_amount=invoice_data['total_amount']
        )
        self.db.add(invoice)
        await self.db.flush()
        
        # Auto-generate GL journal entry
        await self._create_ap_invoice_journal_entry(invoice, invoice_data)
        
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice
    
    async def _create_ap_invoice_journal_entry(self, invoice: APInvoice, invoice_data: dict):
        journal_entry = JournalEntry(
            company_id=self.tenant_id,
            entry_number=f"AP-{invoice.invoice_number}",
            entry_date=invoice.invoice_date,
            description=f"AP Invoice {invoice.invoice_number}",
            total_debit=invoice.total_amount,
            total_credit=invoice.total_amount,
            status='posted',
            source_module='AP'
        )
        self.db.add(journal_entry)
        await self.db.flush()
        
        # Debit expense account
        expense_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=invoice_data.get('expense_account_id'),
            description=f"Expense - {invoice.invoice_number}",
            debit_amount=invoice.total_amount,
            credit_amount=0,
            line_number=1
        )
        
        # Credit accounts payable
        ap_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=invoice_data.get('ap_account_id'),
            description=f"Accounts Payable - {invoice.invoice_number}",
            debit_amount=0,
            credit_amount=invoice.total_amount,
            line_number=2
        )
        
        self.db.add(expense_line)
        self.db.add(ap_line)
    
    async def create_payment(self, payment_data: dict) -> APPayment:
        payment = APPayment(
            company_id=self.tenant_id,
            vendor_id=payment_data['vendor_id'],
            payment_number=f"PAY-{uuid4().hex[:8].upper()}",
            payment_date=payment_data['payment_date'],
            amount=payment_data['amount'],
            payment_method=payment_data.get('payment_method', 'CHECK'),
            reference=payment_data.get('reference')
        )
        self.db.add(payment)
        await self.db.flush()
        
        # Auto-generate GL journal entry
        await self._create_ap_payment_journal_entry(payment, payment_data)
        
        await self.db.commit()
        await self.db.refresh(payment)
        return payment
    
    async def _create_ap_payment_journal_entry(self, payment: APPayment, payment_data: dict):
        journal_entry = JournalEntry(
            company_id=self.tenant_id,
            entry_number=f"PAY-{payment.payment_number}",
            entry_date=payment.payment_date,
            description=f"AP Payment {payment.payment_number}",
            total_debit=payment.amount,
            total_credit=payment.amount,
            status='posted',
            source_module='AP'
        )
        self.db.add(journal_entry)
        await self.db.flush()
        
        # Debit accounts payable
        ap_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=payment_data.get('ap_account_id'),
            description=f"Accounts Payable - {payment.payment_number}",
            debit_amount=payment.amount,
            credit_amount=0,
            line_number=1
        )
        
        # Credit cash account
        cash_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=payment_data.get('cash_account_id'),
            description=f"Cash Payment - {payment.payment_number}",
            debit_amount=0,
            credit_amount=payment.amount,
            line_number=2
        )
        
        self.db.add(ap_line)
        self.db.add(cash_line)