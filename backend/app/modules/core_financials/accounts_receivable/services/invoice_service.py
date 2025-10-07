from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import uuid4
from ..models import Invoice, InvoiceItem, Customer, Payment

class InvoiceService:
    """Service for invoice processing operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_invoice(self, invoice_data: dict, user_id: str):
        """Create a new invoice with real database persistence"""
        # Generate unique invoice number
        invoice_count = await self.db.scalar(select(func.count(Invoice.id)))
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{invoice_count + 1:05d}"
        
        # Calculate due date based on payment terms
        if isinstance(invoice_data.get("issue_date"), str):
            issue_date = datetime.strptime(invoice_data["issue_date"], "%Y-%m-%d").date()
        else:
            issue_date = invoice_data.get("issue_date", date.today())
            
        if isinstance(invoice_data.get("due_date"), str):
            due_date = datetime.strptime(invoice_data["due_date"], "%Y-%m-%d").date()
        else:
            due_date = invoice_data.get("due_date", issue_date + timedelta(days=30))
        
        # Create invoice
        invoice = Invoice(
            id=uuid4(),
            invoice_number=invoice_number,
            customer_id=invoice_data["customer_id"],
            issue_date=issue_date,
            due_date=due_date,
            po_number=invoice_data.get("po_number"),
            terms=invoice_data.get("terms"),
            notes=invoice_data.get("notes"),
            subtotal=Decimal(str(invoice_data.get("subtotal", 0))),
            tax_amount=Decimal(str(invoice_data.get("tax_amount", 0))),
            discount_amount=Decimal(str(invoice_data.get("discount_amount", 0))),
            total_amount=Decimal(str(invoice_data.get("total_amount", 0))),
            balance_due=Decimal(str(invoice_data.get("total_amount", 0))),
            created_by_id=user_id,
            updated_by_id=user_id
        )
        
        self.db.add(invoice)
        await self.db.flush()  # Get the invoice ID
        
        # Create line items if provided
        if invoice_data.get("items"):
            for item_data in invoice_data["items"]:
                line_item = InvoiceItem(
                    id=uuid4(),
                    invoice_id=invoice.id,
                    description=item_data["description"],
                    quantity=Decimal(str(item_data.get("quantity", 1))),
                    unit_price=Decimal(str(item_data["unit_price"])),
                    discount_percent=Decimal(str(item_data.get("discount_percent", 0))),
                    tax_rate=Decimal(str(item_data.get("tax_rate", 0)))
                )
                self.db.add(line_item)
        
        await self.db.commit()
        await self.db.refresh(invoice)
        return await self.get_invoice(invoice.id)
    
    async def get_invoices(self, skip: int = 0, limit: int = 100,
                          status: Optional[str] = None, customer_id: Optional[int] = None):
        """Get invoices with real database filtering"""
        query = select(Invoice).options(
            selectinload(Invoice.invoice_items)
        )
        
        # Apply filters
        if status:
            query = query.where(Invoice.status == status)
        if customer_id:
            query = query.where(Invoice.customer_id == customer_id)
            
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(desc(Invoice.issue_date))
        
        result = await self.db.execute(query)
        invoices = result.scalars().all()
        
        return [
            {
                "id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "customer_id": inv.customer_id,
                "issue_date": inv.issue_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "total_amount": float(inv.total_amount),
                "balance_due": float(inv.balance_due),
                "status": inv.status.value,
                "days_overdue": inv.days_overdue
            }
            for inv in invoices
        ]
    
    async def get_invoice(self, invoice_id):
        """Get invoice by ID with complete details"""
        query = select(Invoice).options(
            selectinload(Invoice.invoice_items),
            selectinload(Invoice.payments)
        ).where(Invoice.id == invoice_id)
        
        result = await self.db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
            
        return {
            "id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "customer_id": invoice.customer_id,
            "issue_date": invoice.issue_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "po_number": invoice.po_number,
            "terms": invoice.terms,
            "subtotal": float(invoice.subtotal),
            "tax_amount": float(invoice.tax_amount),
            "discount_amount": float(invoice.discount_amount),
            "total_amount": float(invoice.total_amount),
            "amount_paid": float(invoice.amount_paid),
            "balance_due": float(invoice.balance_due),
            "status": invoice.status.value,
            "days_overdue": invoice.days_overdue,
            "notes": invoice.notes,
            "items": [
                {
                    "id": str(item.id),
                    "description": item.description,
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "discount_percent": float(item.discount_percent),
                    "tax_rate": float(item.tax_rate),
                    "subtotal": float(item.subtotal),
                    "total_amount": float(item.total_amount)
                }
                for item in invoice.invoice_items
            ],
            "created_at": invoice.created_at.isoformat() if invoice.created_at else None
        }
    
    async def update_invoice(self, invoice_id, invoice_data: dict, user_id: str):
        """Update an existing invoice"""
        query = select(Invoice).where(Invoice.id == invoice_id)
        result = await self.db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
            
        # Update fields
        for field, value in invoice_data.items():
            if hasattr(invoice, field) and value is not None:
                if field in ["subtotal", "tax_amount", "discount_amount", "total_amount", "balance_due"]:
                    setattr(invoice, field, Decimal(str(value)))
                elif field in ["issue_date", "due_date"] and isinstance(value, str):
                    setattr(invoice, field, datetime.strptime(value, "%Y-%m-%d").date())
                else:
                    setattr(invoice, field, value)
                    
        invoice.updated_by_id = user_id
        invoice.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(invoice)
        return await self.get_invoice(invoice_id)
    
    async def void_invoice(self, invoice_id, void_data: dict, user_id: str):
        """Void an invoice"""
        query = select(Invoice).where(Invoice.id == invoice_id)
        result = await self.db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
            
        if invoice.amount_paid > 0:
            return {"error": "Cannot void invoice with payments applied"}
            
        from ..models import InvoiceStatus
        invoice.status = InvoiceStatus.VOID
        invoice.balance_due = Decimal('0')
        invoice.updated_by_id = user_id
        invoice.updated_at = datetime.utcnow()
        
        # Add void reason to notes
        void_note = f"Invoice voided on {datetime.now().strftime('%Y-%m-%d')}"
        if void_data.get("reason"):
            void_note += f": {void_data['reason']}"
            
        if invoice.notes:
            invoice.notes += f"\n{void_note}"
        else:
            invoice.notes = void_note
            
        await self.db.commit()
        
        return {
            "invoice_id": str(invoice_id),
            "status": "void",
            "voided_by": user_id,
            "reason": void_data.get("reason")
        }