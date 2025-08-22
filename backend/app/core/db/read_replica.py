"""
Read replica database configuration.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Read replica engine
read_replica_engine = None
read_replica_session_factory = None

if settings.USE_READ_REPLICA and settings.DATABASE_READ_REPLICA_URL:
    read_replica_engine = create_async_engine(
        settings.DATABASE_READ_REPLICA_URL,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    
    read_replica_session_factory = async_sessionmaker(
        read_replica_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )

async def get_read_db() -> AsyncGenerator[AsyncSession, None]:
    """Get read-only database session."""
    if read_replica_session_factory:
        async with read_replica_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    else:
        # Fallback to main database
        from app.core.db.session import get_db
        async for session in get_db():
            yield session