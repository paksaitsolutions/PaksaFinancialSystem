from typing import List, Optional
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import date
from ..schemas.invoice import Invoice, InvoiceCreate, InvoiceStatus

class InvoiceService:
    def __init__(self):
        self._invoices = {}
        self._next_number = 1000
    
    def create_invoice(self, invoice_data: InvoiceCreate) -> Invoice:
        invoice_id = uuid4()
        
        # Calculate totals
        subtotal = sum(item.amount for item in invoice_data.line_items)
        tax_amount = subtotal * Decimal("0.08")  # 8% tax
        total_amount = subtotal + tax_amount
        
        invoice = Invoice(
            id=invoice_id,
            invoice_number=f"INV-{self._next_number:04d}",
            status=InvoiceStatus.DRAFT,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            balance=total_amount,
            **invoice_data.dict()
        )
        
        self._invoices[invoice_id] = invoice
        self._next_number += 1
        return invoice
    
    def get_invoice(self, invoice_id: UUID) -> Optional[Invoice]:
        return self._invoices.get(invoice_id)
    
    def list_invoices(self, customer_id: Optional[UUID] = None) -> List[Invoice]:
        invoices = list(self._invoices.values())
        if customer_id:
            invoices = [inv for inv in invoices if inv.customer_id == customer_id]
        return invoices
    
    def update_invoice_status(self, invoice_id: UUID, status: InvoiceStatus) -> Optional[Invoice]:
        if invoice_id not in self._invoices:
            return None
        
        self._invoices[invoice_id].status = status
        return self._invoices[invoice_id]
    
    def apply_payment(self, invoice_id: UUID, amount: Decimal) -> Optional[Invoice]:
        if invoice_id not in self._invoices:
            return None
        
        invoice = self._invoices[invoice_id]
        invoice.paid_amount += amount
        invoice.balance = invoice.total_amount - invoice.paid_amount
        
        if invoice.balance <= 0:
            invoice.status = InvoiceStatus.PAID
        
        return invoice