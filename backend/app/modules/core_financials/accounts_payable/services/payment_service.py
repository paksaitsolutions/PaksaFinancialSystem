from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class PaymentService:
    """Service for payment processing operations"""
    
    async def create_payment(self, db: AsyncSession, payment_data: dict):
        """Create a new payment"""
        payment = {
            "id": 1,
            "payment_number": f"PAY-{datetime.now().strftime('%Y%m%d')}-001",
            "vendor_id": payment_data.get("vendor_id"),
            "amount": payment_data.get("amount"),
            "payment_method": payment_data.get("payment_method", "check"),
            "payment_date": payment_data.get("payment_date"),
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        return payment
    
    async def get_payments(self, db: AsyncSession, skip: int = 0, limit: int = 100,
                          status: Optional[str] = None, vendor_id: Optional[int] = None):
        """Get payments with filtering"""
        payments = [
            {
                "id": 1,
                "payment_number": "PAY-20240101-001",
                "vendor_id": 1,
                "vendor_name": "ABC Supplies Inc",
                "amount": 1500.00,
                "payment_method": "check",
                "payment_date": "2024-02-01",
                "status": "pending"
            },
            {
                "id": 2,
                "payment_number": "PAY-20240101-002",
                "vendor_id": 2,
                "vendor_name": "XYZ Services LLC",
                "amount": 2500.00,
                "payment_method": "ach",
                "payment_date": "2024-02-15",
                "status": "approved"
            }
        ]
        
        if status:
            payments = [p for p in payments if p["status"] == status]
        if vendor_id:
            payments = [p for p in payments if p["vendor_id"] == vendor_id]
            
        return payments[skip:skip+limit]
    
    async def create_payment_batch(self, db: AsyncSession, batch_data: dict):
        """Create payment batch"""
        batch_id = str(uuid.uuid4())[:8]
        payments = batch_data.get("payments", [])
        total_amount = sum(p.get("amount", 0) for p in payments)
        
        batch = {
            "batch_id": batch_id,
            "batch_number": f"BATCH-{datetime.now().strftime('%Y%m%d')}-001",
            "total_amount": total_amount,
            "payment_count": len(payments),
            "payment_method": batch_data.get("payment_method", "check"),
            "payment_date": batch_data.get("payment_date"),
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "payments": payments
        }
        return batch
    
    async def get_payment_batch(self, db: AsyncSession, batch_id: str):
        """Get payment batch details"""
        return {
            "batch_id": batch_id,
            "batch_number": f"BATCH-20240101-001",
            "total_amount": 15000.00,
            "payment_count": 10,
            "payment_method": "ach",
            "payment_date": "2024-02-01",
            "status": "approved",
            "created_at": "2024-01-15T10:00:00",
            "approved_at": "2024-01-15T14:30:00",
            "payments": [
                {
                    "payment_id": 1,
                    "vendor_name": "ABC Supplies Inc",
                    "amount": 1500.00,
                    "status": "included"
                },
                {
                    "payment_id": 2,
                    "vendor_name": "XYZ Services LLC",
                    "amount": 2500.00,
                    "status": "included"
                }
            ]
        }
    
    async def approve_payment_batch(self, db: AsyncSession, batch_id: str, approval_data: dict):
        """Approve payment batch"""
        return {
            "batch_id": batch_id,
            "status": "approved",
            "approved_by": approval_data.get("approved_by"),
            "approved_at": datetime.now().isoformat(),
            "approval_notes": approval_data.get("notes")
        }
    
    async def process_payment_batch(self, db: AsyncSession, batch_id: str):
        """Process payment batch"""
        # Simulate batch processing
        return {
            "batch_id": batch_id,
            "status": "processing",
            "started_at": datetime.now().isoformat(),
            "processed_count": 0,
            "failed_count": 0,
            "total_count": 10,
            "estimated_completion": (datetime.now().timestamp() + 300)  # 5 minutes
        }
    
    async def get_payment_methods(self, db: AsyncSession):
        """Get available payment methods"""
        return [
            {
                "id": 1,
                "name": "Check",
                "code": "CHECK",
                "description": "Paper check payment",
                "is_active": True,
                "processing_days": 3
            },
            {
                "id": 2,
                "name": "ACH Transfer",
                "code": "ACH",
                "description": "Electronic bank transfer",
                "is_active": True,
                "processing_days": 1
            },
            {
                "id": 3,
                "name": "Wire Transfer",
                "code": "WIRE",
                "description": "Same-day wire transfer",
                "is_active": True,
                "processing_days": 0
            },
            {
                "id": 4,
                "name": "Credit Card",
                "code": "CARD",
                "description": "Credit card payment",
                "is_active": False,
                "processing_days": 0
            }
        ]
    
    async def create_payment_method(self, db: AsyncSession, method_data: dict):
        """Create payment method"""
        method = {
            "id": 5,
            "name": method_data.get("name"),
            "code": method_data.get("code"),
            "description": method_data.get("description"),
            "is_active": method_data.get("is_active", True),
            "processing_days": method_data.get("processing_days", 1),
            "created_at": datetime.now().isoformat()
        }
        return method
    
    async def approve_payment(self, db: AsyncSession, payment_id: int, approval_data: dict):
        """Approve individual payment"""
        return {
            "payment_id": payment_id,
            "status": "approved",
            "approved_by": approval_data.get("approved_by"),
            "approved_at": datetime.now().isoformat(),
            "approval_notes": approval_data.get("notes")
        }
    
    async def get_payment_status(self, db: AsyncSession, payment_id: int):
        """Get payment status and tracking info"""
        return {
            "payment_id": payment_id,
            "status": "processed",
            "payment_date": "2024-02-01",
            "processed_at": "2024-02-01T09:00:00",
            "tracking_number": "TRK123456789",
            "bank_reference": "REF987654321",
            "status_history": [
                {
                    "status": "created",
                    "timestamp": "2024-01-15T10:00:00",
                    "user": "system"
                },
                {
                    "status": "approved",
                    "timestamp": "2024-01-15T14:30:00",
                    "user": "manager@company.com"
                },
                {
                    "status": "processed",
                    "timestamp": "2024-02-01T09:00:00",
                    "user": "system"
                }
            ]
        }