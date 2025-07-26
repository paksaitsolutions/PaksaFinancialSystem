"""GL Integration Service for cross-module data consistency"""
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.modules.core_financials.general_ledger.models import Account, JournalEntry, JournalEntryLine
from app.modules.core_financials.general_ledger.services import JournalEntryService

class GLIntegrationService:
    """Service for GL integration with other modules"""
    
    def __init__(self):
        self.journal_service = JournalEntryService()
    
    async def create_ap_journal_entry(self, db: AsyncSession, ap_invoice_data: Dict) -> JournalEntry:
        """Create journal entry from AP invoice"""
        entry_data = {
            "entry_date": ap_invoice_data["invoice_date"],
            "description": f"AP Invoice: {ap_invoice_data['invoice_number']}",
            "reference": ap_invoice_data["invoice_number"],
            "lines": [
                {
                    "account_id": ap_invoice_data["expense_account_id"],
                    "description": f"Expense - {ap_invoice_data['vendor_name']}",
                    "debit_amount": ap_invoice_data["amount"],
                    "credit_amount": 0
                },
                {
                    "account_id": ap_invoice_data["ap_account_id"],
                    "description": f"AP - {ap_invoice_data['vendor_name']}",
                    "debit_amount": 0,
                    "credit_amount": ap_invoice_data["amount"]
                }
            ]
        }
        return await self.journal_service.create_journal_entry(db, entry_data)
    
    async def create_ar_journal_entry(self, db: AsyncSession, ar_invoice_data: Dict) -> JournalEntry:
        """Create journal entry from AR invoice"""
        entry_data = {
            "entry_date": ar_invoice_data["invoice_date"],
            "description": f"AR Invoice: {ar_invoice_data['invoice_number']}",
            "reference": ar_invoice_data["invoice_number"],
            "lines": [
                {
                    "account_id": ar_invoice_data["ar_account_id"],
                    "description": f"AR - {ar_invoice_data['customer_name']}",
                    "debit_amount": ar_invoice_data["amount"],
                    "credit_amount": 0
                },
                {
                    "account_id": ar_invoice_data["revenue_account_id"],
                    "description": f"Revenue - {ar_invoice_data['customer_name']}",
                    "debit_amount": 0,
                    "credit_amount": ar_invoice_data["amount"]
                }
            ]
        }
        return await self.journal_service.create_journal_entry(db, entry_data)
    
    async def create_payroll_journal_entry(self, db: AsyncSession, payroll_data: Dict) -> JournalEntry:
        """Create journal entry from payroll processing"""
        lines = [
            {
                "account_id": payroll_data["salary_expense_account_id"],
                "description": f"Payroll - {payroll_data['period']}",
                "debit_amount": payroll_data["gross_pay"],
                "credit_amount": 0
            },
            {
                "account_id": payroll_data["cash_account_id"],
                "description": f"Net Pay - {payroll_data['period']}",
                "debit_amount": 0,
                "credit_amount": payroll_data["net_pay"]
            }
        ]
        
        # Add tax withholdings
        for tax in payroll_data.get("tax_withholdings", []):
            lines.append({
                "account_id": tax["liability_account_id"],
                "description": f"{tax['tax_type']} Withholding",
                "debit_amount": 0,
                "credit_amount": tax["amount"]
            })
        
        entry_data = {
            "entry_date": payroll_data["pay_date"],
            "description": f"Payroll - {payroll_data['period']}",
            "reference": payroll_data["payroll_id"],
            "lines": lines
        }
        return await self.journal_service.create_journal_entry(db, entry_data)
    
    async def create_budget_variance_entry(self, db: AsyncSession, variance_data: Dict) -> Optional[JournalEntry]:
        """Create journal entry for budget variances if needed"""
        if abs(variance_data["variance_amount"]) < 0.01:
            return None
            
        entry_data = {
            "entry_date": variance_data["period_end"],
            "description": f"Budget Variance - {variance_data['account_name']}",
            "reference": f"BV-{variance_data['budget_id']}",
            "lines": [
                {
                    "account_id": variance_data["account_id"],
                    "description": f"Budget Variance Adjustment",
                    "debit_amount": max(0, variance_data["variance_amount"]),
                    "credit_amount": max(0, -variance_data["variance_amount"])
                },
                {
                    "account_id": variance_data["variance_account_id"],
                    "description": f"Budget Variance",
                    "debit_amount": max(0, -variance_data["variance_amount"]),
                    "credit_amount": max(0, variance_data["variance_amount"])
                }
            ]
        }
        return await self.journal_service.create_journal_entry(db, entry_data)
    
    async def create_asset_depreciation_entry(self, db: AsyncSession, depreciation_data: Dict) -> JournalEntry:
        """Create journal entry for asset depreciation"""
        entry_data = {
            "entry_date": depreciation_data["depreciation_date"],
            "description": f"Depreciation - {depreciation_data['asset_name']}",
            "reference": f"DEP-{depreciation_data['asset_id']}",
            "lines": [
                {
                    "account_id": depreciation_data["depreciation_expense_account_id"],
                    "description": f"Depreciation Expense - {depreciation_data['asset_name']}",
                    "debit_amount": depreciation_data["depreciation_amount"],
                    "credit_amount": 0
                },
                {
                    "account_id": depreciation_data["accumulated_depreciation_account_id"],
                    "description": f"Accumulated Depreciation - {depreciation_data['asset_name']}",
                    "debit_amount": 0,
                    "credit_amount": depreciation_data["depreciation_amount"]
                }
            ]
        }
        return await self.journal_service.create_journal_entry(db, entry_data)
    
    async def validate_account_balance(self, db: AsyncSession, account_id: str) -> Dict:
        """Validate account balance consistency"""
        # Get account
        account_result = await db.execute(select(Account).where(Account.id == account_id))
        account = account_result.scalar_one_or_none()
        
        if not account:
            return {"valid": False, "error": "Account not found"}
        
        # Calculate balance from journal entries
        lines_result = await db.execute(
            select(JournalEntryLine)
            .join(JournalEntry)
            .where(
                and_(
                    JournalEntryLine.account_id == account_id,
                    JournalEntry.status == 'posted'
                )
            )
        )
        lines = lines_result.scalars().all()
        
        calculated_balance = sum(line.debit_amount - line.credit_amount for line in lines)
        
        return {
            "valid": abs(account.balance - calculated_balance) < 0.01,
            "account_balance": account.balance,
            "calculated_balance": calculated_balance,
            "difference": account.balance - calculated_balance
        }
    
    async def get_integration_status(self, db: AsyncSession) -> Dict:
        """Get overall GL integration status"""
        # Check for unposted entries
        unposted_result = await db.execute(
            select(JournalEntry).where(JournalEntry.status == 'draft')
        )
        unposted_count = len(unposted_result.scalars().all())
        
        # Check for out-of-balance entries
        entries_result = await db.execute(select(JournalEntry))
        entries = entries_result.scalars().all()
        
        out_of_balance = []
        for entry in entries:
            if abs(entry.total_debit - entry.total_credit) > 0.01:
                out_of_balance.append({
                    "entry_id": entry.id,
                    "entry_number": entry.entry_number,
                    "difference": entry.total_debit - entry.total_credit
                })
        
        return {
            "unposted_entries": unposted_count,
            "out_of_balance_entries": len(out_of_balance),
            "balance_issues": out_of_balance,
            "integration_healthy": unposted_count == 0 and len(out_of_balance) == 0
        }