"""
Database migration utilities.
"""
from sqlalchemy.ext.asyncio import AsyncEngine
from app.models.base import Base
from app.core.db.session import engine

async def create_tables():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """Drop all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def recreate_tables():
    """Drop and recreate all tables."""
    await drop_tables()
    await create_tables()