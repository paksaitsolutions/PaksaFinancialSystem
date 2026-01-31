"""
Unified Database Initialization Script
Consolidates all database initialization logic into a single source of truth.

This script:
1. Creates all database tables
2. Seeds initial data (admin user, reference data)
3. Optionally loads sample data for development
4. Handles migrations

Usage:
    python -m app.core.db.unified_init --mode production
    python -m app.core.db.unified_init --mode development --sample-data
    python -m app.core.db.unified_init --reset  # WARNING: Drops all tables
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import argparse

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine, get_db, init_db
from app.core.config import settings
from app.models import *  # Import all models to ensure they're registered


async def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    try:
        await init_db()
        print("✓ Tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


async def create_admin_user(db: AsyncSession):
    """Create initial admin user."""
    from app.crud.auth.user_crud import user_crud
    from app.schemas.user import UserCreate
    from app.core.security import get_password_hash
    
    print("Creating admin user...")
    try:
        # Check if admin exists
        admin_email = settings.FIRST_SUPERUSER_EMAIL or "admin@paksa.com"
        existing = await user_crud.get_by_email(db, email=admin_email)
        
        if existing:
            print(f"✓ Admin user already exists: {admin_email}")
            return True
        
        # Create admin user
        admin_data = UserCreate(
            email=admin_email,
            password=settings.FIRST_SUPERUSER_PASSWORD or "admin123",
            full_name="System Administrator",
            is_superuser=True,
            is_active=True
        )
        
        await user_crud.create(db, obj_in=admin_data)
        await db.commit()
        print(f"✓ Admin user created: {admin_email}")
        return True
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        await db.rollback()
        return False


async def seed_reference_data(db: AsyncSession):
    """Seed reference data (regions, currencies, etc.)."""
    print("Seeding reference data...")
    try:
        # Import reference data seeding functions
        from app.scripts.seed_region_currency_data import seed_regions_and_currencies
        
        await seed_regions_and_currencies(db)
        await db.commit()
        print("✓ Reference data seeded successfully")
        return True
    except Exception as e:
        print(f"✗ Error seeding reference data: {e}")
        await db.rollback()
        return False


async def seed_chart_of_accounts(db: AsyncSession):
    """Seed default chart of accounts."""
    print("Seeding chart of accounts...")
    try:
        from app.modules.core_financials.general_ledger.seed_accounts import seed_default_accounts
        
        await seed_default_accounts(db)
        await db.commit()
        print("✓ Chart of accounts seeded successfully")
        return True
    except Exception as e:
        print(f"✗ Error seeding chart of accounts: {e}")
        await db.rollback()
        return False


async def load_sample_data(db: AsyncSession):
    """Load sample data for development/testing."""
    print("Loading sample data...")
    try:
        # GL Sample Data
        from app.scripts.seed_gl_data import seed_gl_sample_data
        await seed_gl_sample_data(db)
        
        # AP Sample Data
        from app.scripts.init_ap_data import seed_ap_sample_data
        await seed_ap_sample_data(db)
        
        # AR Sample Data
        from app.scripts.init_ar_data import seed_ar_sample_data
        await seed_ar_sample_data(db)
        
        # Cash Sample Data
        from app.scripts.init_cash_data import seed_cash_sample_data
        await seed_cash_sample_data(db)
        
        # Budget Sample Data
        from app.scripts.init_budget_data import seed_budget_sample_data
        await seed_budget_sample_data(db)
        
        # Payroll Sample Data
        from app.scripts.init_payroll_data import seed_payroll_sample_data
        await seed_payroll_sample_data(db)
        
        # Tax Sample Data
        from app.scripts.init_tax_data import seed_tax_sample_data
        await seed_tax_sample_data(db)
        
        await db.commit()
        print("✓ Sample data loaded successfully")
        return True
    except Exception as e:
        print(f"⚠ Warning: Some sample data failed to load: {e}")
        await db.rollback()
        return False


async def reset_database():
    """Drop all tables (WARNING: Destructive operation)."""
    print("⚠ WARNING: This will delete all data!")
    confirm = input("Type 'DELETE ALL DATA' to confirm: ")
    
    if confirm != "DELETE ALL DATA":
        print("✗ Reset cancelled")
        return False
    
    print("Dropping all tables...")
    try:
        from app.models.base import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("✓ All tables dropped")
        return True
    except Exception as e:
        print(f"✗ Error dropping tables: {e}")
        return False


async def verify_database():
    """Verify database setup."""
    print("\nVerifying database setup...")
    try:
        async with engine.begin() as conn:
            # Check if tables exist
            result = await conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            ))
            table_count = result.scalar()
            print(f"✓ Found {table_count} tables")
            
            # Check admin user
            result = await conn.execute(text(
                "SELECT COUNT(*) FROM users WHERE is_superuser = true"
            ))
            admin_count = result.scalar()
            print(f"✓ Found {admin_count} admin user(s)")
            
        return True
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False


async def main(mode: str = "production", sample_data: bool = False, reset: bool = False):
    """Main initialization function."""
    print("=" * 60)
    print("Paksa Financial System - Database Initialization")
    print("=" * 60)
    print(f"Mode: {mode}")
    print(f"Sample Data: {sample_data}")
    print(f"Reset: {reset}")
    print("=" * 60)
    
    success = True
    
    # Reset if requested
    if reset:
        if not await reset_database():
            return False
    
    # Create tables
    if not await create_tables():
        return False
    
    # Get database session
    async for db in get_db():
        # Create admin user
        if not await create_admin_user(db):
            success = False
        
        # Seed reference data
        if not await seed_reference_data(db):
            success = False
        
        # Seed chart of accounts
        if not await seed_chart_of_accounts(db):
            success = False
        
        # Load sample data if requested
        if sample_data:
            if not await load_sample_data(db):
                print("⚠ Warning: Sample data loading had issues")
        
        break  # Only need one iteration
    
    # Verify setup
    await verify_database()
    
    print("=" * 60)
    if success:
        print("✓ Database initialization completed successfully!")
        print(f"\nAdmin credentials:")
        print(f"  Email: {settings.FIRST_SUPERUSER_EMAIL or 'admin@paksa.com'}")
        print(f"  Password: {settings.FIRST_SUPERUSER_PASSWORD or 'admin123'}")
        print("\n⚠ IMPORTANT: Change the admin password after first login!")
    else:
        print("⚠ Database initialization completed with warnings")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize Paksa Financial System Database")
    parser.add_argument(
        "--mode",
        choices=["production", "development", "testing"],
        default="production",
        help="Initialization mode"
    )
    parser.add_argument(
        "--sample-data",
        action="store_true",
        help="Load sample data for development"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (WARNING: Deletes all data)"
    )
    
    args = parser.parse_args()
    
    # Run initialization
    success = asyncio.run(main(
        mode=args.mode,
        sample_data=args.sample_data,
        reset=args.reset
    ))
    
    sys.exit(0 if success else 1)
