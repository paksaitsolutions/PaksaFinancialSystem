"""
Database configuration and base models.
"""
from __future__ import annotations

import contextlib
import os
from typing import Any, AsyncGenerator, AsyncIterator, Optional, Type, TypeVar, cast

from sqlalchemy import Column, DateTime, MetaData, Text, event, text, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    AsyncConnection,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import declarative_mixin, sessionmaker
from sqlalchemy.sql import func

from ..core.config import settings

# Define a naming convention for database constraints
# This helps with migrations and database introspection
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=convention)

def create_database_engine() -> AsyncEngine:
    """Create and configure the async database engine.
    
    Returns:
        AsyncEngine: Configured SQLAlchemy async engine
    """
    # Use SQLALCHEMY_ECHO if available, otherwise default to False
    echo = getattr(settings, 'SQLALCHEMY_ECHO', getattr(settings, 'DB_ECHO', False))
    pool_size = getattr(settings, 'SQLALCHEMY_POOL_SIZE', getattr(settings, 'DB_POOL_SIZE', 20))
    max_overflow = getattr(settings, 'SQLALCHEMY_MAX_OVERFLOW', getattr(settings, 'DB_MAX_OVERFLOW', 10))
    pool_recycle = getattr(settings, 'SQLALCHEMY_POOL_RECYCLE', getattr(settings, 'DB_POOL_RECYCLE', 300))
    
    engine_options = {
        "echo": echo,
        "future": True,
        "pool_size": pool_size,
        "max_overflow": max_overflow,
        "pool_recycle": pool_recycle,
        "pool_pre_ping": True,  # Enable connection health checks
    }
    
    # Check if using SQLite by examining the database URL
    db_uri = str(getattr(settings, 'DATABASE_URL', ''))
    is_sqlite = 'sqlite' in db_uri.lower()
    
    if is_sqlite:
        # SQLite specific settings
        db_path = getattr(settings, 'SQLITE_DB_PATH', ':memory:')
        if db_path != ":memory:":
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        
        engine_options.update({
            "connect_args": {"check_same_thread": False},
            "poolclass": NullPool,  # Use NullPool for SQLite in async mode
        })
    else:
        # PostgreSQL/other database settings
        engine_options.update({
            "pool_use_lifo": True,  # Use LIFO for better connection reuse
        })
    
    # Convert DATABASE_URL to string if it's a Pydantic object
    database_uri = str(settings.DATABASE_URL)
    return create_async_engine(database_uri, **engine_options)

# Create async database engine
engine = create_database_engine()

# Create async session factory with modern SQLAlchemy 2.0+ approach
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# Create a base class for declarative models with metadata
Base = declarative_base(metadata=metadata)

# Type variable for model classes
ModelType = TypeVar("ModelType", bound="BaseModel")


@declarative_mixin
class BaseModel:
    """Base class for all database models with common functionality.
    
    This mixin provides common columns and methods for all models.
    """
    
    # This makes the class a mixin for declarative base
    __abstract__ = True
    
    # Common columns with proper typing
    id: Any
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="The timestamp when the record was created",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="The timestamp when the record was last updated",
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="The timestamp when the record was soft deleted (if applicable)",
    )
    
    # Define __tablename__ automatically based on class name
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()
    
    def __repr__(self) -> str:
        """Return a string representation of the model."""
        params = ", ".join(
            f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")
        )
        return f"{self.__class__.__name__}({params})"
    
    @classmethod
    async def get(cls: Type[ModelType], db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(select(cls).where(cls.id == id))  # type: ignore
        return result.scalars().first()
    
    @classmethod
    async def get_or_404(
        cls: Type[ModelType], db: AsyncSession, id: Any, detail: str = "Not Found"
    ) -> ModelType:
        """Get a single record by ID or raise 404 if not found."""
        result = await cls.get(db, id)
        if result is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=detail)
        return result
    
    async def save(self, db: AsyncSession) -> None:
        """Save the current instance to the database."""
        db.add(self)
        await db.commit()
        await db.refresh(self)
    
    async def delete(self, db: AsyncSession, hard: bool = False) -> None:
        """Delete the current instance from the database."""
        if hard or self.deleted_at is not None:
            await db.delete(self)
        else:
            # Soft delete
            self.deleted_at = func.now()
            db.add(self)
        await db.commit()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function that yields database sessions.
    
    This is the recommended way to get a database session in FastAPI route handlers.
    It handles session lifecycle including commits, rollbacks, and closing.
    
    Example:
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            # Re-raise the exception to be handled by FastAPI's exception handlers
            raise
        finally:
            await session.close()


