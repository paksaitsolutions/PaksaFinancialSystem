"""
Database session management.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session as SessionType

from app.core.config import settings

# Create database engine
engine = create_async_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,
    pool_size=settings.SQLALCHEMY_POOL_SIZE,
    max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
    pool_timeout=settings.SQLALCHEMY_POOL_TIMEOUT,
    pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE,
    echo=settings.SQLALCHEMY_ECHO,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=True,
)

async def get_db() -> AsyncSession:
    """
    Async dependency function that yields database sessions.
    
    This should be used as a FastAPI dependency to get a database session.
    The session is automatically closed when the request is done.
    
    Example:
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@contextmanager
def get_db_context() -> Generator[SessionType, None, None]:
    """
    Context manager for database sessions.
    
    This can be used in non-FastAPI contexts where you need a database session.
    
    Example:
        with get_db_context() as db:
            db.add(some_object)
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session() -> SessionType:
    """
    Get a database session.
    
    This is a simple function that returns a database session.
    It's the caller's responsibility to close the session.
    
    Returns:
        Session: A SQLAlchemy database session.
    """
    return SessionLocal()
