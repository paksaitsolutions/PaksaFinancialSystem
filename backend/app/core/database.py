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

# Import Base from core_models to ensure consistency
try:
    from app.models.base import Base
except ImportError:
    # Fallback to creating Base if import fails
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
    # Import unified core models
    try:
        from app.models.core_models import (
            ChartOfAccounts, JournalEntry, JournalEntryLine,
            Vendor, Customer, Employee, Department,
            APInvoice, APPayment, ARInvoice, ARPayment,
            PayrollRun, PayrollEntry, LeaveRequest,
            InventoryItem, InventoryCategory, PurchaseOrder,
            TaxRate, FinancialPeriod, Budget, FixedAsset,
            Company, Currency, ExchangeRate
        )
        print("[OK] Core models imported")
    except ImportError as e:
        print(f"Error: Could not import core models: {e}")
        return
    
    # Import additional models
    try:
        from app.models import user  # noqa
        print("[OK] User models imported")
    except ImportError as e:
        print(f"Warning: Could not import user models: {e}")
    
    try:
        from app.models.ai_bi_models import AIInsight, AIRecommendation, AIAnomaly, AIPrediction, AIModelMetrics  # noqa
        print("[OK] AI/BI models imported")
    except ImportError as e:
        print(f"Warning: Could not import AI/BI models: {e}")
    
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