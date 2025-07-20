from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud.base import CRUDBase
from app.models.tax_payment import TaxPayment
from app.schemas.tax_payment import PaymentStatus, TaxPaymentCreate, TaxPaymentUpdate


class CRUDTaxPayment(CRUDBase[TaxPayment, TaxPaymentCreate, TaxPaymentUpdate]):
    def get_multi_by_tax_return(
        self, db: Session, *, tax_return_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[TaxPayment]:
        return (
            db.query(self.model)
            .filter(TaxPayment.tax_return_id == tax_return_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_company(
        self, db: Session, *, company_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[TaxPayment]:
        return (
            db.query(self.model)
            .join(models.TaxReturn)
            .filter(models.TaxReturn.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_status(
        self, db: Session, *, status: PaymentStatus, skip: int = 0, limit: int = 100
    ) -> List[TaxPayment]:
        return (
            db.query(self.model)
            .filter(TaxPayment.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_date_range(
        self,
        db: Session,
        *,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TaxPayment]:
        return (
            db.query(self.model)
            .filter(
                TaxPayment.payment_date >= start_date,
                TaxPayment.payment_date <= end_date,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_tax_return(
        self, db: Session, *, obj_in: TaxPaymentCreate, tax_return_id: UUID, created_by: UUID
    ) -> TaxPayment:
        db_obj = self.model(
            **obj_in.dict(exclude={"metadata"}),
            tax_return_id=tax_return_id,
            created_by=created_by,
            metadata=obj_in.metadata or {},
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_status(
        self, db: Session, *, db_obj: TaxPayment, status: PaymentStatus, updated_by: UUID = None
    ) -> TaxPayment:
        update_data = {"status": status, "updated_at": datetime.utcnow()}
        if updated_by:
            update_data["updated_by"] = updated_by
            
        return self.update(db, db_obj=db_obj, obj_in=update_data)

    def get_summary(
        self, db: Session, *, company_id: UUID, start_date: datetime = None, end_date: datetime = None
    ) -> Dict[str, Any]:
        query = db.query(
            models.TaxPayment.currency,
            models.TaxPayment.status,
            models.TaxPayment.payment_method,
            models.TaxPayment.amount,
        ).join(models.TaxReturn).filter(models.TaxReturn.company_id == company_id)

        if start_date:
            query = query.filter(models.TaxPayment.payment_date >= start_date)
        if end_date:
            query = query.filter(models.TaxPayment.payment_date <= end_date)

        payments = query.all()
        
        # Initialize summary
        summary = {
            "total_paid": 0.0,
            "total_refunded": 0.0,
            "by_currency": {},
            "by_status": {},
            "by_method": {},
        }
        
        # Process payments
        for payment in payments:
            currency = payment.currency
            amount = float(payment.amount)
            status = payment.status
            method = payment.payment_method
            
            # Initialize currency if not exists
            if currency not in summary["by_currency"]:
                summary["by_currency"][currency] = 0.0
                
            # Update totals
            if status == PaymentStatus.REFUNDED or status == PaymentStatus.PARTIALLY_REFUNDED:
                summary["total_refunded"] += amount
                summary["by_currency"][currency] -= amount
            else:
                summary["total_paid"] += amount
                summary["by_currency"][currency] += amount
            
            # Update status summary
            if status not in summary["by_status"]:
                summary["by_status"][status] = 0
            summary["by_status"][status] += 1
            
            # Update method summary
            if method not in summary["by_method"]:
                summary["by_method"][method] = 0.0
            summary["by_method"][method] += amount
        
        return summary


# Initialize the CRUD operations for TaxPayment
tax_payment = CRUDTaxPayment(TaxPayment)
