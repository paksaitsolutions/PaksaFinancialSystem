"""
Simple script to initialize the database and create an admin user.
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.database import Base, get_db_url
from core.security import get_password_hash
from models.user import User, Role

async def init_db():
    """Initialize the database and create an admin user."""
    print("Initializing database...")
    
    # Create database engine
    db_url = get_db_url()
    engine = create_async_engine(db_url, echo=True)
    
    # Create all tables
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a session
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as db:
        # Create admin role if it doesn't exist
        admin_role = await Role.get_by_name(db, "System Administrator")
        if not admin_role:
            admin_role = Role(
                name="System Administrator",
                description="Full system access with all permissions",
                is_system=True
            )
            db.add(admin_role)
            await db.commit()
            print("Created System Administrator role")
        
        # Create admin user
        admin_email = settings.FIRST_SUPERUSER_EMAIL
        admin_password = settings.FIRST_SUPERUSER_PASSWORD
        
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
            print(f"Created admin user: {admin_email}")
        else:
            print(f"Admin user {admin_email} already exists")
    
    print("Database initialization complete!")
    print(f"Admin email: {admin_email}")
    print(f"Admin password: {admin_password}")

if __name__ == "__main__":
    asyncio.run(init_db())
