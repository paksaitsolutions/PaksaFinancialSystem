"""
Database initialization and seeding utilities.
"""
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db.session import async_session_factory

logger = logging.getLogger(__name__)

async def init_db() -> None:
    """Initialize the database with required tables and initial data."""
    logger.info("Initializing database...")
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models.base import Base
    
    # Create database tables
    async with async_session_factory() as session:
        try:
            # Create all tables
            async with session.bind.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database tables created successfully")
            
            # Seed initial data
            await seed_database(session)
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

async def seed_database(session: AsyncSession) -> None:
    """Seed the database with initial data."""
    logger.info("Seeding database...")
    
    # Seed users
    await seed_users(session)
    
    # Add other seed functions as needed
    
    await session.commit()
    logger.info("Database seeding completed successfully")

async def seed_users(session: AsyncSession) -> None:
    """Seed the database with initial users."""
    # Import here to avoid circular imports
    from app.crud.crud_user import user as user_crud
    from app.schemas.user import UserCreate
    from app.core.security import get_password_hash
    
    # Create admin user if it doesn't exist
    admin_email = settings.FIRST_SUPERUSER
    admin_password = settings.FIRST_SUPERUSER_PASSWORD
    
    if not admin_email or not admin_password:
        logger.warning("No admin credentials provided. Skipping admin user creation.")
        return
    
    # Check if user already exists
    existing_admin = await user_crud.get_by_email(session, email=admin_email)
    if existing_admin:
        logger.info(f"Admin user {admin_email} already exists. Skipping creation.")
        return
    
    try:
        # Create admin user
        admin_user = UserCreate(
            email=admin_email,
            password=admin_password,
            full_name="Admin User",
            is_superuser=True,
        )
        
        # Create the user in the database
        await user_crud.create(session, obj_in=admin_user)
        logger.info(f"Created admin user: {admin_email}")
        
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise
