""
Initialize the database with required tables and initial data.
"""
import asyncio
import logging
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import text

from core.config import settings
from core.database import Base, engine, init_db
from models.base import BaseModel
from models.user import User, Role, Permission, RolePermission
from models.permission import SYSTEM_PERMISSIONS, PERMISSION_CATEGORIES
from models.general_ledger import ChartOfAccounts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    ""Create database tables."""
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully.")

async def create_initial_roles(db):
    ""Create initial roles and permissions."""
    logger.info("Creating initial roles and permissions...")
    
    # Create system administrator role
    admin_role = await Role.get_by_name(db, "System Administrator")
    if not admin_role:
        admin_role = Role(
            name="System Administrator",
            description="Full system access with all permissions",
            is_system=True
        )
        db.add(admin_role)
        await db.commit()
        await db.refresh(admin_role)
        logger.info("Created System Administrator role")
    
    # Create default user role
    user_role = await Role.get_by_name(db, "User")
    if not user_role:
        user_role = Role(
            name="User",
            description="Standard user with basic permissions",
            is_default=True
        )
        db.add(user_role)
        await db.commit()
        await db.refresh(user_role)
        logger.info("Created default User role")
    
    return admin_role, user_role

async def create_system_permissions(db):
    ""Create system permissions."""
    logger.info("Creating system permissions...")
    
    # Create all system permissions
    for permission_name, description, category, is_system in SYSTEM_PERMISSIONS:
        permission = await Permission.get_by_name(db, permission_name)
        if not permission:
            permission = Permission(
                name=permission_name,
                description=description,
                category=category,
                is_system=is_system
            )
            db.add(permission)
    
    await db.commit()
    logger.info("Created system permissions")

async def create_initial_admin_user(db, admin_role):
    ""Create the initial admin user."""
    from core.security import get_password_hash
    
    logger.info("Creating initial admin user...")
    
    # Check if admin user already exists
    admin_email = settings.FIRST_SUPERUSER
    admin_password = settings.FIRST_SUPERUSER_PASSWORD
    
    if not admin_email or not admin_password:
        logger.warning("Admin email or password not set in environment variables")
        return
    
    admin_user = await User.get_by_email(db, admin_email)
    if not admin_user:
        admin_user = User(
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            first_name="Admin",
            last_name="User",
            is_superuser=True,
            is_verified=True,
            is_active=True,
            role_id=admin_role.id
        )
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        logger.info(f"Created admin user: {admin_email}")
    else:
        logger.info(f"Admin user {admin_email} already exists")
    
    return admin_user

async def create_initial_chart_of_accounts(db):
    ""Create initial chart of accounts."""
    logger.info("Creating initial chart of accounts...")
    
    # Define the root accounts
    root_accounts = [
        {
            "code": "1",
            "name": "Assets",
            "category": "Asset",
            "account_type": "Current Asset",
            "normal_balance": "D"
        },
        {
            "code": "2",
            "name": "Liabilities",
            "category": "Liability",
            "account_type": "Current Liability",
            "normal_balance": "C"
        },
        {
            "code": "3",
            "name": "Equity",
            "category": "Equity",
            "account_type": "Equity",
            "normal_balance": "C"
        },
        {
            "code": "4",
            "name": "Revenue",
            "category": "Revenue",
            "account_type": "Operating Revenue",
            "normal_balance": "C"
        },
        {
            "code": "5",
            "name": "Expenses",
            "category": "Expense",
            "account_type": "Operating Expense",
            "normal_balance": "D"
        }
    ]
    
    # Create root accounts
    for account_data in root_accounts:
        account = await ChartOfAccounts.get_by_code(db, account_data["code"])
        if not account:
            account = ChartOfAccounts(**account_data)
            db.add(account)
    
    await db.commit()
    logger.info("Created initial chart of accounts")

async def main():
    ""Initialize the database."""
    logger.info("Starting database initialization...")
    
    # Initialize database connection
    db = await init_db()
    
    try:
        # Create tables
        await create_tables()
        
        # Create initial roles and permissions
        admin_role, _ = await create_initial_roles(db)
        await create_system_permissions(db)
        
        # Create initial admin user
        await create_initial_admin_user(db, admin_role)
        
        # Create initial chart of accounts
        await create_initial_chart_of_accounts(db)
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        await db.close()
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
