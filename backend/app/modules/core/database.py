"""
Database configuration and base models.
"""
import contextlib
from typing import Any, AsyncGenerator, Optional

from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker

from .config import settings

# Create async database engine
engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
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
    ""
    Dependency function that yields database sessions.
    
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
    async with engine.begin() as conn:
        # Create all tables
        from ..modules import models  # Import all models to register them with SQLAlchemy
        await conn.run_sync(Base.metadata.create_all)


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