@contextlib.asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Alternative dependency function that can be used as a context manager.
    
    This is useful for non-FastAPI contexts or when you need more control
    over the session lifecycle.
    
    Example:
        async with get_db_session() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
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


def get_db_sync() -> AsyncSession:
    """Get a synchronous database session (for use in synchronous contexts).
    
    Note: This should be used sparingly and only when absolutely necessary.
    Prefer the async version in most cases.
    """
    return async_session_factory()


async def init_db() -> None:
    """Initialize database tables and perform any required setup.
    
    This function:
    1. Creates all tables defined in SQLAlchemy models
    2. Sets up any required database extensions
    3. Performs any necessary data migrations
    4. Sets database-specific optimizations
    
    It should be called during application startup.
    """
    import os
    from sqlalchemy import text
    
    # Check if using SQLite by examining the database URL
    db_url = str(getattr(settings, 'DATABASE_URL', '')).lower()
    is_sqlite = 'sqlite' in db_url
    is_postgresql = 'postgresql' in db_url
    
    # Ensure the database directory exists for SQLite
    if is_sqlite:
        db_path = getattr(settings, 'SQLITE_DB_PATH', ':memory:')
        if db_path != ":memory:":
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
    
    # Create all tables and perform setup
    async with engine.begin() as conn:
        # Database-specific setup
        if is_sqlite:
            # SQLite specific setup
            await conn.execute(text("PRAGMA foreign_keys=ON"))
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA synchronous=NORMAL"))
            await conn.execute(text("PRAGMA busy_timeout=5000"))
            await conn.execute(text("PRAGMA temp_store=MEMORY"))
        elif is_postgresql:
            # PostgreSQL specific setup
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pg_trgm"'))
        
        # Import all models to ensure they are registered with SQLAlchemy
        # This is necessary for create_all to detect all tables
        from .. import models  # noqa: F401
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Run any pending migrations or data seeds
        await _run_migrations(conn)
    
    print("✅ Database initialization completed successfully")


async def _run_migrations(conn: AsyncConnection) -> None:
    """Run any pending database migrations.
    
    This is a placeholder for actual migration logic. In a production app,
    you would use a proper migration tool like Alembic.
    """
    # Example of running a simple migration
    try:
        # Get database URL directly from settings
        db_url = (
            getattr(settings, 'SQLALCHEMY_DATABASE_URI', '') 
            or getattr(settings, 'DATABASE_URL', '')
            or ''
        )
        is_sqlite = 'sqlite' in db_url.lower()
        
        if is_sqlite:
            result = await conn.execute(
                text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='_alembic_version'
                """)
            )
        else:
            result = await conn.execute(
                text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'alembic_version'
                """)
            )
        has_migrations = bool((await result.first()) is not None)
        
        if not has_migrations:
            # This is a fresh database - initialize it
            print("ℹ️  Initializing fresh database")
            await seed_database(conn)
        
    except Exception as e:
        print(f"⚠️  Error running migrations: {e}")
        raise
        

async def seed_database(conn: AsyncConnection) -> None:
    """Initialize database with initial data."""
    print("🌱 Seeding database...")
    
    # Seed users
    await seed_users(conn)
    print("✅ Database seeding completed")


async def seed_users(conn: AsyncConnection) -> None:
    """Seed the database with initial users."""
    from ...core.security import get_password_hash
    from ...models.user import User
    
    # Only seed if no users exist
    try:
        result = await conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar() or 0
        
        if user_count == 0:
            admin_email = settings.FIRST_SUPERUSER_EMAIL
            admin_password = settings.FIRST_SUPERUSER_PASSWORD
            
            # Get password hash function
            from ...core.security import get_password_hash
            
            await conn.execute(
                text("""
                    INSERT INTO users (email, hashed_password, is_active, is_superuser, full_name)
                    VALUES (:email, :hashed_password, :is_active, :is_superuser, :full_name)
                """),
                {
                    "email": admin_email,
                    "hashed_password": get_password_hash(admin_password),
                    "is_active": True,
                    "is_superuser": True,
                    "full_name": "Admin User"
                }
            )
            print(f"👤 Created admin user: {admin_email}")
    except Exception as e:
        print(f"⚠️  Warning: Could not check/seed users table: {e}")
        raise


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
