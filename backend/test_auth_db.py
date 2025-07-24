"""
Test script to verify database connection and authentication functionality
using the application's database configuration.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import application settings and database utilities
from app.core.config import settings
from app.core.db.session import async_session_factory

async def test_database_connection():
    """Test the database connection using the application's configuration."""
    print("Testing database connection...")
    print(f"Database URL: {settings.SQLALCHEMY_DATABASE_URI}")
    
    try:
        # Create a new async session
        async with async_session_factory() as session:
            # Execute a simple query to test the connection
            result = await session.execute("SELECT 1")
            value = result.scalar()
            
            if value == 1:
                print("✅ Successfully connected to the database")
                return True
            else:
                print(f"❌ Unexpected result from database: {value}")
                return False
    except Exception as e:
        print(f"❌ Error connecting to the database: {e}")
        return False

async def list_database_tables():
    """List all tables in the database."""
    print("\nListing database tables...")
    try:
        async with async_session_factory() as session:
            # SQLite specific query to list tables
            result = await session.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
            tables = result.fetchall()
            
            if not tables:
                print("No tables found in the database")
                return []
            
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table[0]}")
            
            return [table[0] for table in tables]
    except Exception as e:
        print(f"❌ Error listing tables: {e}")
        return []

async def check_user_table():
    """Check if the User table exists and has records."""
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
    print("Starting database tests...")
    
    # Test database connection
    db_ok = await test_database_connection()
    if not db_ok:
        print("\n❌ Database connection test failed")
        return
    
    # List all tables
    tables = await list_database_tables()
    
    # Check User table if it exists
    if 'user' in tables:
        await check_user_table()
    else:
        print("\n⚠️ User table not found in the database")
    
    print("\n✅ Database tests completed")

if __name__ == "__main__":
    asyncio.run(main())
