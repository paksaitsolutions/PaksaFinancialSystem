from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from datetime import datetime

class VendorService:
    """Service for vendor management operations"""
    
    async def create_vendor(self, db: AsyncSession, vendor_data: dict):
        """Create a new vendor"""
        # Simulate vendor creation
        vendor = {
            "id": 1,
            "vendor_id": f"VEN-{datetime.now().strftime('%Y%m%d')}-001",
            "name": vendor_data.get("name"),
            "email": vendor_data.get("email"),
            "status": "pending_approval",
            "created_at": datetime.now().isoformat()
        }
        return vendor
    
    async def get_vendors(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
                         status: Optional[str] = None, category: Optional[str] = None):
        """Get vendors with filtering"""
        # Simulate vendor retrieval
        vendors = [
            {
                "id": 1,
                "vendor_id": "VEN-20240101-001",
                "name": "ABC Supplies Inc",
                "email": "contact@abcsupplies.com",
                "status": "active",
                "category": "supplier",
                "total_spent": 125000.00
            },
            {
                "id": 2,
                "vendor_id": "VEN-20240101-002", 
                "name": "XYZ Services LLC",
                "email": "info@xyzservices.com",
                "status": "active",
                "category": "service_provider",
                "total_spent": 75000.00
            }
        ]
        
        # Apply filters
        if status:
            vendors = [v for v in vendors if v["status"] == status]
        if category:
            vendors = [v for v in vendors if v["category"] == category]
            
        return vendors[skip:skip+limit]
    
    async def get_vendor(self, db: AsyncSession, vendor_id: int):
        """Get vendor by ID"""
        # Simulate vendor retrieval
        return {
            "id": vendor_id,
            "vendor_id": f"VEN-20240101-{vendor_id:03d}",
            "name": "Sample Vendor",
            "email": "vendor@example.com",
            "status": "active",
            "category": "supplier",
            "contact_person": "John Doe",
            "phone": "+1-555-0123",
            "address": "123 Business St, City, State 12345",
            "payment_terms": "NET30",
            "credit_limit": 50000.00,
            "current_balance": 15000.00
        }
    
    async def update_vendor(self, db: AsyncSession, vendor_id: int, vendor_data: dict):
        """Update vendor"""
        # Simulate vendor update
        updated_vendor = await self.get_vendor(db, vendor_id)
        updated_vendor.update(vendor_data)
        updated_vendor["updated_at"] = datetime.now().isoformat()
        return updated_vendor
    
    async def delete_vendor(self, db: AsyncSession, vendor_id: int):
        """Delete vendor"""
        # Simulate vendor deletion
        return {"deleted": True, "vendor_id": vendor_id}
    
    async def approve_vendor(self, db: AsyncSession, vendor_id: int, approval_data: dict):
        """Approve vendor"""
        # Simulate vendor approval
        return {
            "vendor_id": vendor_id,
            "status": "approved",
            "approved_by": approval_data.get("approved_by"),
            "approved_at": datetime.now().isoformat(),
            "notes": approval_data.get("notes")
        }
    
    async def reject_vendor(self, db: AsyncSession, vendor_id: int, approval_data: dict):
        """Reject vendor"""
        # Simulate vendor rejection
        return {
            "vendor_id": vendor_id,
            "status": "rejected",
            "rejected_by": approval_data.get("rejected_by"),
            "rejected_at": datetime.now().isoformat(),
            "reason": approval_data.get("reason")
        }
    
    async def get_vendor_performance(self, db: AsyncSession, vendor_id: int):
        """Get vendor performance metrics"""
        # Simulate performance calculation
        return {
            "vendor_id": vendor_id,
            "performance_score": 4.2,
            "on_time_delivery_rate": 95.5,
            "quality_score": 4.5,
            "total_orders": 150,
            "total_spent_ytd": 125000.00,
            "average_order_value": 833.33,
            "last_evaluation_date": "2024-01-15",
            "recommendations": "Continue partnership - excellent performance"
        }
    
    async def create_evaluation(self, db: AsyncSession, vendor_id: int, evaluation_data: dict):
        """Create vendor evaluation"""
        # Simulate evaluation creation
        return {
            "evaluation_id": 1,
            "vendor_id": vendor_id,
            "evaluator": evaluation_data.get("evaluator"),
            "overall_score": evaluation_data.get("overall_score"),
            "quality_score": evaluation_data.get("quality_score"),
            "delivery_score": evaluation_data.get("delivery_score"),
            "service_score": evaluation_data.get("service_score"),
            "comments": evaluation_data.get("comments"),
            "evaluation_date": datetime.now().isoformat()
        }