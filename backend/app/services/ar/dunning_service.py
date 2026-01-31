"""Automated dunning letter service for AR collections.

Author: Paksa IT Solutions
Copyright (c) 2024 Paksa IT Solutions. All rights reserved.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.invoice import Invoice


class DunningService:
    """Service for automated dunning letter generation and management."""

    DUNNING_LEVELS = {
        1: {"days_overdue": 7, "tone": "friendly", "subject": "Payment Reminder"},
        2: {"days_overdue": 15, "tone": "firm", "subject": "Payment Past Due"},
        3: {"days_overdue": 30, "tone": "urgent", "subject": "Final Notice"},
        4: {"days_overdue": 45, "tone": "legal", "subject": "Account Suspended"},
    }

    def __init__(self, db: Session):
        self.db = db

    def get_overdue_invoices(self, days_overdue: int) -> List[Invoice]:
        """Get invoices overdue by specified days."""
        cutoff_date = datetime.utcnow().date() - timedelta(days=days_overdue)
        return (
            self.db.query(Invoice)
            .filter(
                Invoice.due_date <= cutoff_date,
                Invoice.status == "unpaid",
                Invoice.balance_due > 0,
            )
            .all()
        )

    def determine_dunning_level(self, invoice: Invoice) -> int:
        """Determine appropriate dunning level based on days overdue."""
        days_overdue = (datetime.utcnow().date() - invoice.due_date).days
        for level in sorted(self.DUNNING_LEVELS.keys(), reverse=True):
            if days_overdue >= self.DUNNING_LEVELS[level]["days_overdue"]:
                return level
        return 1

    def generate_dunning_letter(self, invoice: Invoice, level: int) -> Dict:
        """Generate dunning letter content for invoice."""
        config = self.DUNNING_LEVELS[level]
        days_overdue = (datetime.utcnow().date() - invoice.due_date).days

        templates = {
            "friendly": f"We noticed invoice #{invoice.invoice_number} is {days_overdue} days overdue. Please remit payment of ${invoice.balance_due:.2f} at your earliest convenience.",
            "firm": f"Invoice #{invoice.invoice_number} is now {days_overdue} days past due. Immediate payment of ${invoice.balance_due:.2f} is required to avoid service interruption.",
            "urgent": f"FINAL NOTICE: Invoice #{invoice.invoice_number} is {days_overdue} days overdue. Payment of ${invoice.balance_due:.2f} must be received within 5 business days.",
            "legal": f"Your account has been suspended due to non-payment. Invoice #{invoice.invoice_number} is {days_overdue} days overdue. Legal action may be pursued if payment of ${invoice.balance_due:.2f} is not received immediately.",
        }

        return {
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "customer_id": invoice.customer_id,
            "level": level,
            "subject": config["subject"],
            "body": templates[config["tone"]],
            "amount_due": float(invoice.balance_due),
            "days_overdue": days_overdue,
            "generated_at": datetime.utcnow(),
        }

    def process_dunning_cycle(self) -> Dict:
        """Process dunning cycle for all overdue invoices."""
        results = {"letters_generated": [], "customers_notified": set()}

        for level, config in self.DUNNING_LEVELS.items():
            invoices = self.get_overdue_invoices(config["days_overdue"])
            for invoice in invoices:
                current_level = self.determine_dunning_level(invoice)
                if current_level == level:
                    letter = self.generate_dunning_letter(invoice, level)
                    results["letters_generated"].append(letter)
                    results["customers_notified"].add(invoice.customer_id)

        return {
            "total_letters": len(results["letters_generated"]),
            "customers_notified": len(results["customers_notified"]),
            "letters": results["letters_generated"],
        }
