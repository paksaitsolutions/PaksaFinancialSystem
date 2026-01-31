"""Customer portal service for AR self-service.

Author: Paksa IT Solutions
Copyright (c) 2024 Paksa IT Solutions. All rights reserved.
"""

from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.invoice import Invoice


class CustomerPortalService:
    """Service for customer self-service portal functionality."""

    def __init__(self, db: Session):
        self.db = db

    def get_customer_dashboard(self, customer_id: int) -> Dict:
        """Get customer dashboard data."""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"error": "Customer not found"}

        invoices = (
            self.db.query(Invoice).filter(Invoice.customer_id == customer_id).all()
        )

        total_outstanding = sum(
            inv.balance_due
            for inv in invoices
            if inv.status in ["unpaid", "partially_paid"]
        )
        overdue_amount = sum(
            inv.balance_due
            for inv in invoices
            if inv.status in ["unpaid", "partially_paid"]
            and inv.due_date < datetime.utcnow().date()
        )

        return {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "total_outstanding": float(total_outstanding),
            "overdue_amount": float(overdue_amount),
            "credit_limit": (
                float(customer.credit_limit) if customer.credit_limit else None
            ),
            "available_credit": (
                float(customer.credit_limit - total_outstanding)
                if customer.credit_limit
                else None
            ),
            "invoice_count": len(invoices),
            "last_payment_date": None,  # Would come from payment records
        }

    def get_customer_invoices(
        self, customer_id: int, status: Optional[str] = None, limit: int = 50
    ) -> List[Dict]:
        """Get customer invoices with optional status filter."""
        query = self.db.query(Invoice).filter(Invoice.customer_id == customer_id)

        if status:
            query = query.filter(Invoice.status == status)

        invoices = query.order_by(Invoice.invoice_date.desc()).limit(limit).all()

        return [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "invoice_date": inv.invoice_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "amount": float(inv.amount),
                "balance_due": float(inv.balance_due),
                "status": inv.status,
                "is_overdue": inv.due_date < datetime.utcnow().date()
                and inv.status != "paid",
            }
            for inv in invoices
        ]

    def get_invoice_details(self, customer_id: int, invoice_id: int) -> Optional[Dict]:
        """Get detailed invoice information for customer."""
        invoice = (
            self.db.query(Invoice)
            .filter(Invoice.id == invoice_id, Invoice.customer_id == customer_id)
            .first()
        )

        if not invoice:
            return None

        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "amount": float(invoice.amount),
            "balance_due": float(invoice.balance_due),
            "status": invoice.status,
            "description": invoice.description,
            "line_items": [],  # Would include invoice line items
            "payment_history": [],  # Would include payment records
        }

    def initiate_payment(
        self,
        customer_id: int,
        invoice_ids: List[int],
        payment_amount: float,
        payment_method: str,
    ) -> Dict:
        """Initiate payment for invoices (returns payment intent)."""
        invoices = (
            self.db.query(Invoice)
            .filter(Invoice.id.in_(invoice_ids), Invoice.customer_id == customer_id)
            .all()
        )

        total_due = sum(inv.balance_due for inv in invoices)

        return {
            "payment_intent_id": f"pi_{datetime.utcnow().timestamp()}",
            "customer_id": customer_id,
            "invoice_ids": invoice_ids,
            "payment_amount": payment_amount,
            "total_due": float(total_due),
            "payment_method": payment_method,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }

    def get_payment_history(self, customer_id: int, limit: int = 20) -> List[Dict]:
        """Get customer payment history."""
        # In real implementation, query payment records
        return []

    def download_invoice_pdf(
        self, customer_id: int, invoice_id: int
    ) -> Optional[bytes]:
        """Generate and return invoice PDF."""
        # In real implementation, generate PDF
        return None
