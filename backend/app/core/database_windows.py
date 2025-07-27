"""
Windows-compatible database configuration using asyncpg.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Use asyncpg for Windows compatibility
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://paksa_user:paksa_local_2024@localhost:5432/paksa_financial_local"
)

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()