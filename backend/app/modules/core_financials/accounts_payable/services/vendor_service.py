from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, datetime
from decimal import Decimal

from app.modules.core_financials.accounts_payable.models import Vendor, VendorStatus
from app.modules.core_financials.accounts_payable.schemas import VendorCreate, VendorUpdate
from app.core.exceptions import NotFoundError, ValidationError

class VendorService:
    def __init__(self, db: Session):
        self.db = db

    def create_vendor(self, vendor_data: VendorCreate) -> Vendor:
        """Create a new vendor"""
        vendor = Vendor(
            vendor_id=vendor_data.vendor_id,
            name=vendor_data.name,
            legal_name=vendor_data.legal_name,
            category=vendor_data.category,
            contact_person=vendor_data.contact_person,
            email=vendor_data.email,
            phone=vendor_data.phone,
            billing_address=vendor_data.billing_address,
            tax_id=vendor_data.tax_id,
            payment_terms=vendor_data.payment_terms,
            credit_limit=vendor_data.credit_limit,
            currency_code=vendor_data.currency_code,
            status=VendorStatus.ACTIVE
        )
        self.db.add(vendor)
        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    def get_vendor(self, vendor_id: int) -> Vendor:
        """Get a vendor by ID"""
        vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise NotFoundError(f"Vendor with ID {vendor_id} not found")
        return vendor

    def get_vendors(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Vendor]:
        """Get a list of vendors with optional filtering"""
        query = self.db.query(Vendor)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Vendor.name.ilike(search_pattern),
                    Vendor.vendor_id.ilike(search_pattern),
                    Vendor.email.ilike(search_pattern),
                    Vendor.tax_id.ilike(search_pattern)
                )
            )
            
        if status:
            try:
                status_enum = VendorStatus(status)
                query = query.filter(Vendor.status == status_enum)
            except ValueError:
                # Skip invalid status values
                pass
                
        if category:
            try:
                category_enum = VendorCategory(category)
                query = query.filter(Vendor.category == category_enum)
            except ValueError:
                # Skip invalid category values
                pass
                
        return query.offset(skip).limit(limit).all()

    def update_vendor(self, vendor_id: int, vendor_data: VendorUpdate) -> Vendor:
        """Update an existing vendor"""
        vendor = self.get_vendor(vendor_id)
        
        update_data = vendor_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)
            
        vendor.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    def delete_vendor(self, vendor_id: int) -> None:
        """Delete a vendor"""
        vendor = self.get_vendor(vendor_id)
        self.db.delete(vendor)
        self.db.commit()

    def get_vendor_outstanding_balance(self, vendor_id: int) -> Decimal:
        """Get the total outstanding balance for a vendor"""
        vendor = self.get_vendor(vendor_id)
        return vendor.outstanding_balance

    def get_vendor_payment_history(self, vendor_id: int, days: int = 30) -> List[dict]:
        """Get payment history for a vendor"""
        from .payment_service import PaymentService
        payment_service = PaymentService(self.db)
        return payment_service.get_vendor_payments(vendor_id, days=days)

    def get_vendor_invoices(self, vendor_id: int, status: Optional[str] = None) -> List:
        """Get all invoices for a vendor with optional status filter"""
        from .invoice_service import InvoiceService
        invoice_service = InvoiceService(self.db)
        return invoice_service.get_vendor_invoices(vendor_id, status=status)
