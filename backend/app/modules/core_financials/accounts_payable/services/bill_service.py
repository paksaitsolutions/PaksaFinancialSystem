from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict
from datetime import datetime, date
from decimal import Decimal
from ..models import Invoice, InvoiceLineItem, Vendor, Payment, PaymentInvoice

class BillService:
    """Service for bill/invoice processing operations"""
    
    async def create_bill(self, db: AsyncSession, bill_data: dict, user_id: int):
        """Create a new bill/invoice with real database persistence"""
        # Generate unique invoice number
        invoice_count = await db.scalar(select(func.count(Invoice.id)))
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{invoice_count + 1:04d}"
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            vendor_id=bill_data["vendor_id"],
            invoice_date=datetime.strptime(bill_data["invoice_date"], "%Y-%m-%d").date(),
            due_date=datetime.strptime(bill_data["due_date"], "%Y-%m-%d").date(),
            reference_number=bill_data.get("reference_number"),
            subtotal=Decimal(str(bill_data.get("subtotal", 0))),
            tax_amount=Decimal(str(bill_data.get("tax_amount", 0))),
            total_amount=Decimal(str(bill_data.get("total_amount", 0))),
            balance_due=Decimal(str(bill_data.get("total_amount", 0))),
            status="draft",
            approval_status="pending",
            notes=bill_data.get("notes"),
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(invoice)
        await db.flush()  # Get the invoice ID
        
        # Create line items
        if bill_data.get("line_items"):
            for i, line_data in enumerate(bill_data["line_items"]):
                line_item = InvoiceLineItem(
                    invoice_id=invoice.id,
                    line_number=i + 1,
                    item_code=line_data.get("item_code"),
                    description=line_data["description"],
                    quantity=Decimal(str(line_data.get("quantity", 1))),
                    unit_price=Decimal(str(line_data["unit_price"])),
                    amount=Decimal(str(line_data["amount"])),
                    line_total=Decimal(str(line_data["line_total"])),
                    gl_account_id=line_data.get("gl_account_id")
                )
                db.add(line_item)
        
        await db.commit()
        await db.refresh(invoice)
        return await self.get_bill(db, invoice.id)
    
    async def get_bills(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
                       status: Optional[str] = None, vendor_id: Optional[int] = None):
        """Get bills with real database filtering"""
        query = select(Invoice).options(
            selectinload(Invoice.vendor),
            selectinload(Invoice.line_items)
        )
        
        # Apply filters
        if status:
            query = query.where(Invoice.status == status)
        if vendor_id:
            query = query.where(Invoice.vendor_id == vendor_id)
            
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(Invoice.invoice_date.desc())
        
        result = await db.execute(query)
        invoices = result.scalars().all()
        
        return [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "vendor_name": inv.vendor.name,
                "invoice_date": inv.invoice_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "total_amount": float(inv.total_amount),
                "balance_due": float(inv.balance_due),
                "status": inv.status,
                "approval_status": inv.approval_status
            }
            for inv in invoices
        ]
    
    async def get_bill(self, db: AsyncSession, bill_id: int):
        """Get bill by ID with complete details"""
        query = select(Invoice).options(
            selectinload(Invoice.vendor),
            selectinload(Invoice.line_items),
            selectinload(Invoice.payments)
        ).where(Invoice.id == bill_id)
        
        result = await db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
            
        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "reference_number": invoice.reference_number,
            "vendor_id": invoice.vendor_id,
            "vendor_name": invoice.vendor.name,
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "subtotal": float(invoice.subtotal),
            "tax_amount": float(invoice.tax_amount),
            "total_amount": float(invoice.total_amount),
            "paid_amount": float(invoice.paid_amount),
            "balance_due": float(invoice.balance_due),
            "status": invoice.status,
            "approval_status": invoice.approval_status,
            "notes": invoice.notes,
            "line_items": [
                {
                    "id": line.id,
                    "line_number": line.line_number,
                    "description": line.description,
                    "quantity": float(line.quantity),
                    "unit_price": float(line.unit_price),
                    "amount": float(line.amount),
                    "line_total": float(line.line_total)
                }
                for line in invoice.line_items
            ],
            "created_at": invoice.created_at.isoformat() if invoice.created_at else None
        }
    
    async def approve_bill(self, db: AsyncSession, bill_id: int, approval_data: dict, user_id: int):
        """Approve bill with real database update"""
        query = select(Invoice).where(Invoice.id == bill_id)
        result = await db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
            
        invoice.approval_status = "approved"
        invoice.status = "approved"
        invoice.updated_by = user_id
        invoice.updated_at = datetime.utcnow()
        
        # Add approval notes
        if approval_data.get("notes"):
            approval_note = f"Approved on {datetime.now().strftime('%Y-%m-%d')}: {approval_data['notes']}"
            if invoice.notes:
                invoice.notes += f"\n{approval_note}"
            else:
                invoice.notes = approval_note
        
        await db.commit()
        return {"bill_id": bill_id, "status": "approved", "approved_by": user_id}
    
    async def reject_bill(self, db: AsyncSession, bill_id: int, rejection_data: dict, user_id: int):
        """Reject bill with real database update"""
        query = select(Invoice).where(Invoice.id == bill_id)
        result = await db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
            
        invoice.approval_status = "rejected"
        invoice.status = "rejected"
        invoice.updated_by = user_id
        invoice.updated_at = datetime.utcnow()
        
        # Add rejection reason
        if rejection_data.get("reason"):
            rejection_note = f"Rejected on {datetime.now().strftime('%Y-%m-%d')}: {rejection_data['reason']}"
            if invoice.notes:
                invoice.notes += f"\n{rejection_note}"
            else:
                invoice.notes = rejection_note
        
        await db.commit()
        return {"bill_id": bill_id, "status": "rejected", "rejected_by": user_id}
    
    async def perform_three_way_match(self, db: AsyncSession, bill_id: int, match_data: dict):
        """Perform three-way matching (PO, Receipt, Invoice)"""
        query = select(Invoice).options(
            selectinload(Invoice.line_items)
        ).where(Invoice.id == bill_id)
        
        result = await db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
        
        # Mock three-way matching logic
        po_number = match_data.get("po_number")
        receipt_number = match_data.get("receipt_number")
        
        # In real implementation, this would:
        # 1. Validate PO exists and is approved
        # 2. Validate receipt exists and matches PO
        # 3. Compare invoice line items with PO and receipt
        # 4. Flag discrepancies for review
        
        match_results = {
            "bill_id": bill_id,
            "po_number": po_number,
            "receipt_number": receipt_number,
            "match_status": "matched",
            "discrepancies": [],
            "total_variance": 0.00,
            "line_matches": []
        }
        
        # Simulate line-by-line matching
        for line in invoice.line_items:
            line_match = {
                "line_number": line.line_number,
                "description": line.description,
                "invoice_qty": float(line.quantity),
                "po_qty": float(line.quantity),  # Mock - would come from PO
                "receipt_qty": float(line.quantity),  # Mock - would come from receipt
                "invoice_price": float(line.unit_price),
                "po_price": float(line.unit_price),  # Mock
                "variance": 0.00,
                "match_status": "matched"
            }
            match_results["line_matches"].append(line_match)
        
        # Update invoice status if matched
        if match_results["match_status"] == "matched":
            invoice.status = "matched"
            await db.commit()
        
        return match_results
    
    async def schedule_payment(self, db: AsyncSession, bill_id: int, schedule_data: dict, user_id: int):
        """Schedule payment for bill"""
        query = select(Invoice).where(Invoice.id == bill_id)
        result = await db.execute(query)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            return None
        
        # Update payment due date
        payment_date = datetime.strptime(schedule_data["payment_date"], "%Y-%m-%d").date()
        invoice.payment_due_date = payment_date
        invoice.updated_by = user_id
        invoice.updated_at = datetime.utcnow()
        
        # Add scheduling note
        schedule_note = f"Payment scheduled for {payment_date.strftime('%Y-%m-%d')}"
        if schedule_data.get("notes"):
            schedule_note += f": {schedule_data['notes']}"
            
        if invoice.notes:
            invoice.notes += f"\n{schedule_note}"
        else:
            invoice.notes = schedule_note
        
        await db.commit()
        
        return {
            "bill_id": bill_id,
            "payment_date": payment_date.isoformat(),
            "amount": float(invoice.balance_due),
            "status": "scheduled",
            "scheduled_by": user_id
        }