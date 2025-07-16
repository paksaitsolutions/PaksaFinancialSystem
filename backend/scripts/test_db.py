"""
Test script to verify database configuration and connectivity.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Import the database configuration
from app.core.config import settings
from app.modules.core.database import Base, init_db, get_db_session

# Create a test model
class TestModel(Base):
    __tablename__ = "test_model"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


async def test_database_connection():
    """Test database connection and basic operations."""
    print(f"Using database URL: {settings.DATABASE_URI}")
    
    # Initialize the database
    print("Initializing database...")
    await init_db()
    
    # Test creating a record
    async with get_db_session() as session:
        print("Creating test record...")
        test_record = TestModel(name="Test Record")
        session.add(test_record)
        await session.commit()
        record_id = test_record.id
        print(f"Created test record with ID: {record_id}")
    
    # Test reading the record
    async with get_db_session() as session:
        print("Reading test record...")
        result = await session.execute(
            TestModel.__table__.select().where(TestModel.id == record_id)
        )
        record = result.first()
        if record:
            print(f"Found record: {dict(record)}")
        else:
            print("Error: Could not find the test record")
    
    # Test updating the record
    async with get_db_session() as session:
        print("Updating test record...")
        result = await session.execute(
            TestModel.__table__.select().where(TestModel.id == record_id)
        )
        record = result.first()
        if record:
            test_record = TestModel(**dict(record))
            test_record.name = "Updated Test Record"
            session.add(test_record)
            await session.commit()
            print(f"Updated record name to: {test_record.name}")
        else:
            print("Error: Could not find the test record to update")
    
    # Test deleting the record
    async with get_db_session() as session:
        print("Deleting test record...")
        result = await session.execute(
            TestModel.__table__.delete().where(TestModel.id == record_id)
        )
        await session.commit()
        print(f"Deleted {result.rowcount} record(s)")
    
    print("Database tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_database_connection())
