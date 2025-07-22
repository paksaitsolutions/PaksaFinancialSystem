"""
Database initialization and setup.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import engine, Base
from app.modules.core_financials.general_ledger.models import Account, JournalEntry, JournalEntryLine, FiscalPeriod
from app.modules.core_financials.payroll.models import Employee, PayrollRecord, PayrollDeduction
from app.modules.core_financials.accounts_payable.models import Vendor, APInvoice, APPayment
from app.modules.core_financials.accounts_receivable.models import Customer, ARInvoice, ARInvoiceLineItem, ARPayment
from app.modules.core_financials.cash_management.models import BankAccount, BankTransaction, BankReconciliation, CashFlowForecast
from app.modules.core_financials.fixed_assets.models import Asset, DepreciationSchedule, MaintenanceRecord, AssetDisposal

async def init_db() -> None:
    """Initialize database tables."""
    from sqlalchemy import inspect
    from sqlalchemy.exc import SQLAlchemyError
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Test the database connection
        logger.info("Testing database connection...")
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection successful")
        
        # Create all tables
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            # Check if tables already exist
            inspector = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn.engine)
            )
            existing_tables = await conn.run_sync(
                lambda sync_conn: inspector.get_table_names()
            )
            
            if existing_tables:
                logger.info(f"Found {len(existing_tables)} existing tables")
            else:
                logger.info("No existing tables found, creating schema...")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
    except SQLAlchemyError as e:
        logger.error(f"Database error during initialization: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        raise

async def create_sample_data() -> None:
    """Create sample data for testing."""
    from app.db.base import AsyncSessionLocal
    from app.modules.core_financials.general_ledger.models import AccountType
    from datetime import date
    
    async with AsyncSessionLocal() as db:
        # Create sample chart of accounts
        accounts = [
            Account(account_code="1000", account_name="Cash", account_type=AccountType.ASSET),
            Account(account_code="1200", account_name="Accounts Receivable", account_type=AccountType.ASSET),
            Account(account_code="2000", account_name="Accounts Payable", account_type=AccountType.LIABILITY),
            Account(account_code="3000", account_name="Owner's Equity", account_type=AccountType.EQUITY),
            Account(account_code="4000", account_name="Revenue", account_type=AccountType.REVENUE),
            Account(account_code="5000", account_name="Expenses", account_type=AccountType.EXPENSE),
        ]
        
        for account in accounts:
            db.add(account)
        
        # Create sample employee
        employee = Employee(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            email="john.doe@company.com",
            department="Finance",
            position="Accountant",
            hire_date=date(2024, 1, 1),
            salary=60000.00
        )
        db.add(employee)
        
        await db.commit()