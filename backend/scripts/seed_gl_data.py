import sys
import os
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models and schemas
from app.models.gl_models_updated import GLAccount, JournalEntry, JournalEntryLine, AccountingPeriod
from app.schemas.gl_schemas_new import AccountType, JournalEntryStatus

# Database setup
DATABASE_URL = "sqlite:///../../gl_database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def create_sample_accounts():
    """Create sample chart of accounts"""
    print("Creating sample chart of accounts...")
    
    # Top-level accounts
    accounts = [
        # Assets
        {"code": "1000", "name": "Current Assets", "type": AccountType.ASSET, "parent": None},
        {"code": "1100", "name": "Cash and Cash Equivalents", "type": AccountType.ASSET, "parent": "1000"},
        {"code": "1110", "name": "Petty Cash", "type": AccountType.ASSET, "parent": "1100"},
        {"code": "1120", "name": "Bank Accounts", "type": AccountType.ASSET, "parent": "1100"},
        {"code": "1200", "name": "Accounts Receivable", "type": AccountType.ASSET, "parent": "1000"},
        {"code": "1300", "name": "Inventory", "type": AccountType.ASSET, "parent": "1000"},
        {"code": "1400", "name": "Prepaid Expenses", "type": AccountType.ASSET, "parent": "1000"},
        
        # Liabilities
        {"code": "2000", "name": "Current Liabilities", "type": AccountType.LIABILITY, "parent": None},
        {"code": "2100", "name": "Accounts Payable", "type": AccountType.LIABILITY, "parent": "2000"},
        {"code": "2200", "name": "Accrued Expenses", "type": AccountType.LIABILITY, "parent": "2000"},
        {"code": "2300", "name": "Short-term Loans", "type": AccountType.LIABILITY, "parent": "2000"},
        
        # Equity
        {"code": "3000", "name": "Owner's Equity", "type": AccountType.EQUITY, "parent": None},
        {"code": "3100", "name": "Common Stock", "type": AccountType.EQUITY, "parent": "3000"},
        {"code": "3200", "name": "Retained Earnings", "type": AccountType.EQUITY, "parent": "3000"},
        
        # Revenue
        {"code": "4000", "name": "Operating Revenue", "type": AccountType.REVENUE, "parent": None},
        {"code": "4100", "name": "Product Sales", "type": AccountType.REVENUE, "parent": "4000"},
        {"code": "4200", "name": "Service Revenue", "type": AccountType.REVENUE, "parent": "4000"},
        {"code": "4300", "name": "Other Income", "type": AccountType.REVENUE, "parent": "4000"},
        
        # Expenses
        {"code": "5000", "name": "Operating Expenses", "type": AccountType.EXPENSE, "parent": None},
        {"code": "5100", "name": "Cost of Goods Sold", "type": AccountType.EXPENSE, "parent": "5000"},
        {"code": "5200", "name": "Salaries and Wages", "type": AccountType.EXPENSE, "parent": "5000"},
        {"code": "5300", "name": "Rent Expense", "type": AccountType.EXPENSE, "parent": "5000"},
        {"code": "5400", "name": "Utilities", "type": AccountType.EXPENSE, "parent": "5000"},
        {"code": "5500", "name": "Office Supplies", "type": AccountType.EXPENSE, "parent": "5000"},
        {"code": "5600", "name": "Marketing", "type": AccountType.EXPENSE, "parent": "5000"},
        {"code": "5700", "name": "Depreciation", "type": AccountType.EXPENSE, "parent": "5000"},
        {"code": "5800", "name": "Interest Expense", "type": AccountType.EXPENSE, "parent": "5000"},
    ]
    
    # Create account mapping for parent references
    account_map = {}
    
    for acc in accounts:
        parent_id = None
        if acc["parent"]:
            parent_account = db.query(GLAccount).filter_by(account_code=acc["parent"]).first()
            if parent_account:
                parent_id = parent_account.id
        
        account = GLAccount(
            account_code=acc["code"],
            account_name=acc["name"],
            account_type=acc["type"],
            parent_id=parent_id,
            is_active=True
        )
        db.add(account)
        db.flush()  # Flush to get the ID
        account_map[acc["code"]] = account.id
    
    db.commit()
    print(f"Created {len(accounts)} accounts")
    return account_map

