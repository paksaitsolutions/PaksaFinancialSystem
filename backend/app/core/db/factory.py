"""
Consolidated database session factory.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.session import async_session_factory

class DatabaseSessionFactory:
    """Centralized database session factory."""
    
    def __init__(self):
        self._session_factory = async_session_factory
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_session(self) -> AsyncSession:
        """Create new session for direct use."""
        return self._session_factory()

# Global factory instance
db_factory = DatabaseSessionFactory()