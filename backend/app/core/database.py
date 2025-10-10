"""
Database configuration and session management.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.core.config.settings import settings

# Create sync engine (avoiding async issues)
sync_db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

if sync_db_url.startswith("sqlite"):
    engine = create_engine(
        sync_db_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        sync_db_url,
        echo=settings.DEBUG
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create base class for models
Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Import all models to ensure they are registered
    from app.models import user  # noqa
    from app.models import tax_return  # noqa
    from app.models import settings  # noqa
    
    # Import models with unique names to avoid conflicts
    try:
        from app.models.tax_models import TaxRate, TaxTransaction, TaxExemption, TaxJurisdiction  # noqa
        from app.models.tax_payment import TaxPayment  # noqa - Use TaxPayment instead of Payment
        print("[OK] Tax models imported")
    except ImportError as e:
        print(f"Warning: Could not import tax models: {e}")
    
    try:
        from app.models.payroll_models import Employee, PayRun, PayRunEmployee, Payslip, PayrollItem, EmployeePayrollItem  # noqa
        print("[OK] Payroll models imported")
    except ImportError as e:
        print(f"Warning: Could not import payroll models: {e}")
    
    try:
        from app.models.gl_models import (  # Import GL models
            GLChartOfAccounts, JournalEntry, JournalEntryLine, 
            AccountingPeriod, LedgerBalance, TrialBalance, 
            TrialBalanceAccount, FinancialStatement, BudgetEntry
        )
        from app.core.audit import AuditLog
        print("[OK] GL models imported")
    except ImportError as e:
        print(f"Warning: Could not import GL models: {e}")
    
    try:
        from app.models.accounts_payable.payment import APPayment  # noqa - Use APPayment instead of Payment
        from app.models.accounts_payable.vendor import Vendor  # noqa
        from app.models.accounts_payable.invoice import APInvoice  # noqa
        print("[OK] AP models imported")
    except ImportError as e:
        print(f"Warning: Could not import AP models: {e}")
    
    try:
        from app.models.accounting import Customer, Invoice as ARInvoice  # noqa
        print("[OK] AR models imported")
    except ImportError as e:
        print(f"Warning: Could not import AR models: {e}")
    
    try:
        from app.models.cash_management import BankAccount, BankTransaction, CashFlowCategory  # noqa
        print("[OK] Cash models imported")
    except ImportError as e:
        print(f"Warning: Could not import cash models: {e}")
    
    try:
        from app.models.inventory import InventoryItem, InventoryLocation, InventoryCategory, FixedAsset  # noqa
        print("[OK] Inventory models imported")
    except ImportError as e:
        print(f"Warning: Could not import inventory models: {e}")
    
    try:
        from app.models.inventory import FixedAsset, AssetDepreciation, AssetMaintenance  # noqa
        print("[OK] Fixed Assets models imported")
    except ImportError as e:
        print(f"Warning: Could not import fixed assets models: {e}")
    
    try:
        from app.models.bi_ai.dashboard import Dashboard, KPI, Anomaly, Prediction  # noqa
        print("[OK] BI/AI models imported")
    except ImportError as e:
        print(f"Warning: Could not import BI/AI models: {e}")
    
    print("[OK] All available models imported")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created/verified")
    
    # Create first superuser if it doesn't exist
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Check if superuser exists
        superuser_email = getattr(settings, 'FIRST_SUPERUSER_EMAIL', 'admin@paksa.com')
        superuser_password = getattr(settings, 'FIRST_SUPERUSER_PASSWORD', 'admin123')
        
        existing_user = db.query(User).filter(User.email == superuser_email).first()
        if not existing_user:
            # Create superuser
            hashed_password = get_password_hash(superuser_password)
            superuser = User(
                email=superuser_email,
                hashed_password=hashed_password,
                first_name="System",
                last_name="Administrator",
                is_active=True,
                is_superuser=True
            )
            db.add(superuser)
            db.commit()
            print(f"[OK] Created superuser: {superuser_email}")
        else:
            print(f"[OK] Superuser already exists: {superuser_email}")
    finally:
        db.close()