def create_accounting_periods():
    """Create sample accounting periods for the current year"""
    print("Creating accounting periods...")
    
    current_year = date.today().year
    periods = []
    
    # Create monthly periods for the current year
    for month in range(1, 13):
        start_date = date(current_year, month, 1)
        if month == 12:
            end_date = date(current_year, 12, 31)
        else:
            end_date = date(current_year, month + 1, 1) - timedelta(days=1)
        
        period_name = start_date.strftime("%b-%Y").upper()
        is_closed = start_date.month < date.today().month
        
        period = AccountingPeriod(
            period_name=period_name,
            start_date=start_date,
            end_date=end_date,
            is_closed=is_closed
        )
        db.add(period)
        periods.append(period)
    
    db.commit()
    print(f"Created {len(periods)} accounting periods for {current_year}")
    return periods

def create_sample_journal_entries(account_map):
    """Create sample journal entries"""
    print("Creating sample journal entries...")
    
    # Get the current month's period
    current_month = date.today().replace(day=1)
    period = db.query(AccountingPeriod).filter(
        AccountingPeriod.start_date == current_month
    ).first()
    
    if not period:
        print("No accounting period found for the current month")
        return
    
    # Sample journal entries
    entries = [
        {
            "entry_number": "JE-2023-001",
            "entry_date": date.today() - timedelta(days=5),
            "reference": "INV-1001",
            "description": "Recording sales for the day",
            "lines": [
                {"account_code": "1120", "debit": 0, "credit": 1500.00, "description": "Bank deposit"},
                {"account_code": "4100", "debit": 1500.00, "credit": 0, "description": "Product sales"}
            ]
        },
        {
            "entry_number": "JE-2023-002",
            "entry_date": date.today() - timedelta(days=3),
            "reference": "BILL-5001",
            "description": "Office rent for the month",
            "lines": [
                {"account_code": "5300", "debit": 2000.00, "credit": 0, "description": "Monthly rent"},
                {"account_code": "1120", "debit": 0, "credit": 2000.00, "description": "Rent payment"}
            ]
        },
        {
            "entry_number": "JE-2023-003",
            "entry_date": date.today() - timedelta(days=1),
            "reference": "PAY-1001",
            "description": "Monthly payroll",
            "lines": [
                {"account_code": "5200", "debit": 5000.00, "credit": 0, "description": "Salaries expense"},
                {"account_code": "2100", "debit": 0, "credit": 5000.00, "description": "Salaries payable"}
            ]
        }
    ]
    
    for entry_data in entries:
        # Create the journal entry
        entry = JournalEntry(
            entry_number=entry_data["entry_number"],
            entry_date=entry_data["entry_date"],
            reference=entry_data["reference"],
            description=entry_data["description"],
            status=JournalEntryStatus.POSTED
        )
        db.add(entry)
        db.flush()
        
        # Add journal entry lines
        for line_num, line_data in enumerate(entry_data["lines"], 1):
            account_id = account_map.get(line_data["account_code"])
            if not account_id:
                print(f"Account not found: {line_data['account_code']}")
                continue
                
            line = JournalEntryLine(
                journal_entry_id=entry.id,
                account_id=account_id,
                line_number=line_num,
                debit_amount=line_data["debit"],
                credit_amount=line_data["credit"],
                description=line_data["description"]
            )
            db.add(line)
    
    db.commit()
    print(f"Created {len(entries)} sample journal entries")

def main():
    try:
        # Create sample data
        account_map = create_sample_accounts()
        create_accounting_periods()
        create_sample_journal_entries(account_map)
        
        print("\n✅ Sample data creation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding General Ledger data...\n")
    main()
