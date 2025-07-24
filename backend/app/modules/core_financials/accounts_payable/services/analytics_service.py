from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case, extract
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.modules.core_financials.accounts_payable.models import (
    Vendor, Invoice, Payment, InvoiceStatus, PaymentStatus
)
from app.modules.core_financials.accounts_payable.schemas import (
    APSummaryResponse, AgingReportResponse, AgingReportItem, VendorSummaryResponse
)

class APAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_ap_summary(self) -> APSummaryResponse:
        """Get summary statistics for accounts payable"""
        # Total outstanding across all vendors
        total_outstanding = self.db.query(
            func.coalesce(func.sum(Invoice.balance_due), Decimal("0.00"))
        ).filter(
            Invoice.status.in_([InvoiceStatus.APPROVED, InvoiceStatus.PARTIALLY_PAID])
        ).scalar() or Decimal("0.00")

        # Overdue amount (invoices past due date)
        overdue_amount = self.db.query(
            func.coalesce(func.sum(Invoice.balance_due), Decimal("0.00"))
        ).filter(
            Invoice.due_date < date.today(),
            Invoice.status.in_([InvoiceStatus.APPROVED, InvoiceStatus.PARTIALLY_PAID]),
            Invoice.balance_due > 0
        ).scalar() or Decimal("0.00")

        # This month's invoices
        today = date.today()
        first_day_of_month = today.replace(day=1)
        this_month_invoices = self.db.query(
            func.coalesce(func.sum(Invoice.total_amount), Decimal("0.00"))
        ).filter(
            Invoice.invoice_date >= first_day_of_month,
            Invoice.invoice_date <= today
        ).scalar() or Decimal("0.00")

        # Pending approval
        pending_approval = self.db.query(
            func.coalesce(func.sum(Invoice.total_amount), Decimal("0.00"))
        ).filter(
            Invoice.status == InvoiceStatus.PENDING_APPROVAL
        ).scalar() or Decimal("0.00")

        # Vendor counts
        total_vendors = self.db.query(Vendor).count()
        active_vendors = self.db.query(Vendor).filter(Vendor.status == "active").count()

        return APSummaryResponse(
            total_outstanding=total_outstanding,
            overdue_amount=overdue_amount,
            this_month_invoices=this_month_invoices,
            pending_approval=pending_approval,
            total_vendors=total_vendors,
            active_vendors=active_vendors
        )

    def get_aging_report(self, as_of_date: Optional[date] = None) -> AgingReportResponse:
        """Generate an aging report as of a specific date"""
        as_of_date = as_of_date or date.today()
        
        # Define aging buckets
        buckets = [
            (0, 30, "current"),
            (31, 60, "1-30_days"),
            (61, 90, "31-60_days"),
            (91, 120, "61-90_days"),
            (121, None, "over_120_days")
        ]
        
        # Base query for unpaid invoices
        base_query = self.db.query(
            Vendor.id.label("vendor_id"),
            Vendor.name.label("vendor_name"),
            Invoice.id.label("invoice_id"),
            Invoice.invoice_number,
            Invoice.invoice_date,
            Invoice.due_date,
            Invoice.total_amount,
            Invoice.balance_due,
            (as_of_date - Invoice.due_date).label("days_overdue")
        ).join(
            Vendor, Vendor.id == Invoice.vendor_id
        ).filter(
            Invoice.status.in_([InvoiceStatus.APPROVED, InvoiceStatus.PARTIALLY_PAID]),
            Invoice.balance_due > 0,
            Invoice.due_date <= as_of_date
        )
        
        # Get all unpaid invoices
        unpaid_invoices = base_query.all()
        
        # Process aging buckets for each invoice
        report_items = []
        for inv in unpaid_invoices:
            aging_buckets = {}
            days_overdue = (as_of_date - inv.due_date).days
            
            # Initialize all buckets to zero
            for _, _, bucket_name in buckets:
                aging_buckets[bucket_name] = Decimal("0.00")
            
            # Assign to appropriate bucket
            for min_days, max_days, bucket_name in buckets:
                if (min_days is None or days_overdue >= min_days) and \
                   (max_days is None or days_overdue <= max_days):
                    aging_buckets[bucket_name] = inv.balance_due
                    break
            
            report_items.append({
                "vendor_id": inv.vendor_id,
                "vendor_name": inv.vendor_name,
                "invoice_id": inv.invoice_id,
                "invoice_number": inv.invoice_number,
                "invoice_date": inv.invoice_date,
                "due_date": inv.due_date,
                "total_amount": inv.total_amount,
                "balance_due": inv.balance_due,
                "days_overdue": days_overdue,
                **aging_buckets
            })
        
        # Calculate totals
        totals = {
            "total_amount": sum(item["total_amount"] for item in report_items),
            "balance_due": sum(item["balance_due"] for item in report_items),
        }
        
        # Add bucket totals
        for _, _, bucket_name in buckets:
            totals[bucket_name] = sum(item[bucket_name] for item in report_items)
        
        return AgingReportResponse(
            report_date=as_of_date,
            items=[AgingReportItem(**item) for item in report_items],
            totals=totals
        )

    def get_vendor_summary(self, vendor_id: int) -> VendorSummaryResponse:
        """Get summary statistics for a specific vendor"""
        # Get vendor info
        vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise NotFoundError(f"Vendor with ID {vendor_id} not found")
        
        # Total outstanding
        total_outstanding = self.db.query(
            func.coalesce(func.sum(Invoice.balance_due), Decimal("0.00"))
        ).filter(
            Invoice.vendor_id == vendor_id,
            Invoice.status.in_([InvoiceStatus.APPROVED, InvoiceStatus.PARTIALLY_PAID])
        ).scalar() or Decimal("0.00")
        
        # Overdue amount
        overdue_amount = self.db.query(
            func.coalesce(func.sum(Invoice.balance_due), Decimal("0.00"))
        ).filter(
            Invoice.vendor_id == vendor_id,
            Invoice.due_date < date.today(),
            Invoice.status.in_([InvoiceStatus.APPROVED, InvoiceStatus.PARTIALLY_PAID]),
            Invoice.balance_due > 0
        ).scalar() or Decimal("0.00")
        
        # This year's spend
        this_year_start = date.today().replace(month=1, day=1)
        this_year_spend = self.db.query(
            func.coalesce(func.sum(Invoice.total_amount), Decimal("0.00"))
        ).filter(
            Invoice.vendor_id == vendor_id,
            Invoice.invoice_date >= this_year_start
        ).scalar() or Decimal("0.00")
        
        # Last payment date and amount
        last_payment = (
            self.db.query(Payment)
            .filter(
                Payment.vendor_id == vendor_id,
                Payment.status.in_([PaymentStatus.PROCESSED, PaymentStatus.APPLIED])
            )
            .order_by(Payment.payment_date.desc())
            .first()
        )
        
        # Open invoices count
        open_invoices_count = self.db.query(Invoice).filter(
            Invoice.vendor_id == vendor_id,
            Invoice.status.in_([InvoiceStatus.APPROVED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PENDING_APPROVAL])
        ).count()
        
        return VendorSummaryResponse(
            vendor_id=vendor.id,
            vendor_name=vendor.name,
            total_outstanding=total_outstanding,
            overdue_amount=overdue_amount,
            this_year_spend=this_year_spend,
            last_payment_date=last_payment.payment_date if last_payment else None,
            last_payment_amount=last_payment.amount if last_payment else Decimal("0.00"),
            open_invoices_count=open_invoices_count,
            credit_limit=vendor.credit_limit,
            available_credit=(vendor.credit_limit - total_outstanding) if vendor.credit_limit else None
        )
