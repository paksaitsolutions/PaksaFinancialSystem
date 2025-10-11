"""
Data migration script for model consolidation
"""
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import *

def migrate_existing_data():
    """Migrate existing data to use unified models"""
    db = next(get_db())
    
    # Update AP invoices to generate missing GL entries
    ap_invoices = db.query(APInvoice).outerjoin(
        JournalEntry, 
        and_(JournalEntry.source_id == APInvoice.id, JournalEntry.source_module == 'AP')
    ).filter(JournalEntry.id.is_(None)).all()
    
    for invoice in ap_invoices:
        # Create GL entry for AP invoice
        journal_entry = JournalEntry(
            company_id=invoice.company_id,
            entry_date=invoice.invoice_date,
            description=f"AP Invoice {invoice.invoice_number}",
            reference_number=invoice.invoice_number,
            source_module='AP',
            source_id=invoice.id,
            status='posted'
        )
        db.add(journal_entry)
        db.flush()
        
        # Add journal entry lines
        for line_item in invoice.line_items:
            # Debit expense account
            db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=line_item.account_id,
                description=line_item.description,
                debit_amount=line_item.amount,
                credit_amount=0
            ))
        
        # Credit accounts payable
        ap_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == '2000',
            ChartOfAccounts.company_id == invoice.company_id
        ).first()
        
        if ap_account:
            db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=ap_account.id,
                description=f"AP Invoice {invoice.invoice_number}",
                debit_amount=0,
                credit_amount=invoice.total_amount
            ))
    
    db.commit()
    print(f"Migrated {len(ap_invoices)} AP invoices")

if __name__ == "__main__":
    migrate_existing_data()