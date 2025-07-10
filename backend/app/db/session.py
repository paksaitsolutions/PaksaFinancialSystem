"""
Database session management.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SessionType

from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
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
    expire_on_commit=True,
)

def get_db() -> Generator[SessionType, None, None]:
    """
    Dependency function that yields database sessions.
    
    This should be used as a FastAPI dependency to get a database session.
    The session is automatically closed when the request is done.
    
    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
