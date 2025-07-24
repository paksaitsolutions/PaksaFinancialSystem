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

# Use a simple SQLite configuration for now
DB_DIR = Path("./instance")
DB_PATH = DB_DIR / "paksa_finance.db"
DB_URI = f"sqlite+aiosqlite:///{DB_PATH}"

# Ensure the database directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n=== Database Configuration ===")
print(f"Using SQLite database at: {DB_PATH}")
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

# For backward compatibility
SessionLocal = async_session_factory
SessionType = AsyncSession