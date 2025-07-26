from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from datetime import datetime, timedelta

class BillService:
    """Service for bill processing operations"""
    
    async def create_bill(self, db: AsyncSession, bill_data: dict):
        """Create a new bill"""
        bill = {
            "id": 1,
            "bill_number": f"BILL-{datetime.now().strftime('%Y%m%d')}-001",
            "vendor_id": bill_data.get("vendor_id"),
            "amount": bill_data.get("amount"),
            "due_date": bill_data.get("due_date"),
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        return bill
    
    async def get_bills(self, db: AsyncSession, skip: int = 0, limit: int = 100,
                       status: Optional[str] = None, vendor_id: Optional[int] = None):
        """Get bills with filtering"""
        bills = [
            {
                "id": 1,
                "bill_number": "BILL-20240101-001",
                "vendor_id": 1,
                "vendor_name": "ABC Supplies Inc",
                "amount": 1500.00,
                "due_date": "2024-02-01",
                "status": "pending_approval"
            },
            {
                "id": 2,
                "bill_number": "BILL-20240101-002",
                "vendor_id": 2,
                "vendor_name": "XYZ Services LLC",
                "amount": 2500.00,
                "due_date": "2024-02-15",
                "status": "approved"
            }
        ]
        
        if status:
            bills = [b for b in bills if b["status"] == status]
        if vendor_id:
            bills = [b for b in bills if b["vendor_id"] == vendor_id]
            
        return bills[skip:skip+limit]
    
    async def get_bill(self, db: AsyncSession, bill_id: int):
        """Get bill by ID"""
        return {
            "id": bill_id,
            "bill_number": f"BILL-20240101-{bill_id:03d}",
            "vendor_id": 1,
            "vendor_name": "ABC Supplies Inc",
            "amount": 1500.00,
            "tax_amount": 120.00,
            "total_amount": 1620.00,
            "due_date": "2024-02-01",
            "status": "pending_approval",
            "description": "Office supplies and equipment",
            "line_items": [
                {
                    "description": "Office chairs",
                    "quantity": 5,
                    "unit_price": 200.00,
                    "amount": 1000.00
                },
                {
                    "description": "Desk supplies",
                    "quantity": 1,
                    "unit_price": 500.00,
                    "amount": 500.00
                }
            ]
        }
    
    async def approve_bill(self, db: AsyncSession, bill_id: int, approval_data: dict):
        """Approve bill"""
        return {
            "bill_id": bill_id,
            "status": "approved",
            "approved_by": approval_data.get("approved_by"),
            "approved_at": datetime.now().isoformat(),
            "approval_notes": approval_data.get("notes")
        }
    
    async def reject_bill(self, db: AsyncSession, bill_id: int, rejection_data: dict):
        """Reject bill"""
        return {
            "bill_id": bill_id,
            "status": "rejected",
            "rejected_by": rejection_data.get("rejected_by"),
            "rejected_at": datetime.now().isoformat(),
            "rejection_reason": rejection_data.get("reason")
        }
    
    async def three_way_match(self, db: AsyncSession, bill_id: int, match_data: dict):
        """Perform three-way matching"""
        # Simulate matching logic
        po_number = match_data.get("po_number")
        receipt_number = match_data.get("receipt_number")
        
        # Mock matching results
        match_result = {
            "bill_id": bill_id,
            "po_number": po_number,
            "receipt_number": receipt_number,
            "match_status": "matched",
            "po_matched": True,
            "receipt_matched": True,
            "variances": [],
            "matched_amount": 1500.00,
            "variance_amount": 0.00,
            "match_date": datetime.now().isoformat()
        }
        
        # Check for variances (simulated)
        if match_data.get("check_variances", True):
            # Simulate price variance
            if match_data.get("po_amount", 1500.00) != match_data.get("bill_amount", 1500.00):
                match_result["variances"].append({
                    "type": "price_variance",
                    "description": "Price difference between PO and bill",
                    "amount": abs(match_data.get("po_amount", 1500.00) - match_data.get("bill_amount", 1500.00))
                })
                match_result["match_status"] = "variance_detected"
        
        return match_result
    
    async def schedule_payment(self, db: AsyncSession, bill_id: int, schedule_data: dict):
        """Schedule payment for bill"""
        payment_date = schedule_data.get("payment_date")
        if isinstance(payment_date, str):
            payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
        
        return {
            "bill_id": bill_id,
            "payment_date": payment_date.isoformat() if payment_date else None,
            "amount": schedule_data.get("amount"),
            "payment_method": schedule_data.get("payment_method", "check"),
            "status": "scheduled",
            "scheduled_at": datetime.now().isoformat(),
            "scheduled_by": schedule_data.get("scheduled_by")
        }
    
    async def get_bills_for_payment(self, db: AsyncSession, due_date: Optional[str] = None):
        """Get bills ready for payment"""
        # Simulate getting bills ready for payment
        bills = [
            {
                "bill_id": 1,
                "bill_number": "BILL-20240101-001",
                "vendor_id": 1,
                "vendor_name": "ABC Supplies Inc",
                "amount": 1500.00,
                "due_date": "2024-02-01",
                "status": "approved",
                "payment_terms": "NET30"
            },
            {
                "bill_id": 2,
                "bill_number": "BILL-20240101-002",
                "vendor_id": 2,
                "vendor_name": "XYZ Services LLC",
                "amount": 2500.00,
                "due_date": "2024-02-15",
                "status": "approved",
                "payment_terms": "NET15"
            }
        ]
        
        if due_date:
            # Filter by due date
            bills = [b for b in bills if b["due_date"] <= due_date]
        
        return bills