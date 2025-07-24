"""
Test script to verify database connection and authentication functionality.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Database configuration
DB_DIR = Path("D:/Paksa Financial System/backend/instance")
DB_PATH = DB_DIR / "paksa_finance.db"
DB_URI = f"sqlite+aiosqlite:///{DB_PATH}"

# Create async engine
engine = create_async_engine(
    DB_URI,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False}
)

# Create async session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def test_db_connection():
    """Test database connection and list tables."""
    print("Testing database connection...")
    try:
        async with engine.connect() as conn:
            print("✅ Successfully connected to the database")
            
            # List all tables
            result = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
            tables = result.fetchall()
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table[0]}")
            
            return True
    except Exception as e:
        print(f"❌ Error connecting to the database: {e}")
        return False

async def test_user_table():
    """Test if the User table exists and has records."""
    print("\nChecking User table...")
    try:
        async with async_session_factory() as session:
            # Check if User table exists
            result = await session.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='user';"
            )
            if not result.scalar():
                print("❌ User table does not exist in the database")
                return False
            
            # Count users
            result = await session.execute("SELECT COUNT(*) FROM user;")
            count = result.scalar()
            print(f"✅ Found {count} users in the database")
            
            # List users (first 5)
            if count > 0:
                result = await session.execute("SELECT id, email, is_active FROM user LIMIT 5;")
                users = result.fetchall()
                print("\nSample users:")
                for user in users:
                    print(f"- ID: {user[0]}, Email: {user[1]}, Active: {user[2]}")
            
            return True
    except Exception as e:
        print(f"❌ Error querying User table: {e}")
        return False

async def main():
    """Run database tests."""
    print(f"Database path: {DB_PATH}")
    
    # Test database connection
    db_ok = await test_db_connection()
    if not db_ok:
        print("\n❌ Database connection test failed")
        return
    
    # Test User table
    await test_user_table()
    
    print("\n✅ Database tests completed")

if __name__ == "__main__":
    asyncio.run(main())
