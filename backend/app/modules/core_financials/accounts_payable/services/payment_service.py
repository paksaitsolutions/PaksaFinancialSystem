from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict
from datetime import datetime, date
from decimal import Decimal
from ..models import Payment, PaymentInvoice, Invoice, Vendor

class PaymentService:
    """Service for payment processing operations"""
    
    async def create_payment(self, db: AsyncSession, payment_data: dict, user_id: int):
        """Create a new payment with real database persistence"""
        # Generate unique payment number
        payment_count = await db.scalar(select(func.count(Payment.id)))
        payment_number = f"PAY-{datetime.now().strftime('%Y%m%d')}-{payment_count + 1:04d}"
        
        # Create payment
        payment = Payment(
            payment_number=payment_number,
            vendor_id=payment_data["vendor_id"],
            payment_date=datetime.strptime(payment_data["payment_date"], "%Y-%m-%d").date(),
            payment_method=payment_data.get("payment_method", "check"),
            reference_number=payment_data.get("reference_number"),
            memo=payment_data.get("memo"),
            amount=Decimal(str(payment_data["amount"])),
            currency_code=payment_data.get("currency_code", "USD"),
            status="draft",
            bank_account_id=payment_data.get("bank_account_id"),
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(payment)
        await db.flush()  # Get the payment ID
        
        # Apply payment to invoices if specified
        if payment_data.get("invoice_applications"):
            for application in payment_data["invoice_applications"]:
                payment_invoice = PaymentInvoice(
                    payment_id=payment.id,
                    invoice_id=application["invoice_id"],
                    amount_applied=Decimal(str(application["amount_applied"])),
                    discount_taken=Decimal(str(application.get("discount_taken", 0)))
                )
                db.add(payment_invoice)
                
                # Update invoice paid amount and balance
                invoice_query = select(Invoice).where(Invoice.id == application["invoice_id"])
                invoice_result = await db.execute(invoice_query)
                invoice = invoice_result.scalar_one()
                
                invoice.paid_amount += Decimal(str(application["amount_applied"]))
                invoice.balance_due = invoice.total_amount - invoice.paid_amount
                
                # Update invoice status based on balance
                if invoice.balance_due <= 0:
                    invoice.status = "paid"
                elif invoice.paid_amount > 0:
                    invoice.status = "partially_paid"
        
        await db.commit()
        await db.refresh(payment)
        return await self.get_payment(db, payment.id)
    
    async def get_payments(self, db: AsyncSession, skip: int = 0, limit: int = 100,
                          vendor_id: Optional[int] = None, status: Optional[str] = None):
        """Get payments with real database filtering"""
        query = select(Payment).options(
            selectinload(Payment.vendor),
            selectinload(Payment.invoice_applications)
        )
        
        # Apply filters
        if vendor_id:
            query = query.where(Payment.vendor_id == vendor_id)
        if status:
            query = query.where(Payment.status == status)
            
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(Payment.payment_date.desc())
        
        result = await db.execute(query)
        payments = result.scalars().all()
        
        return [
            {
                "id": payment.id,
                "payment_number": payment.payment_number,
                "vendor_name": payment.vendor.name,
                "payment_date": payment.payment_date.isoformat(),
                "amount": float(payment.amount),
                "payment_method": payment.payment_method,
                "status": payment.status,
                "reference_number": payment.reference_number
            }
            for payment in payments
        ]
    
    async def get_payment(self, db: AsyncSession, payment_id: int):
        """Get payment by ID with complete details"""
        query = select(Payment).options(
            selectinload(Payment.vendor),
            selectinload(Payment.invoice_applications).selectinload(PaymentInvoice.invoice)
        ).where(Payment.id == payment_id)
        
        result = await db.execute(query)
        payment = result.scalar_one_or_none()
        
        if not payment:
            return None
            
        return {
            "id": payment.id,
            "payment_number": payment.payment_number,
            "vendor_id": payment.vendor_id,
            "vendor_name": payment.vendor.name,
            "payment_date": payment.payment_date.isoformat(),
            "payment_method": payment.payment_method,
            "reference_number": payment.reference_number,
            "memo": payment.memo,
            "amount": float(payment.amount),
            "currency_code": payment.currency_code,
            "status": payment.status,
            "invoice_applications": [
                {
                    "invoice_id": app.invoice_id,
                    "invoice_number": app.invoice.invoice_number,
                    "amount_applied": float(app.amount_applied),
                    "discount_taken": float(app.discount_taken)
                }
                for app in payment.invoice_applications
            ],
            "created_at": payment.created_at.isoformat() if payment.created_at else None
        }
    
    async def process_payment_batch(self, db: AsyncSession, batch_data: dict, user_id: int):
        """Process multiple payments in a batch"""
        batch_results = {
            "batch_id": f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "processed_count": 0,
            "failed_count": 0,
            "total_amount": 0.0,
            "payments": [],
            "errors": []
        }
        
        for payment_data in batch_data.get("payments", []):
            try:
                payment = await self.create_payment(db, payment_data, user_id)
                batch_results["payments"].append(payment)
                batch_results["processed_count"] += 1
                batch_results["total_amount"] += float(payment["amount"])
            except Exception as e:
                batch_results["failed_count"] += 1
                batch_results["errors"].append({
                    "payment_data": payment_data,
                    "error": str(e)
                })
        
        return batch_results
    
    async def approve_payment(self, db: AsyncSession, payment_id: int, approval_data: dict, user_id: int):
        """Approve payment with real database update"""
        query = select(Payment).where(Payment.id == payment_id)
        result = await db.execute(query)
        payment = result.scalar_one_or_none()
        
        if not payment:
            return None
            
        payment.status = "approved"
        payment.updated_by = user_id
        payment.updated_at = datetime.utcnow()
        
        # Add approval memo
        if approval_data.get("notes"):
            approval_note = f"Approved on {datetime.now().strftime('%Y-%m-%d')}: {approval_data['notes']}"
            if payment.memo:
                payment.memo += f"\n{approval_note}"
            else:
                payment.memo = approval_note
        
        await db.commit()
        return {"payment_id": payment_id, "status": "approved", "approved_by": user_id}
    
    async def void_payment(self, db: AsyncSession, payment_id: int, void_data: dict, user_id: int):
        """Void payment and reverse invoice applications"""
        query = select(Payment).options(
            selectinload(Payment.invoice_applications).selectinload(PaymentInvoice.invoice)
        ).where(Payment.id == payment_id)
        
        result = await db.execute(query)
        payment = result.scalar_one_or_none()
        
        if not payment:
            return None
            
        # Reverse invoice applications
        for application in payment.invoice_applications:
            invoice = application.invoice
            invoice.paid_amount -= application.amount_applied
            invoice.balance_due = invoice.total_amount - invoice.paid_amount
            
            # Update invoice status
            if invoice.paid_amount <= 0:
                invoice.status = "approved"
            elif invoice.balance_due > 0:
                invoice.status = "partially_paid"
        
        # Update payment status
        payment.status = "void"
        payment.updated_by = user_id
        payment.updated_at = datetime.utcnow()
        
        # Add void reason
        if void_data.get("reason"):
            void_note = f"Voided on {datetime.now().strftime('%Y-%m-%d')}: {void_data['reason']}"
            if payment.memo:
                payment.memo += f"\n{void_note}"
            else:
                payment.memo = void_note
        
        await db.commit()
        return {"payment_id": payment_id, "status": "void", "voided_by": user_id}
    
    async def get_payment_methods(self, db: AsyncSession):
        """Get available payment methods"""
        return [
            {"code": "check", "name": "Check", "description": "Paper check payment"},
            {"code": "ach", "name": "ACH Transfer", "description": "Electronic bank transfer"},
            {"code": "wire", "name": "Wire Transfer", "description": "Wire transfer payment"},
            {"code": "credit_card", "name": "Credit Card", "description": "Credit card payment"},
            {"code": "cash", "name": "Cash", "description": "Cash payment"},
            {"code": "other", "name": "Other", "description": "Other payment method"}
        ]
    
    async def get_payment_history(self, db: AsyncSession, vendor_id: int, limit: int = 50):
        """Get payment history for a vendor"""
        query = select(Payment).options(
            selectinload(Payment.invoice_applications).selectinload(PaymentInvoice.invoice)
        ).where(
            Payment.vendor_id == vendor_id,
            Payment.status.in_(["approved", "paid"])
        ).order_by(Payment.payment_date.desc()).limit(limit)
        
        result = await db.execute(query)
        payments = result.scalars().all()
        
        return [
            {
                "payment_id": payment.id,
                "payment_number": payment.payment_number,
                "payment_date": payment.payment_date.isoformat(),
                "amount": float(payment.amount),
                "payment_method": payment.payment_method,
                "invoices_paid": len(payment.invoice_applications),
                "reference_number": payment.reference_number
            }
            for payment in payments
        ]