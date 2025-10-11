"""
Advanced reconciliation features for multi-module integration
"""
from datetime import date
from decimal import Decimal
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import *
from app.services.base import BaseService

class AdvancedReconciliationService(BaseService):
    """Advanced reconciliation across all financial modules"""
    
    def __init__(self, db: Session):
        super().__init__(db, JournalEntry)
    
    def reconcile_ap_gl(self, company_id: UUID, as_of_date: date) -> Dict[str, Any]:
        """Reconcile AP balances with GL"""
        # AP balance from invoices
        ap_balance = self.db.query(func.sum(APInvoice.total_amount - APInvoice.paid_amount)).filter(
            APInvoice.company_id == company_id,
            APInvoice.invoice_date <= as_of_date
        ).scalar() or Decimal('0')
        
        # GL AP account balance
        ap_account = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.account_code == '2000'
        ).first()
        
        gl_balance = self.db.query(
            func.sum(JournalEntryLine.credit_amount - JournalEntryLine.debit_amount)
        ).join(JournalEntry).filter(
            JournalEntryLine.account_id == ap_account.id,
            JournalEntry.entry_date <= as_of_date,
            JournalEntry.status == 'posted'
        ).scalar() or Decimal('0')
        
        return {
            "ap_module_balance": float(ap_balance),
            "gl_balance": float(gl_balance),
            "difference": float(ap_balance - gl_balance),
            "is_reconciled": abs(ap_balance - gl_balance) < Decimal('0.01')
        }
    
    def reconcile_ar_gl(self, company_id: UUID, as_of_date: date) -> Dict[str, Any]:
        """Reconcile AR balances with GL"""
        # AR balance from invoices
        ar_balance = self.db.query(func.sum(ARInvoice.total_amount - ARInvoice.paid_amount)).filter(
            ARInvoice.company_id == company_id,
            ARInvoice.invoice_date <= as_of_date
        ).scalar() or Decimal('0')
        
        # GL AR account balance
        ar_account = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.account_code == '1200'
        ).first()
        
        gl_balance = self.db.query(
            func.sum(JournalEntryLine.debit_amount - JournalEntryLine.credit_amount)
        ).join(JournalEntry).filter(
            JournalEntryLine.account_id == ar_account.id,
            JournalEntry.entry_date <= as_of_date,
            JournalEntry.status == 'posted'
        ).scalar() or Decimal('0')
        
        return {
            "ar_module_balance": float(ar_balance),
            "gl_balance": float(gl_balance),
            "difference": float(ar_balance - gl_balance),
            "is_reconciled": abs(ar_balance - gl_balance) < Decimal('0.01')
        }
    
    def comprehensive_reconciliation(self, company_id: UUID, as_of_date: date) -> Dict[str, Any]:
        """Perform comprehensive reconciliation across all modules"""
        return {
            "as_of_date": as_of_date.isoformat(),
            "ap_reconciliation": self.reconcile_ap_gl(company_id, as_of_date),
            "ar_reconciliation": self.reconcile_ar_gl(company_id, as_of_date),
            "overall_status": "reconciled" if all([
                self.reconcile_ap_gl(company_id, as_of_date)["is_reconciled"],
                self.reconcile_ar_gl(company_id, as_of_date)["is_reconciled"]
            ]) else "discrepancies_found"
        }