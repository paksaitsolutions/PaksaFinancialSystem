"""
Consolidated Financial Reporting Service
Consolidates data from all modules (AP, AR, Cash, Payroll, GL) for comprehensive reporting.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models import (
    ChartOfAccounts,
    JournalEntry,
    JournalEntryLine,
    APInvoice,
    APPayment,
    ARInvoice,
    ARPayment,
    PayrollRun,
    PayrollEntry,
    BankTransaction,
    Company
)
from app.services.base import BaseService


class ConsolidatedReportingService(BaseService):
    """Service for generating consolidated financial reports across all modules."""
    
    def __init__(self, db: Session):
        super().__init__(db, JournalEntry)
    
    def generate_module_activity_report(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Generate a report showing activity across all modules."""
        
        # AP Module Activity
        ap_invoices = self.db.query(func.count(APInvoice.id), func.sum(APInvoice.total_amount)).filter(
            APInvoice.company_id == company_id,
            APInvoice.invoice_date.between(start_date, end_date)
        ).first()
        
        ap_payments = self.db.query(func.count(APPayment.id), func.sum(APPayment.amount)).filter(
            APPayment.company_id == company_id,
            APPayment.payment_date.between(start_date, end_date)
        ).first()
        
        # AR Module Activity
        ar_invoices = self.db.query(func.count(ARInvoice.id), func.sum(ARInvoice.total_amount)).filter(
            ARInvoice.company_id == company_id,
            ARInvoice.invoice_date.between(start_date, end_date)
        ).first()
        
        ar_payments = self.db.query(func.count(ARPayment.id), func.sum(ARPayment.amount)).filter(
            ARPayment.company_id == company_id,
            ARPayment.payment_date.between(start_date, end_date)
        ).first()
        
        # Payroll Activity
        payroll_runs = self.db.query(func.count(PayrollRun.id), func.sum(PayrollRun.total_gross_pay)).filter(
            PayrollRun.company_id == company_id,
            PayrollRun.pay_period_start.between(start_date, end_date)
        ).first()
        
        # Cash Activity
        bank_transactions = self.db.query(
            func.count(BankTransaction.id),
            func.sum(BankTransaction.amount)
        ).filter(
            BankTransaction.company_id == company_id,
            BankTransaction.transaction_date.between(start_date, end_date)
        ).first()
        
        # GL Journal Entries by Module
        gl_entries_by_module = self.db.query(
            JournalEntry.source_module,
            func.count(JournalEntry.id),
            func.sum(JournalEntryLine.debit_amount)
        ).join(JournalEntryLine).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.entry_date.between(start_date, end_date),
            JournalEntry.status == 'posted'
        ).group_by(JournalEntry.source_module).all()
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "modules": {
                "accounts_payable": {
                    "invoices_count": ap_invoices[0] or 0,
                    "invoices_amount": float(ap_invoices[1] or 0),
                    "payments_count": ap_payments[0] or 0,
                    "payments_amount": float(ap_payments[1] or 0)
                },
                "accounts_receivable": {
                    "invoices_count": ar_invoices[0] or 0,
                    "invoices_amount": float(ar_invoices[1] or 0),
                    "payments_count": ar_payments[0] or 0,
                    "payments_amount": float(ar_payments[1] or 0)
                },
                "payroll": {
                    "runs_count": payroll_runs[0] or 0,
                    "total_gross_pay": float(payroll_runs[1] or 0)
                },
                "cash_management": {
                    "transactions_count": bank_transactions[0] or 0,
                    "transactions_amount": float(bank_transactions[1] or 0)
                },
                "general_ledger": {
                    "entries_by_module": [
                        {
                            "module": entry[0],
                            "entries_count": entry[1],
                            "total_amount": float(entry[2] or 0)
                        }
                        for entry in gl_entries_by_module
                    ]
                }
            }
        }
    
    def generate_account_activity_summary(
        self,
        company_id: UUID,
        start_date: date,
        end_date: date,
        account_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate summary of account activity across all modules."""
        
        query = self.db.query(
            ChartOfAccounts.account_type,
            ChartOfAccounts.account_code,
            ChartOfAccounts.account_name,
            JournalEntry.source_module,
            func.count(JournalEntryLine.id).label('transaction_count'),
            func.sum(JournalEntryLine.debit_amount).label('total_debits'),
            func.sum(JournalEntryLine.credit_amount).label('total_credits')
        ).join(
            JournalEntryLine, ChartOfAccounts.id == JournalEntryLine.account_id
        ).join(
            JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id
        ).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.entry_date.between(start_date, end_date),
            JournalEntry.status == 'posted',
            ChartOfAccounts.is_active == True
        )
        
        if account_types:
            query = query.filter(ChartOfAccounts.account_type.in_(account_types))
        
        results = query.group_by(
            ChartOfAccounts.account_type,
            ChartOfAccounts.account_code,
            ChartOfAccounts.account_name,
            JournalEntry.source_module
        ).all()
        
        # Group by account type
        account_summary = {}
        for result in results:
            account_type = result.account_type
            if account_type not in account_summary:
                account_summary[account_type] = {
                    "accounts": {},
                    "totals": {
                        "transaction_count": 0,
                        "total_debits": 0,
                        "total_credits": 0
                    }
                }
            
            account_key = f"{result.account_code} - {result.account_name}"
            if account_key not in account_summary[account_type]["accounts"]:
                account_summary[account_type]["accounts"][account_key] = {
                    "modules": {},
                    "totals": {
                        "transaction_count": 0,
                        "total_debits": 0,
                        "total_credits": 0
                    }
                }
            
            # Add module activity
            account_summary[account_type]["accounts"][account_key]["modules"][result.source_module] = {
                "transaction_count": result.transaction_count,
                "total_debits": float(result.total_debits or 0),
                "total_credits": float(result.total_credits or 0)
            }
            
            # Update account totals
            account_summary[account_type]["accounts"][account_key]["totals"]["transaction_count"] += result.transaction_count
            account_summary[account_type]["accounts"][account_key]["totals"]["total_debits"] += float(result.total_debits or 0)
            account_summary[account_type]["accounts"][account_key]["totals"]["total_credits"] += float(result.total_credits or 0)
            
            # Update account type totals
            account_summary[account_type]["totals"]["transaction_count"] += result.transaction_count
            account_summary[account_type]["totals"]["total_debits"] += float(result.total_debits or 0)
            account_summary[account_type]["totals"]["total_credits"] += float(result.total_credits or 0)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "account_types_included": account_types or ["All"],
            "account_summary": account_summary
        }
    
    def generate_integration_health_report(self, company_id: UUID) -> Dict[str, Any]:
        """Generate a report showing the health of module integrations."""
        
        # Check for orphaned records (transactions without GL entries)
        ap_without_gl = self.db.query(func.count(APInvoice.id)).outerjoin(
            JournalEntry, and_(
                JournalEntry.source_id == APInvoice.id,
                JournalEntry.source_module == 'AP'
            )
        ).filter(
            APInvoice.company_id == company_id,
            JournalEntry.id.is_(None)
        ).scalar()
        
        ar_without_gl = self.db.query(func.count(ARInvoice.id)).outerjoin(
            JournalEntry, and_(
                JournalEntry.source_id == ARInvoice.id,
                JournalEntry.source_module == 'AR'
            )
        ).filter(
            ARInvoice.company_id == company_id,
            JournalEntry.id.is_(None)
        ).scalar()
        
        # Check for GL entries without source records
        orphaned_gl_entries = self.db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.source_id.isnot(None),
            JournalEntry.source_module.isnot(None)
        ).scalar()
        
        # Module integration status
        modules_with_gl = self.db.query(
            JournalEntry.source_module,
            func.count(JournalEntry.id)
        ).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.source_module.isnot(None)
        ).group_by(JournalEntry.source_module).all()
        
        return {
            "integration_health": {
                "orphaned_records": {
                    "ap_invoices_without_gl": ap_without_gl,
                    "ar_invoices_without_gl": ar_without_gl,
                    "total_orphaned": ap_without_gl + ar_without_gl
                },
                "modules_integrated": {
                    module: count for module, count in modules_with_gl
                },
                "health_score": self._calculate_integration_health_score(
                    ap_without_gl, ar_without_gl, len(modules_with_gl)
                )
            },
            "recommendations": self._generate_integration_recommendations(
                ap_without_gl, ar_without_gl, modules_with_gl
            )
        }
    
    def _calculate_integration_health_score(
        self, 
        ap_orphaned: int, 
        ar_orphaned: int, 
        integrated_modules: int
    ) -> float:
        """Calculate a health score for module integration (0-100)."""
        base_score = 100.0
        
        # Deduct points for orphaned records
        orphaned_penalty = (ap_orphaned + ar_orphaned) * 2
        base_score -= min(orphaned_penalty, 50)  # Max 50 point deduction
        
        # Add points for integrated modules
        integration_bonus = integrated_modules * 10
        base_score += min(integration_bonus, 30)  # Max 30 point bonus
        
        return max(0, min(100, base_score))
    
    def _generate_integration_recommendations(
        self, 
        ap_orphaned: int, 
        ar_orphaned: int, 
        modules_with_gl: List
    ) -> List[str]:
        """Generate recommendations for improving integration."""
        recommendations = []
        
        if ap_orphaned > 0:
            recommendations.append(f"Fix {ap_orphaned} AP invoices missing GL entries")
        
        if ar_orphaned > 0:
            recommendations.append(f"Fix {ar_orphaned} AR invoices missing GL entries")
        
        expected_modules = ['AP', 'AR', 'PAYROLL', 'CASH']
        integrated_module_names = [m[0] for m in modules_with_gl]
        missing_modules = set(expected_modules) - set(integrated_module_names)
        
        if missing_modules:
            recommendations.append(f"Enable GL integration for modules: {', '.join(missing_modules)}")
        
        if not recommendations:
            recommendations.append("All modules are properly integrated with GL")
        
        return recommendations