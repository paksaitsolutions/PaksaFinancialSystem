"""
Database routing for read/write operations.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.session import get_db
from app.core.db.read_replica import get_read_db

class DatabaseRouter:
    """Route database operations to appropriate instances."""
    
    @staticmethod
    async def get_write_session() -> AsyncGenerator[AsyncSession, None]:
        """Get write database session."""
        async for session in get_db():
            yield session
    
    @staticmethod
    async def get_read_session() -> AsyncGenerator[AsyncSession, None]:
        """Get read database session."""
        async for session in get_read_db():
            yield session

# Global router instance
db_router = DatabaseRouter()