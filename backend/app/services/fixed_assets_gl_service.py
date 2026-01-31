"""
Fixed Assets GL Integration Service
"""
from datetime import datetime

from decimal import Decimal
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import FixedAsset, AssetDepreciation, JournalEntry, JournalEntryLine, ChartOfAccounts
from app.services.base import BaseService


class FixedAssetsGLService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, FixedAsset)
    
    def post_asset_purchase_to_gl(self, asset: FixedAsset) -> JournalEntry:
        
        journal_entry = JournalEntry(
            company_id=asset.company_id,
            entry_number=f"FA-{asset.asset_number}",
            entry_date=asset.purchase_date,
            description=f"Fixed Asset Purchase {asset.asset_name}",
            source_module="FIXED_ASSETS",
            status="posted"
        )
        self.db.add(journal_entry)
        self.db.flush()
        
        # Get accounts
        asset_account = self._get_account(asset.company_id, "1500", "Fixed Assets")
        cash_account = self._get_account(asset.company_id, "1000", "Cash")
        
        # Dr. Fixed Assets
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=asset_account.id,
            description=f"Asset Purchase - {asset.asset_name}",
            debit_amount=asset.purchase_cost,
            credit_amount=Decimal('0'),
            line_number=1
        ))
        
        # Cr. Cash
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=cash_account.id,
            description="Cash Payment",
            debit_amount=Decimal('0'),
            credit_amount=asset.purchase_cost,
            line_number=2
        ))
        
        journal_entry.total_debit = asset.purchase_cost
        journal_entry.total_credit = asset.purchase_cost
        
        return journal_entry
    
    def post_depreciation_to_gl(self, asset: FixedAsset, depreciation_amount: Decimal) -> JournalEntry:
        
        journal_entry = JournalEntry(
            company_id=asset.company_id,
            entry_number=f"DEP-{asset.asset_number}-{datetime.now().strftime('%Y%m')}",
            entry_date=datetime.now().date(),
            description=f"Depreciation - {asset.asset_name}",
            source_module="FIXED_ASSETS",
            status="posted"
        )
        self.db.add(journal_entry)
        self.db.flush()
        
        # Get accounts
        depreciation_expense = self._get_account(asset.company_id, "6200", "Depreciation Expense")
        accumulated_depreciation = self._get_account(asset.company_id, "1510", "Accumulated Depreciation")
        
        # Dr. Depreciation Expense
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=depreciation_expense.id,
            description="Depreciation Expense",
            debit_amount=depreciation_amount,
            credit_amount=Decimal('0'),
            line_number=1
        ))
        
        # Cr. Accumulated Depreciation
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=accumulated_depreciation.id,
            description="Accumulated Depreciation",
            debit_amount=Decimal('0'),
            credit_amount=depreciation_amount,
            line_number=2
        ))
        
        # Create depreciation record
        depreciation_record = AssetDepreciation(
            asset_id=asset.id,
            depreciation_date=datetime.now().date(),
            depreciation_amount=depreciation_amount,
            accumulated_depreciation=asset.accumulated_depreciation + depreciation_amount,
            book_value=asset.purchase_cost - (asset.accumulated_depreciation + depreciation_amount)
        )
        self.db.add(depreciation_record)
        
        # Update asset
        asset.accumulated_depreciation += depreciation_amount
        asset.current_value = asset.purchase_cost - asset.accumulated_depreciation
        
        journal_entry.total_debit = depreciation_amount
        journal_entry.total_credit = depreciation_amount
        
        return journal_entry
    
    def post_asset_disposal_to_gl(self, asset: FixedAsset, disposal_amount: Decimal, disposal_date: datetime = None) -> JournalEntry:
        
        if not disposal_date:
            disposal_date = datetime.now().date()
        
        journal_entry = JournalEntry(
            company_id=asset.company_id,
            entry_number=f"DISP-{asset.asset_number}",
            entry_date=disposal_date,
            description=f"Asset Disposal - {asset.asset_name}",
            source_module="FIXED_ASSETS",
            status="posted"
        )
        self.db.add(journal_entry)
        self.db.flush()
        
        # Get accounts
        cash_account = self._get_account(asset.company_id, "1000", "Cash")
        asset_account = self._get_account(asset.company_id, "1500", "Fixed Assets")
        accumulated_depreciation = self._get_account(asset.company_id, "1510", "Accumulated Depreciation")
        
        # Calculate gain/loss
        book_value = asset.purchase_cost - asset.accumulated_depreciation
        gain_loss = disposal_amount - book_value
        
        line_number = 1
        
        # Dr. Cash (disposal amount)
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=cash_account.id,
            description="Cash from Asset Disposal",
            debit_amount=disposal_amount,
            credit_amount=Decimal('0'),
            line_number=line_number
        ))
        line_number += 1
        
        # Dr. Accumulated Depreciation
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=accumulated_depreciation.id,
            description="Remove Accumulated Depreciation",
            debit_amount=asset.accumulated_depreciation,
            credit_amount=Decimal('0'),
            line_number=line_number
        ))
        line_number += 1
        
        # Handle gain/loss
        if gain_loss != 0:
            gain_loss_account = self._get_account(
                asset.company_id, 
                "7100" if gain_loss > 0 else "6300", 
                "Gain on Asset Disposal" if gain_loss > 0 else "Loss on Asset Disposal"
            )
            
            if gain_loss > 0:  # Gain - Credit
                self.db.add(JournalEntryLine(
                    journal_entry_id=journal_entry.id,
                    account_id=gain_loss_account.id,
                    description="Gain on Asset Disposal",
                    debit_amount=Decimal('0'),
                    credit_amount=abs(gain_loss),
                    line_number=line_number
                ))
            else:  # Loss - Debit
                self.db.add(JournalEntryLine(
                    journal_entry_id=journal_entry.id,
                    account_id=gain_loss_account.id,
                    description="Loss on Asset Disposal",
                    debit_amount=abs(gain_loss),
                    credit_amount=Decimal('0'),
                    line_number=line_number
                ))
            line_number += 1
        
        # Cr. Fixed Assets (original cost)
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=asset_account.id,
            description=f"Remove Asset - {asset.asset_name}",
            debit_amount=Decimal('0'),
            credit_amount=asset.purchase_cost,
            line_number=line_number
        ))
        
        # Update totals
        total_debits = disposal_amount + asset.accumulated_depreciation + (abs(gain_loss) if gain_loss < 0 else Decimal('0'))
        total_credits = asset.purchase_cost + (abs(gain_loss) if gain_loss > 0 else Decimal('0'))
        
        journal_entry.total_debit = total_debits
        journal_entry.total_credit = total_credits
        
        # Update asset status
        asset.status = "disposed"
        
        return journal_entry
    
    def post_maintenance_cost_to_ap(self, asset: FixedAsset, maintenance_amount: Decimal, vendor_id: UUID, description: str) -> JournalEntry:
        from app.models import APInvoice, APInvoiceLineItem, Vendor
        
        # Create AP Invoice
        vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise ValueError("Vendor not found")
        
        invoice_number = f"MAINT-{asset.asset_number}-{datetime.now().strftime('%Y%m%d')}"
        
        ap_invoice = APInvoice(
            company_id=asset.company_id,
            vendor_id=vendor_id,
            invoice_number=invoice_number,
            invoice_date=datetime.now().date(),
            due_date=datetime.now().date(),
            subtotal=maintenance_amount,
            total_amount=maintenance_amount,
            status="approved"
        )
        self.db.add(ap_invoice)
        self.db.flush()
        
        # Get maintenance expense account
        maintenance_account = self._get_account(asset.company_id, "6250", "Asset Maintenance Expense")
        
        # Create invoice line item
        line_item = APInvoiceLineItem(
            invoice_id=ap_invoice.id,
            account_id=maintenance_account.id,
            description=f"Maintenance - {asset.asset_name}: {description}",
            quantity=Decimal('1'),
            unit_price=maintenance_amount,
            amount=maintenance_amount
        )
        self.db.add(line_item)
        
        # Create GL Journal Entry
        journal_entry = JournalEntry(
            company_id=asset.company_id,
            entry_number=f"MAINT-{asset.asset_number}-{datetime.now().strftime('%Y%m%d')}",
            entry_date=datetime.now().date(),
            description=f"Asset Maintenance - {asset.asset_name}",
            source_module="FIXED_ASSETS",
            status="posted"
        )
        self.db.add(journal_entry)
        self.db.flush()
        
        # Get AP account
        ap_account = self._get_account(asset.company_id, "2000", "Accounts Payable")
        
        # Dr. Maintenance Expense
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=maintenance_account.id,
            description=f"Maintenance Expense - {asset.asset_name}",
            debit_amount=maintenance_amount,
            credit_amount=Decimal('0'),
            line_number=1
        ))
        
        # Cr. Accounts Payable
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=ap_account.id,
            description=f"AP - {vendor.vendor_name}",
            debit_amount=Decimal('0'),
            credit_amount=maintenance_amount,
            line_number=2
        ))
        
        journal_entry.total_debit = maintenance_amount
        journal_entry.total_credit = maintenance_amount
        
        return journal_entry
    
    def _get_account(self, company_id: UUID, code: str, name: str) -> ChartOfAccounts:
        account = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.account_code == code
        ).first()
        
        if not account:
            if code.startswith("1"):
                account_type = "Asset"
                normal_balance = "Debit"
            elif code.startswith("6"):
                account_type = "Expense"
                normal_balance = "Debit"
            else:
                account_type = "Liability"
                normal_balance = "Credit"
                
            account = ChartOfAccounts(
                company_id=company_id,
                account_code=code,
                account_name=name,
                account_type=account_type,
                normal_balance=normal_balance
            )
            self.db.add(account)
            self.db.flush()
        
        return account