"""
Database configuration and session management.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.core.config.settings import settings

# Create sync engine (avoiding async issues)
sync_db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

if sync_db_url.startswith("sqlite"):
    engine = create_engine(
        sync_db_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        sync_db_url,
        echo=settings.DEBUG
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create base class for models
Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Import all models to ensure they are registered
    from app.models import user  # noqa
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create first superuser if it doesn't exist
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Check if superuser exists
        existing_user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
        if not existing_user:
            # Create superuser
            hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
            superuser = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=hashed_password,
                first_name="System",
                last_name="Administrator",
                is_active=True,
                is_superuser=True
            )
            db.add(superuser)
            db.commit()
            print(f"✅ Created superuser: {settings.FIRST_SUPERUSER_EMAIL}")
    finally:
        db.close()