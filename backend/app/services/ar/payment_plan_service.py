"""Payment plan management service for AR.

Author: Paksa IT Solutions
Copyright (c) 2024 Paksa IT Solutions. All rights reserved.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.invoice import Invoice


class PaymentPlanService:
    """Service for managing customer payment plans and installments."""

    def __init__(self, db: Session):
        self.db = db

    def create_payment_plan(
        self,
        customer_id: int,
        invoice_ids: List[int],
        num_installments: int,
        frequency: str = "monthly",
        down_payment: Decimal = 0,
    ) -> Dict:
        """Create payment plan for customer invoices."""
        invoices = self.db.query(Invoice).filter(Invoice.id.in_(invoice_ids)).all()
        total_amount = sum(inv.balance_due for inv in invoices)

        if down_payment >= total_amount:
            return {"success": False, "message": "Down payment exceeds total amount"}

        remaining_amount = total_amount - down_payment
        installment_amount = remaining_amount / num_installments

        installments = []
        start_date = datetime.utcnow().date()

        frequency_days = {"weekly": 7, "biweekly": 14, "monthly": 30, "quarterly": 90}
        days_between = frequency_days.get(frequency, 30)

        for i in range(num_installments):
            due_date = start_date + timedelta(days=days_between * (i + 1))
            installments.append(
                {
                    "installment_number": i + 1,
                    "amount": float(installment_amount),
                    "due_date": due_date.isoformat(),
                    "status": "pending",
                }
            )

        return {
            "success": True,
            "customer_id": customer_id,
            "invoice_ids": invoice_ids,
            "total_amount": float(total_amount),
            "down_payment": float(down_payment),
            "remaining_amount": float(remaining_amount),
            "num_installments": num_installments,
            "installment_amount": float(installment_amount),
            "frequency": frequency,
            "installments": installments,
            "created_at": datetime.utcnow(),
        }

    def calculate_installments(
        self, total_amount: Decimal, num_installments: int, down_payment: Decimal = 0
    ) -> List[Dict]:
        """Calculate installment schedule."""
        remaining = total_amount - down_payment
        installment_amount = remaining / num_installments

        return [
            {
                "installment_number": i + 1,
                "amount": float(installment_amount),
                "cumulative_amount": float(installment_amount * (i + 1)),
            }
            for i in range(num_installments)
        ]

    def record_installment_payment(
        self,
        plan_id: int,
        installment_number: int,
        amount_paid: Decimal,
        payment_date: datetime,
    ) -> Dict:
        """Record payment for installment."""
        return {
            "success": True,
            "plan_id": plan_id,
            "installment_number": installment_number,
            "amount_paid": float(amount_paid),
            "payment_date": payment_date.isoformat(),
            "status": "paid",
        }

    def get_overdue_installments(self, customer_id: Optional[int] = None) -> List[Dict]:
        """Get overdue installments for customer or all customers."""
        # In real implementation, query payment_plan_installments table
        return []

    def get_payment_plan_status(self, plan_id: int) -> Dict:
        """Get current status of payment plan."""
        # In real implementation, calculate from installments
        return {
            "plan_id": plan_id,
            "total_installments": 0,
            "paid_installments": 0,
            "pending_installments": 0,
            "overdue_installments": 0,
            "total_paid": 0.0,
            "total_remaining": 0.0,
            "completion_percent": 0.0,
            "status": "active",
        }
