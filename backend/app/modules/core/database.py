"""
Database configuration and base models.
"""
import contextlib
from typing import Any, AsyncGenerator, Optional

from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

# Import settings from the correct location
from app.core.config import settings
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker

# Settings imported at the top

# Determine if we're using SQLite
IS_SQLITE = "sqlite" in settings.DATABASE_URI.lower()

# Create async database engine with appropriate parameters based on database type
engine = create_async_engine(
    settings.DATABASE_URI,
    echo=settings.SQLALCHEMY_ECHO,
    future=True,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
    pool_pre_ping=not IS_SQLITE,  # Enable for PostgreSQL, disable for SQLite
    # For SQLite, use a memory-based connection pool
    poolclass=NullPool if IS_SQLITE else None,
    pool_size=settings.SQLALCHEMY_POOL_SIZE if not IS_SQLITE else 5,
    max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW if not IS_SQLITE else 0,
    pool_timeout=settings.SQLALCHEMY_POOL_TIMEOUT if not IS_SQLITE else 30,
    pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE if not IS_SQLITE else 3600,
)

# Create async session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@as_declarative()
class Base:
    """Base class for all database models."""
    
    id: Any
    __name__: str
    
    # Generate table name from class name
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Common columns
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # For soft deletes


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function that yields database sessions.
    
    Usage:
        async with get_db() as db:
            # Use db session
            result = await db.execute(select(User))
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


async def init_db() -> None:
    """Initialize database tables."""
    import os
    from sqlalchemy import text
    
    # Create database directory for SQLite if it doesn't exist
    if IS_SQLITE and not os.path.exists("instance"):
        os.makedirs("instance")
    
    async with engine.begin() as conn:
        # Enable foreign keys for SQLite
        if IS_SQLITE:
            await conn.execute(text("PRAGMA foreign_keys=ON"))
        
        # Create all tables
        from .. import models  # Import all models to register them with SQLAlchemy
        await conn.run_sync(Base.metadata.create_all)
        
        # For SQLite, ensure WAL mode is enabled for better concurrency
        if IS_SQLITE:
            await conn.execute(text("PRAGMA journal_mode=WAL"))


@contextlib.asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database sessions."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# For backward compatibility
SessionLocal = async_session_factory
