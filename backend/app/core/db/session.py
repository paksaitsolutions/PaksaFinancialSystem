"""
Database session management with production-ready configuration.
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create declarative base for models
Base = declarative_base()

# Use environment-based configuration with fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./paksa_finance.db")

# Handle SQLite path creation if using SQLite
if "sqlite" in DATABASE_URL:
    db_path = DATABASE_URL.split("///")[-1] if "///" in DATABASE_URL else "paksa_finance.db"
    DB_DIR = Path(db_path).parent
    DB_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n=== Database Configuration ===")
print(f"Database URL: {DATABASE_URL}")
print(f"Environment: {getattr(settings, 'ENVIRONMENT', 'development')}")
print("==============================\n")

# Create async engine with proper configuration
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    DATABASE_URL,
    echo=getattr(settings, 'DEBUG', False),
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300 if "postgresql" in DATABASE_URL else -1
)

# Create async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# SessionLocal for FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    
    This can be used in non-FastAPI contexts where you need a database session.
    
    Example:
        async with get_db_context() as db:
            db.add(some_object)
            await db.commit()
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize database with tables
async def init_db():
    """Initialize database with all tables."""
    try:
        # Import specific models to ensure they're registered
        from app.models.base import BaseModel
        from app.models.user import User
        from app.models.gl_account import GLAccount
        from app.models.journal_entry import JournalEntry, JournalEntryLine
        from app.models.vendor import MainVendor as Vendor, APInvoice, APPayment
        from app.models.customer import Customer, ARInvoice, ARPayment
        from app.models.budget import Budget, BudgetLineItem
        from app.models.cash_account import CashAccount, CashTransaction
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database initialized successfully")
        
        # Seed with sample data
        await seed_database()
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't raise in development to allow server to start
        pass

async def seed_database():
    """Seed database with initial data."""
    try:
        async with get_db_context() as db:
            from app.models.user import User
            from app.models.gl_account import GLAccount
            from app.models.vendor import MainVendor as Vendor
            from app.models.customer import Customer
            from app.models.cash_account import CashAccount
            from app.core.security import get_password_hash
            from sqlalchemy import select
            
            # Check if data already exists
            result = await db.execute(select(User))
            if result.first():
                print("✅ Database already seeded")
                return
            
            tenant_id = "12345678-1234-5678-9012-123456789012"
            
            # Create admin user
            admin_user = User(
                email="admin@paksa.com",
                username="admin",
                first_name="System",
                last_name="Administrator",
                hashed_password=get_password_hash("admin123"),
                tenant_id=tenant_id,
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            db.add(admin_user)
            
            # Create sample GL accounts
            accounts = [
                GLAccount(tenant_id=tenant_id, account_code="1000", account_name="Cash", account_type="Asset", balance=50000),
                GLAccount(tenant_id=tenant_id, account_code="1200", account_name="Accounts Receivable", account_type="Asset", balance=25000),
                GLAccount(tenant_id=tenant_id, account_code="2000", account_name="Accounts Payable", account_type="Liability", balance=15000),
                GLAccount(tenant_id=tenant_id, account_code="4000", account_name="Revenue", account_type="Revenue", balance=100000),
                GLAccount(tenant_id=tenant_id, account_code="5000", account_name="Expenses", account_type="Expense", balance=40000)
            ]
            
            # Create sample vendors
            vendors = [
                Vendor(tenant_id=tenant_id, vendor_code="VEND001", vendor_name="Office Supplies Inc", current_balance=5000),
                Vendor(tenant_id=tenant_id, vendor_code="VEND002", vendor_name="Tech Solutions Ltd", current_balance=10000)
            ]
            
            # Create sample customers
            customers = [
                Customer(tenant_id=tenant_id, customer_code="CUST001", customer_name="ABC Corporation", current_balance=15000, credit_limit=50000),
                Customer(tenant_id=tenant_id, customer_code="CUST002", customer_name="XYZ Industries", current_balance=10000, credit_limit=75000)
            ]
            
            # Create sample cash account
            cash_account = CashAccount(
                tenant_id=tenant_id,
                account_name="Main Checking",
                account_number="****1234",
                bank_name="ABC Bank",
                current_balance=50000
            )
            
            for item in accounts + vendors + customers + [cash_account]:
                db.add(item)
            
            await db.commit()
            print("✅ Database seeded with sample data")
            
    except Exception as e:
        print(f"⚠️ Database seeding failed: {e}")

# Alias for get_db_context
get_db_session = get_db_context

# For backward compatibility
SessionLocal = async_session_factory
SessionType = AsyncSession