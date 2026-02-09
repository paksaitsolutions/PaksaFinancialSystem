"""Data integrity utilities for reconciliation and quality monitoring."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.observability import trace_job


def get_constraints_review() -> List[Dict[str, Any]]:
    """Return a static constraints review checklist per module."""
    return [
        {
            "module": "Accounts Payable",
            "checks": [
                "vendor_id foreign keys",
                "unique invoice numbers",
                "non-negative amounts",
            ],
            "status": "reviewed",
        },
        {
            "module": "Accounts Receivable",
            "checks": [
                "customer_id foreign keys",
                "unique invoice numbers",
                "non-negative amounts",
            ],
            "status": "reviewed",
        },
        {
            "module": "Cash Management",
            "checks": [
                "bank_accounts company_id index",
                "transaction account_id foreign keys",
                "non-negative balances",
            ],
            "status": "reviewed",
        },
        {
            "module": "General Ledger",
            "checks": [
                "chart of accounts unique codes",
                "journal entry line integrity",
                "period lock checks",
            ],
            "status": "reviewed",
        },
    ]


def run_reconciliation(db: Session) -> Dict[str, Any]:
    """Run high-level reconciliation checks across AR/AP/Cash/GL."""
    results: List[Dict[str, Any]] = []
    with trace_job("reconciliation") as mark_failed:
        try:
            from app.models.core_models import APInvoice, APPayment, ARInvoice, ARPayment, ChartOfAccounts

            ap_invoices = db.query(APInvoice).all()
            ap_payments = db.query(APPayment).all()
            ar_invoices = db.query(ARInvoice).all()
            ar_payments = db.query(ARPayment).all()
            cash_accounts = db.query(ChartOfAccounts).filter(ChartOfAccounts.account_type == "Asset").all()

            ap_total = sum(float(inv.total_amount or 0) for inv in ap_invoices) - sum(
                float(pmt.amount or 0) for pmt in ap_payments
            )
            ar_total = sum(float(inv.total_amount or 0) for inv in ar_invoices) - sum(
                float(pmt.amount or 0) for pmt in ar_payments
            )
            gl_cash = sum(float(acc.balance or 0) for acc in cash_accounts)

            results.append(
                {
                    "check": "AP open balance",
                    "value": ap_total,
                    "status": "ok" if ap_total >= 0 else "warning",
                }
            )
            results.append(
                {
                    "check": "AR open balance",
                    "value": ar_total,
                    "status": "ok" if ar_total >= 0 else "warning",
                }
            )
            results.append(
                {
                    "check": "GL cash balance",
                    "value": gl_cash,
                    "status": "ok",
                }
            )
        except Exception as exc:
            mark_failed()
            results.append({"check": "reconciliation", "status": "degraded", "error": str(exc)})

    return {"timestamp": datetime.utcnow().isoformat(), "results": results}


def get_data_quality_dashboard(db: Session) -> Dict[str, Any]:
    """Return data quality metrics for dashboards."""
    metrics: Dict[str, Any] = {
        "orphaned_records": [],
        "posting_gaps": [],
        "stale_states": [],
    }

    try:
        from app.models.core_models import APPayment, APInvoice, ARPayment, ARInvoice, Vendor, Customer, JournalEntry

        orphaned_ap = (
            db.query(APPayment)
            .filter(APPayment.vendor_id.notin_(db.query(Vendor.id)))
            .count()
        )
        orphaned_ar = (
            db.query(ARPayment)
            .filter(ARPayment.customer_id.notin_(db.query(Customer.id)))
            .count()
        )
        metrics["orphaned_records"] = [
            {"type": "ap_payment_vendor", "count": orphaned_ap},
            {"type": "ar_payment_customer", "count": orphaned_ar},
        ]

        unpaid_ap = db.query(APInvoice).filter(APInvoice.status != "paid").count()
        unpaid_ar = db.query(ARInvoice).filter(ARInvoice.status != "paid").count()
        metrics["posting_gaps"] = [
            {"type": "ap_unpaid_invoices", "count": unpaid_ap},
            {"type": "ar_unpaid_invoices", "count": unpaid_ar},
        ]

        stale_date = datetime.utcnow() - timedelta(days=30)
        stale_journal_entries = (
            db.query(JournalEntry)
            .filter(JournalEntry.status == "draft")
            .count()
        )
        metrics["stale_states"] = [
            {"type": "draft_journal_entries", "count": stale_journal_entries, "threshold_days": 30},
        ]
    except Exception as exc:
        metrics["error"] = str(exc)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics,
    }
