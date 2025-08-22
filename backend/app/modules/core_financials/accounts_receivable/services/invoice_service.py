from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from decimal import Decimal
from ..models import ARInvoice, ARInvoiceLineItem, Customer, ARPayment, ARPaymentInvoice

class InvoiceService:
    """Service for invoice processing operations"""
    
    async def create_invoice(self, db: AsyncSession, invoice_data: dict, user_id: int):
        """Create a new invoice with real database persistence"""
        # Generate unique invoice number
        invoice_count = await db.scalar(select(func.count(ARInvoice.id)))
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{invoice_count + 1:05d}"
        
        # Calculate due date based on payment terms
        invoice_date = datetime.strptime(invoice_data["invoice_date"], "%Y-%m-%d").date()
        terms = invoice_data.get("terms", "NET30")
        if terms == "NET30":
            due_date = invoice_date + timedelta(days=30)
        elif terms == "NET15":
            due_date = invoice_date + timedelta(days=15)
        elif terms == "NET60":
            due_date = invoice_date + timedelta(days=60)
        else:
            due_date = invoice_date + timedelta(days=30)
        
        # Create invoice
        invoice = ARInvoice(
            invoice_number=invoice_number,
            customer_id=invoice_data["customer_id"],
            invoice_date=invoice_date,
            due_date=due_date,
            terms=terms,
            po_number=invoice_data.get("po_number"),
            subtotal=Decimal(str(invoice_data.get("subtotal", 0))),
            tax_amount=Decimal(str(invoice_data.get("tax_amount", 0))),
            discount_amount=Decimal(str(invoice_data.get("discount_amount", 0))),
            total_amount=Decimal(str(invoice_data.get("total_amount", 0))),
            balance_due=Decimal(str(invoice_data.get("total_amount", 0))),
            status="draft",
            notes=invoice_data.get("notes"),
            is_recurring=invoice_data.get("is_recurring", False),
            recurring_frequency=invoice_data.get("recurring_frequency"),
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(invoice)
        await db.flush()  # Get the invoice ID
        
        # Create line items
        if invoice_data.get("line_items"):
            for i, line_data in enumerate(invoice_data["line_items"]):
                line_item = ARInvoiceLineItem(
                    invoice_id=invoice.id,
                    line_number=i + 1,
                    item_code=line_data.get("item_code"),
                    description=line_data["description"],
                    quantity=Decimal(str(line_data.get("quantity", 1))),
                    unit_price=Decimal(str(line_data["unit_price"])),
                    line_total=Decimal(str(line_data["line_total"])),
                    tax_amount=Decimal(str(line_data.get("tax_amount", 0))),
                    revenue_account_id=line_data.get("revenue_account_id")
                )
                db.add(line_item)
        
        await db.commit()
        await db.refresh(invoice)
        return await self.get_invoice(db, invoice.id)
    
    async def get_invoices(self, db: AsyncSession, skip: int = 0, limit: int = 100,
                          status: Optional[str] = None, customer_id: Optional[int] = None):
        """Get invoices with real database filtering"""
        query = select(ARInvoice).options(
            selectinload(ARInvoice.customer),
            selectinload(ARInvoice.line_items)
        )
        
        # Apply filters
        if status:
            query = query.where(ARInvoice.status == status)
        if customer_id:
            query = query.where(ARInvoice.customer_id == customer_id)
            
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(desc(ARInvoice.invoice_date))
        
        result = await db.execute(query)
        invoices = result.scalars().all()
        
        return [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "customer_name": inv.customer.name,
                "invoice_date": inv.invoice_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "total_amount": float(inv.total_amount),
                "balance_due": float(inv.balance_due),
                "status": inv.status,
                "days_overdue": inv.days_overdue
            }
            for inv in invoices
        ]
    
    async def get_invoice(self, db: AsyncSession, invoice_id: int):
        """Get invoice by ID with complete details"""
        query = select(ARInvoice).options(
            selectinload(ARInvoice.customer),
            selectinload(ARInvoice.line_items),
            selectinload(ARInvoice.payments)
        ).where(ARInvoice.id == invoice_id)
        
        result = await db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
            
        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "customer_id": invoice.customer_id,
            "customer_name": invoice.customer.name,
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "terms": invoice.terms,
            "po_number": invoice.po_number,
            "subtotal": float(invoice.subtotal),
            "tax_amount": float(invoice.tax_amount),
            "discount_amount": float(invoice.discount_amount),
            "total_amount": float(invoice.total_amount),
            "paid_amount": float(invoice.paid_amount),
            "balance_due": float(invoice.balance_due),
            "status": invoice.status,
            "days_overdue": invoice.days_overdue,
            "notes": invoice.notes,
            "is_recurring": invoice.is_recurring,
            "recurring_frequency": invoice.recurring_frequency,
            "line_items": [
                {
                    "id": line.id,
                    "line_number": line.line_number,
                    "description": line.description,
                    "quantity": float(line.quantity),
                    "unit_price": float(line.unit_price),
                    "line_total": float(line.line_total)
                }
                for line in invoice.line_items
            ],
            "created_at": invoice.created_at.isoformat() if invoice.created_at else None
        }
    
    async def send_invoice(self, db: AsyncSession, invoice_id: int, send_data: dict, user_id: int):
        """Send invoice to customer"""
        query = select(ARInvoice).where(ARInvoice.id == invoice_id)
        result = await db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
            
        invoice.status = "sent"
        invoice.sent_date = datetime.utcnow()
        invoice.updated_by = user_id
        invoice.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # In real implementation, this would trigger email sending
        return {
            "invoice_id": invoice_id,
            "status": "sent",
            "sent_date": invoice.sent_date.isoformat(),
            "recipient": send_data.get("email"),
            "sent_by": user_id
        }
    
    async def record_payment(self, db: AsyncSession, invoice_id: int, payment_data: dict, user_id: int):
        """Record payment against invoice"""
        query = select(ARInvoice).where(ARInvoice.id == invoice_id)
        result = await db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
        
        # Generate payment number
        payment_count = await db.scalar(select(func.count(ARPayment.id)))
        payment_number = f"PMT-{datetime.now().strftime('%Y%m%d')}-{payment_count + 1:04d}"
        
        # Create payment record
        payment = ARPayment(
            payment_number=payment_number,
            customer_id=invoice.customer_id,
            payment_date=datetime.strptime(payment_data["payment_date"], "%Y-%m-%d").date(),
            payment_method=payment_data.get("payment_method", "check"),
            reference_number=payment_data.get("reference_number"),
            amount=Decimal(str(payment_data["amount"])),
            status="processed",
            processed_date=datetime.utcnow(),
            notes=payment_data.get("notes"),
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(payment)
        await db.flush()
        
        # Apply payment to invoice
        amount_applied = min(Decimal(str(payment_data["amount"])), invoice.balance_due)
        
        payment_invoice = ARPaymentInvoice(
            payment_id=payment.id,
            invoice_id=invoice_id,
            amount_applied=amount_applied
        )
        db.add(payment_invoice)
        
        # Update invoice amounts
        invoice.paid_amount += amount_applied
        invoice.balance_due = invoice.total_amount - invoice.paid_amount
        
        # Update invoice status
        if invoice.balance_due <= 0:
            invoice.status = "paid"
        elif invoice.paid_amount > 0:
            invoice.status = "partially_paid"
        
        await db.commit()
        
        return {
            "payment_id": payment.id,
            "payment_number": payment.payment_number,
            "amount_applied": float(amount_applied),
            "invoice_balance": float(invoice.balance_due),
            "invoice_status": invoice.status
        }
    
    async def create_recurring_invoices(self, db: AsyncSession, user_id: int):
        """Create recurring invoices that are due"""
        today = date.today()
        
        # Find recurring invoices due for generation
        query = select(ARInvoice).options(
            selectinload(ARInvoice.customer),
            selectinload(ARInvoice.line_items)
        ).where(
            ARInvoice.is_recurring == True,
            ARInvoice.next_invoice_date <= today,
            ARInvoice.status != "cancelled"
        )
        
        result = await db.execute(query)
        recurring_invoices = result.scalars().all()
        
        created_invoices = []
        
        for template_invoice in recurring_invoices:
            # Calculate next invoice date
            if template_invoice.recurring_frequency == "monthly":
                next_date = today + timedelta(days=30)
            elif template_invoice.recurring_frequency == "quarterly":
                next_date = today + timedelta(days=90)
            elif template_invoice.recurring_frequency == "annually":
                next_date = today + timedelta(days=365)
            else:
                next_date = today + timedelta(days=30)
            
            # Create new invoice data
            invoice_data = {
                "customer_id": template_invoice.customer_id,
                "invoice_date": today.isoformat(),
                "terms": template_invoice.terms,
                "subtotal": float(template_invoice.subtotal),
                "tax_amount": float(template_invoice.tax_amount),
                "total_amount": float(template_invoice.total_amount),
                "notes": f"Recurring invoice based on {template_invoice.invoice_number}",
                "line_items": [
                    {
                        "description": line.description,
                        "quantity": float(line.quantity),
                        "unit_price": float(line.unit_price),
                        "line_total": float(line.line_total)
                    }
                    for line in template_invoice.line_items
                ]
            }
            
            # Create new invoice
            new_invoice = await self.create_invoice(db, invoice_data, user_id)
            created_invoices.append(new_invoice)
            
            # Update template invoice next date
            template_invoice.next_invoice_date = next_date
            template_invoice.updated_by = user_id
            template_invoice.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "created_count": len(created_invoices),
            "invoices": created_invoices
        }
    
    async def void_invoice(self, db: AsyncSession, invoice_id: int, void_data: dict, user_id: int):
        """Void an invoice"""
        query = select(ARInvoice).where(ARInvoice.id == invoice_id)
        result = await db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
            
        if invoice.paid_amount > 0:
            return {"error": "Cannot void invoice with payments applied"}
            
        invoice.status = "void"
        invoice.balance_due = Decimal('0')
        invoice.updated_by = user_id
        invoice.updated_at = datetime.utcnow()
        
        # Add void reason to notes
        void_note = f"Invoice voided on {datetime.now().strftime('%Y-%m-%d')}"
        if void_data.get("reason"):
            void_note += f": {void_data['reason']}"
            
        if invoice.notes:
            invoice.notes += f"\n{void_note}"
        else:
            invoice.notes = void_note
            
        await db.commit()
        
        return {
            "invoice_id": invoice_id,
            "status": "void",
            "voided_by": user_id,
            "reason": void_data.get("reason")
        }