from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

class InvoiceService:
    """Service for invoice processing operations"""
    
    async def create_invoice(self, db: AsyncSession, invoice_data: dict):
        """Create a new invoice"""
        invoice = {
            "id": 1,
            "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d')}-001",
            "customer_id": invoice_data.get("customer_id"),
            "amount": invoice_data.get("amount"),
            "due_date": invoice_data.get("due_date"),
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        return invoice
    
    async def get_invoices(self, db: AsyncSession, skip: int = 0, limit: int = 100, status: Optional[str] = None):
        """Get invoices with filtering"""
        invoices = [
            {
                "id": 1,
                "invoice_number": "INV-20240101-001",
                "customer_id": 1,
                "customer_name": "ABC Corporation",
                "amount": 2500.00,
                "due_date": "2024-02-01",
                "status": "sent"
            }
        ]
        
        if status:
            invoices = [i for i in invoices if i["status"] == status]
            
        return invoices[skip:skip+limit]
    
    async def create_recurring_invoice(self, db: AsyncSession, recurring_data: dict):
        """Create recurring invoice"""
        return {
            "recurring_id": 1,
            "customer_id": recurring_data.get("customer_id"),
            "frequency": recurring_data.get("frequency"),
            "amount": recurring_data.get("amount"),
            "next_invoice_date": recurring_data.get("next_date"),
            "status": "active"
        }