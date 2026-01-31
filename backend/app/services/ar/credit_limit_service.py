"""Credit limit management service for AR.

Author: Paksa IT Solutions
Copyright (c) 2024 Paksa IT Solutions. All rights reserved.
"""

from datetime import datetime
from typing import Dict, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.invoice import Invoice


class CreditLimitService:
    """Service for managing customer credit limits and exposure."""

    def __init__(self, db: Session):
        self.db = db

    def get_customer_exposure(self, customer_id: int) -> Decimal:
        """Calculate total outstanding balance for customer."""
        invoices = (
            self.db.query(Invoice)
            .filter(
                Invoice.customer_id == customer_id,
                Invoice.status.in_(["unpaid", "partially_paid"]),
            )
            .all()
        )
        return sum(inv.balance_due for inv in invoices)

    def check_credit_limit(
        self, customer_id: int, additional_amount: Decimal = 0
    ) -> Dict:
        """Check if customer is within credit limit."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"allowed": False, "reason": "Customer not found"}

        if not customer.credit_limit:
            return {"allowed": True, "reason": "No credit limit set"}

        current_exposure = self.get_customer_exposure(customer_id)
        total_exposure = current_exposure + additional_amount
        available_credit = customer.credit_limit - current_exposure

        utilization = (
            (total_exposure / customer.credit_limit * 100)
            if customer.credit_limit > 0
            else 0
        )

        return {
            "allowed": total_exposure <= customer.credit_limit,
            "credit_limit": float(customer.credit_limit),
            "current_exposure": float(current_exposure),
            "additional_amount": float(additional_amount),
            "total_exposure": float(total_exposure),
            "available_credit": float(available_credit),
            "utilization_percent": float(utilization),
            "status": self._get_status(utilization),
        }

    def _get_status(self, utilization: float) -> str:
        """Get credit status based on utilization."""
        if utilization >= 100:
            return "exceeded"
        elif utilization >= 90:
            return "critical"
        elif utilization >= 75:
            return "warning"
        return "normal"

    def update_credit_limit(
        self, customer_id: int, new_limit: Decimal, reason: str
    ) -> Dict:
        """Update customer credit limit with audit trail."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"success": False, "message": "Customer not found"}

        old_limit = customer.credit_limit
        customer.credit_limit = new_limit
        self.db.commit()

        return {
            "success": True,
            "customer_id": customer_id,
            "old_limit": float(old_limit) if old_limit else 0,
            "new_limit": float(new_limit),
            "reason": reason,
            "updated_at": datetime.utcnow(),
        }

    def get_credit_alerts(self) -> Dict:
        """Get customers with credit limit issues."""
        customers = (
            self.db.query(Customer).filter(Customer.credit_limit.isnot(None)).all()
        )
        alerts = {"exceeded": [], "critical": [], "warning": []}

        for customer in customers:
            check = self.check_credit_limit(customer.id)
            status = check["status"]
            if status in alerts:
                alerts[status].append(
                    {
                        "customer_id": customer.id,
                        "customer_name": customer.name,
                        "utilization": check["utilization_percent"],
                        "exposure": check["current_exposure"],
                        "limit": check["credit_limit"],
                    }
                )

        return alerts
