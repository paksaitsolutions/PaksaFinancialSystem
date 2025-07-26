from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from ..models import Vendor, VendorEvaluation, VendorContract

class VendorService:
    """Service for vendor management operations"""
    
    async def create_vendor(self, db: AsyncSession, vendor_data: dict, user_id: int):
        """Create a new vendor with real database persistence"""
        # Generate unique vendor ID
        vendor_count = await db.scalar(select(func.count(Vendor.id)))
        vendor_id = f"VEN-{datetime.now().strftime('%Y%m%d')}-{vendor_count + 1:03d}"
        
        # Create vendor instance
        vendor = Vendor(
            vendor_id=vendor_id,
            name=vendor_data.get("name"),
            legal_name=vendor_data.get("legal_name", vendor_data.get("name")),
            category=vendor_data.get("category", "supplier"),
            email=vendor_data.get("email"),
            phone=vendor_data.get("phone"),
            contact_person=vendor_data.get("contact_person"),
            billing_address_line1=vendor_data.get("address_line1"),
            billing_city=vendor_data.get("city"),
            billing_state=vendor_data.get("state"),
            billing_postal_code=vendor_data.get("postal_code"),
            billing_country=vendor_data.get("country", "US"),
            payment_terms_id=vendor_data.get("payment_terms_id"),
            credit_limit=vendor_data.get("credit_limit", 0),
            status="pending_approval",
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(vendor)
        await db.commit()
        await db.refresh(vendor)
        return vendor
    
    async def get_vendors(self, db: AsyncSession, skip: int = 0, limit: int = 100, 
                         status: Optional[str] = None, category: Optional[str] = None):
        """Get vendors with real database filtering"""
        query = select(Vendor).options(selectinload(Vendor.payment_terms_rel))
        
        # Apply filters
        if status:
            query = query.where(Vendor.status == status)
        if category:
            query = query.where(Vendor.category == category)
            
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Vendor.name)
        
        result = await db.execute(query)
        vendors = result.scalars().all()
        
        # Calculate total spent for each vendor
        vendor_list = []
        for vendor in vendors:
            vendor_dict = {
                "id": vendor.id,
                "vendor_id": vendor.vendor_id,
                "name": vendor.name,
                "email": vendor.email,
                "status": vendor.status,
                "category": vendor.category,
                "total_spent": float(vendor.total_spent_ytd or 0),
                "outstanding_balance": float(vendor.outstanding_balance or 0),
                "credit_limit": float(vendor.credit_limit or 0),
                "created_at": vendor.created_at.isoformat() if vendor.created_at else None
            }
            vendor_list.append(vendor_dict)
            
        return vendor_list
    
    async def get_vendor(self, db: AsyncSession, vendor_id: int):
        """Get vendor by ID with real database lookup"""
        query = select(Vendor).options(
            selectinload(Vendor.payment_terms_rel),
            selectinload(Vendor.invoices),
            selectinload(Vendor.evaluations)
        ).where(Vendor.id == vendor_id)
        
        result = await db.execute(query)
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            return None
            
        return {
            "id": vendor.id,
            "vendor_id": vendor.vendor_id,
            "name": vendor.name,
            "legal_name": vendor.legal_name,
            "email": vendor.email,
            "phone": vendor.phone,
            "status": vendor.status,
            "category": vendor.category,
            "contact_person": vendor.contact_person,
            "billing_address_line1": vendor.billing_address_line1,
            "billing_city": vendor.billing_city,
            "billing_state": vendor.billing_state,
            "billing_postal_code": vendor.billing_postal_code,
            "billing_country": vendor.billing_country,
            "payment_terms": vendor.payment_terms_rel.name if vendor.payment_terms_rel else None,
            "credit_limit": float(vendor.credit_limit or 0),
            "current_balance": float(vendor.current_balance or 0),
            "outstanding_balance": float(vendor.outstanding_balance or 0),
            "total_spent_ytd": float(vendor.total_spent_ytd or 0),
            "created_at": vendor.created_at.isoformat() if vendor.created_at else None,
            "updated_at": vendor.updated_at.isoformat() if vendor.updated_at else None
        }
    
    async def update_vendor(self, db: AsyncSession, vendor_id: int, vendor_data: dict, user_id: int):
        """Update vendor with real database persistence"""
        query = select(Vendor).where(Vendor.id == vendor_id)
        result = await db.execute(query)
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            return None
            
        # Update fields
        for field, value in vendor_data.items():
            if hasattr(vendor, field) and value is not None:
                setattr(vendor, field, value)
                
        vendor.updated_by = user_id
        vendor.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(vendor)
        return await self.get_vendor(db, vendor_id)
    
    async def delete_vendor(self, db: AsyncSession, vendor_id: int):
        """Delete vendor with real database operation"""
        query = select(Vendor).where(Vendor.id == vendor_id)
        result = await db.execute(query)
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            return {"deleted": False, "error": "Vendor not found"}
            
        # Check for existing invoices or payments
        invoice_count = await db.scalar(
            select(func.count()).select_from(
                select(1).where(and_(
                    Vendor.id == vendor_id,
                    Vendor.invoices.any()
                )).subquery()
            )
        )
        
        if invoice_count > 0:
            return {"deleted": False, "error": "Cannot delete vendor with existing invoices"}
            
        await db.delete(vendor)
        await db.commit()
        return {"deleted": True, "vendor_id": vendor_id}
    
    async def approve_vendor(self, db: AsyncSession, vendor_id: int, approval_data: dict, user_id: int):
        """Approve vendor with real database update"""
        query = select(Vendor).where(Vendor.id == vendor_id)
        result = await db.execute(query)
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            return None
            
        vendor.status = "active"
        vendor.updated_by = user_id
        vendor.updated_at = datetime.utcnow()
        
        # Add approval notes to internal notes
        approval_note = f"Approved on {datetime.now().strftime('%Y-%m-%d')} by user {user_id}"
        if approval_data.get("notes"):
            approval_note += f": {approval_data['notes']}"
            
        if vendor.internal_notes:
            vendor.internal_notes += f"\n{approval_note}"
        else:
            vendor.internal_notes = approval_note
            
        await db.commit()
        await db.refresh(vendor)
        
        return {
            "vendor_id": vendor_id,
            "status": vendor.status,
            "approved_by": user_id,
            "approved_at": datetime.now().isoformat(),
            "notes": approval_data.get("notes")
        }
    
    async def reject_vendor(self, db: AsyncSession, vendor_id: int, rejection_data: dict, user_id: int):
        """Reject vendor with real database update"""
        query = select(Vendor).where(Vendor.id == vendor_id)
        result = await db.execute(query)
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            return None
            
        vendor.status = "inactive"
        vendor.updated_by = user_id
        vendor.updated_at = datetime.utcnow()
        
        # Add rejection reason to internal notes
        rejection_note = f"Rejected on {datetime.now().strftime('%Y-%m-%d')} by user {user_id}"
        if rejection_data.get("reason"):
            rejection_note += f": {rejection_data['reason']}"
            
        if vendor.internal_notes:
            vendor.internal_notes += f"\n{rejection_note}"
        else:
            vendor.internal_notes = rejection_note
            
        await db.commit()
        await db.refresh(vendor)
        
        return {
            "vendor_id": vendor_id,
            "status": vendor.status,
            "rejected_by": user_id,
            "rejected_at": datetime.now().isoformat(),
            "reason": rejection_data.get("reason")
        }
    
    async def get_vendor_performance(self, db: AsyncSession, vendor_id: int):
        """Get vendor performance metrics from real data"""
        # Get vendor with evaluations
        query = select(Vendor).options(
            selectinload(Vendor.evaluations),
            selectinload(Vendor.invoices)
        ).where(Vendor.id == vendor_id)
        
        result = await db.execute(query)
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            return None
            
        # Calculate performance metrics from evaluations
        evaluations = vendor.evaluations
        if evaluations:
            latest_eval = max(evaluations, key=lambda e: e.evaluation_date)
            avg_quality = sum(e.quality_score for e in evaluations if e.quality_score) / len([e for e in evaluations if e.quality_score]) if evaluations else 0
            avg_delivery = sum(e.delivery_score for e in evaluations if e.delivery_score) / len([e for e in evaluations if e.delivery_score]) if evaluations else 0
            avg_overall = sum(e.overall_score for e in evaluations if e.overall_score) / len([e for e in evaluations if e.overall_score]) if evaluations else 0
        else:
            latest_eval = None
            avg_quality = avg_delivery = avg_overall = 0
            
        # Calculate order metrics from invoices
        paid_invoices = [inv for inv in vendor.invoices if inv.status == "paid"]
        total_orders = len(paid_invoices)
        total_spent = sum(float(inv.total_amount) for inv in paid_invoices)
        avg_order_value = total_spent / total_orders if total_orders > 0 else 0
        
        return {
            "vendor_id": vendor_id,
            "performance_score": float(avg_overall) if avg_overall else 0,
            "on_time_delivery_rate": float(avg_delivery * 20) if avg_delivery else 0,  # Convert 0-5 to 0-100
            "quality_score": float(avg_quality) if avg_quality else 0,
            "total_orders": total_orders,
            "total_spent_ytd": float(vendor.total_spent_ytd or 0),
            "average_order_value": avg_order_value,
            "last_evaluation_date": latest_eval.evaluation_date.isoformat() if latest_eval else None,
            "recommendations": latest_eval.comments if latest_eval else "No evaluations available"
        }
    
    async def create_evaluation(self, db: AsyncSession, vendor_id: int, evaluation_data: dict, user_id: int):
        """Create vendor evaluation with real database persistence"""
        evaluation = VendorEvaluation(
            vendor_id=vendor_id,
            evaluator_id=user_id,
            evaluation_date=evaluation_data.get("evaluation_date", datetime.now().date()),
            quality_score=evaluation_data.get("quality_score"),
            delivery_score=evaluation_data.get("delivery_score"),
            price_score=evaluation_data.get("price_score"),
            service_score=evaluation_data.get("service_score"),
            communication_score=evaluation_data.get("communication_score"),
            overall_score=evaluation_data.get("overall_score"),
            recommendation=evaluation_data.get("recommendation"),
            strengths=evaluation_data.get("strengths"),
            areas_for_improvement=evaluation_data.get("areas_for_improvement"),
            comments=evaluation_data.get("comments"),
            status="submitted",
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        
        return {
            "evaluation_id": evaluation.id,
            "vendor_id": vendor_id,
            "evaluator": user_id,
            "overall_score": float(evaluation.overall_score),
            "quality_score": float(evaluation.quality_score) if evaluation.quality_score else None,
            "delivery_score": float(evaluation.delivery_score) if evaluation.delivery_score else None,
            "service_score": float(evaluation.service_score) if evaluation.service_score else None,
            "comments": evaluation.comments,
            "evaluation_date": evaluation.evaluation_date.isoformat()
        }