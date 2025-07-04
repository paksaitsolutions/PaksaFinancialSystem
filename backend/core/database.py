from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

from .config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URI,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=10,
    poolclass=NullPool if settings.TESTING else None,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base class for all models
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async DB session.
    
    Yields:
        AsyncSession: An async database session.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize database connections and create tables."""
    from sqlalchemy import text
    
    async with engine.begin() as conn:
        # Create extensions
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS "uuid-osup""))
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

async def close_db() -> None:
    """Close database connections."""
    if engine:
        await engine.dispose()

# Import all models to ensure they are registered with SQLAlchemy
# This must be done after Base is defined
from ..models import *  # noqa
