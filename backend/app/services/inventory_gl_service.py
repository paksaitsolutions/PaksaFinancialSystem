"""
Inventory GL Integration Service
"""
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import InventoryItem, PurchaseOrder, JournalEntry, JournalEntryLine, ChartOfAccounts
from app.services.base import BaseService

class InventoryGLService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, InventoryItem)
    
    def post_inventory_receipt_to_gl(self, po: PurchaseOrder) -> JournalEntry:
        """Post inventory receipt to GL"""
        
        journal_entry = JournalEntry(
            company_id=po.company_id,
            entry_number=f"INV-{po.po_number}",
            entry_date=po.po_date,
            description=f"Inventory Receipt PO {po.po_number}",
            source_module="INVENTORY",
            status="posted"
        )
        self.db.add(journal_entry)
        self.db.flush()
        
        # Get accounts
        inventory_account = self._get_account(po.company_id, "1300", "Inventory")
        ap_account = self._get_account(po.company_id, "2000", "Accounts Payable")
        
        # Dr. Inventory
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=inventory_account.id,
            description="Inventory Receipt",
            debit_amount=po.total_amount,
            credit_amount=Decimal('0'),
            line_number=1
        ))
        
        # Cr. Accounts Payable
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=ap_account.id,
            description="Accounts Payable",
            debit_amount=Decimal('0'),
            credit_amount=po.total_amount,
            line_number=2
        ))
        
        journal_entry.total_debit = po.total_amount
        journal_entry.total_credit = po.total_amount
        
        return journal_entry
    
    def post_inventory_issue_to_gl(self, item: InventoryItem, quantity: Decimal, cost: Decimal) -> JournalEntry:
        """Post inventory issue to GL"""
        
        total_cost = quantity * cost
        
        journal_entry = JournalEntry(
            company_id=item.company_id,
            entry_number=f"ISSUE-{item.item_code}",
            entry_date=datetime.utcnow().date(),
            description=f"Inventory Issue {item.item_name}",
            source_module="INVENTORY",
            status="posted"
        )
        self.db.add(journal_entry)
        self.db.flush()
        
        # Get accounts
        cogs_account = self._get_account(item.company_id, "5000", "Cost of Goods Sold")
        inventory_account = self._get_account(item.company_id, "1300", "Inventory")
        
        # Dr. COGS
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=cogs_account.id,
            description="Cost of Goods Sold",
            debit_amount=total_cost,
            credit_amount=Decimal('0'),
            line_number=1
        ))
        
        # Cr. Inventory
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=inventory_account.id,
            description="Inventory",
            debit_amount=Decimal('0'),
            credit_amount=total_cost,
            line_number=2
        ))
        
        journal_entry.total_debit = total_cost
        journal_entry.total_credit = total_cost
        
        return journal_entry
    
    def post_inventory_adjustment_to_gl(self, item: InventoryItem, adjustment_quantity: Decimal, adjustment_reason: str) -> JournalEntry:
        """Post inventory adjustment to GL"""
        from datetime import datetime
        
        adjustment_value = adjustment_quantity * item.unit_cost
        
        journal_entry = JournalEntry(
            company_id=item.company_id,
            entry_number=f"ADJ-{item.item_code}-{datetime.now().strftime('%Y%m%d')}",
            entry_date=datetime.now().date(),
            description=f"Inventory Adjustment - {item.item_name}: {adjustment_reason}",
            source_module="INVENTORY",
            status="posted"
        )
        self.db.add(journal_entry)
        self.db.flush()
        
        # Get accounts
        inventory_account = self._get_account(item.company_id, "1300", "Inventory")
        adjustment_account = self._get_account(item.company_id, "6400", "Inventory Adjustment Expense")
        
        if adjustment_quantity > 0:  # Positive adjustment (increase inventory)
            # Dr. Inventory
            self.db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=inventory_account.id,
                description=f"Inventory Increase - {item.item_name}",
                debit_amount=abs(adjustment_value),
                credit_amount=Decimal('0'),
                line_number=1
            ))
            
            # Cr. Inventory Adjustment (contra expense)
            self.db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=adjustment_account.id,
                description=f"Inventory Adjustment - {adjustment_reason}",
                debit_amount=Decimal('0'),
                credit_amount=abs(adjustment_value),
                line_number=2
            ))
        else:  # Negative adjustment (decrease inventory)
            # Dr. Inventory Adjustment Expense
            self.db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=adjustment_account.id,
                description=f"Inventory Adjustment - {adjustment_reason}",
                debit_amount=abs(adjustment_value),
                credit_amount=Decimal('0'),
                line_number=1
            ))
            
            # Cr. Inventory
            self.db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=inventory_account.id,
                description=f"Inventory Decrease - {item.item_name}",
                debit_amount=Decimal('0'),
                credit_amount=abs(adjustment_value),
                line_number=2
            ))
        
        journal_entry.total_debit = abs(adjustment_value)
        journal_entry.total_credit = abs(adjustment_value)
        
        # Update inventory quantity
        item.quantity_on_hand += adjustment_quantity
        
        return journal_entry
    
    def _get_account(self, company_id: UUID, code: str, name: str) -> ChartOfAccounts:
        """Get or create chart of accounts"""
        account = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.account_code == code
        ).first()
        
        if not account:
            account_type = "Asset" if code.startswith("1") else "Liability" if code.startswith("2") else "Expense"
            account = ChartOfAccounts(
                company_id=company_id,
                account_code=code,
                account_name=name,
                account_type=account_type,
                normal_balance="Debit" if account_type in ["Asset", "Expense"] else "Credit"
            )
            self.db.add(account)
            self.db.flush()
        
        return account