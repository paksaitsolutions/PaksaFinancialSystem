"""
Database session management.
"""
import os
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator
from pathlib import Path
from typing import AsyncGenerator, Generator, TypeVar, Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

# Database configuration
DB_DIR = Path("D:/Paksa Financial System/backend/instance")
DB_PATH = DB_DIR / "paksa_finance.db"
DB_URI = f"sqlite+aiosqlite:///{DB_PATH}"

# Ensure the database directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n=== Database Configuration ===")
print(f"Using database at: {DB_PATH}")
print("==========================\n")

# Create async engine
engine = create_async_engine(
    DB_URI,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False}
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
        finally:
            await session.close()

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
    db = SessionLocal()
    try:
        yield db
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()

# For backward compatibility
SessionType = AsyncSession

def get_db_session() -> AsyncSession:
    """
    Get a database session.
    
    This is a simple function that returns a database session.
    It's the caller's responsibility to close the session.
    
    Returns:
        Session: A SQLAlchemy database session.
    """
    return SessionLocal()
