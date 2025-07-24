"""
Simple script to verify database connection and check for User table.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import SQLAlchemy components
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Database configuration
DB_PATH = Path("D:/Paksa Financial System/backend/instance/paksa_finance.db")
DB_URI = f"sqlite+aiosqlite:///{DB_PATH}"

async def check_database():
    """Check database connection and list tables."""
    print(f"Database path: {DB_PATH}")
    print(f"Database exists: {DB_PATH.exists()}")
    
    # Create async engine
    engine = create_async_engine(
        DB_URI,
        echo=True,
        future=True,
        connect_args={"check_same_thread": False}
    )
    
    try:
        # Test connection
        print("\nTesting database connection...")
        async with engine.connect() as conn:
            print("✅ Successfully connected to the database")
            
            # List all tables
            print("\nListing tables...")
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            )
            tables = result.fetchall()
            
            if not tables:
                print("No tables found in the database")
                return
                
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table[0]}")
            
            # Check if User table exists
            user_table_exists = any(table[0] == 'user' for table in tables)
            print(f"\nUser table exists: {user_table_exists}")
            
            if user_table_exists:
                # Count users
                result = await conn.execute(text("SELECT COUNT(*) FROM user;"))
                count = result.scalar()
                print(f"Number of users: {count}")
                
                if count > 0:
                    # Get sample users
                    result = await conn.execute(
                        text("SELECT id, email, is_active FROM user LIMIT 5;")
                    )
                    users = result.fetchall()
                    print("\nSample users:")
                    for user in users:
                        print(f"- ID: {user[0]}, Email: {user[1]}, Active: {user[2]}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_database())
