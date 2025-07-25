"""
Database session management.
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

class BaseModel(Base):
    """Base model class with common functionality."""
    __abstract__ = True

# Use environment-based configuration
DB_URI = os.getenv("DATABASE_URL", settings.SQLALCHEMY_DATABASE_URI)

# Handle SQLite path creation if using SQLite
if "sqlite" in DB_URI:
    db_path = DB_URI.split("///")[-1] if "///" in DB_URI else "paksa_finance.db"
    DB_DIR = Path(db_path).parent
    DB_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n=== Database Configuration ===")
print(f"Database URI: {DB_URI}")
print(f"Environment: {settings.ENVIRONMENT}")
print("==========================\n")

# Create async engine with proper configuration
connect_args = {}
if "sqlite" in DB_URI:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    DB_URI,
    echo=settings.DEBUG,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300 if "postgresql" in DB_URI else -1
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

# Additional utility functions
async def init_db():
    """Initialize database."""
    pass

async def seed_database():
    """Seed database with initial data."""
    pass

async def seed_users():
    """Seed users."""
    pass

def get_database_url():
    """Get database URL."""
    return DB_URI

def validate_database_url(url):
    """Validate database URL."""
    return url

# Alias for get_db_context
get_db_session = get_db_context

# For backward compatibility
SessionLocal = async_session_factory
SessionType = AsyncSession