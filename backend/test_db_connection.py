import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os

async def test_connection():
    # Use the same database URL as in settings
    db_url = "sqlite+aiosqlite:///./paksa_financial.db"
    print(f"Testing connection to: {db_url}")
    
    # Create async engine
    engine = create_async_engine(
        db_url,
        echo=True,  # Enable SQL query logging
        connect_args={"check_same_thread": False}  # SQLite specific
    )
    
    try:
        # Test connection
        async with engine.begin() as conn:
            print("\nSuccessfully connected to the database!")
            
            # Get SQLite version
            result = await conn.execute(text("SELECT sqlite_version()"))
            version = result.scalar()
            print(f"SQLite version: {version}")
            
            # List all tables
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = result.scalars().all()
            
            if not tables:
                print("\nNo tables found in the database.")
            else:
                print("\nTables in the database:")
                for table in tables:
                    print(f"- {table}")
                    
                    # Get table info
                    result = await conn.execute(
                        text(f"PRAGMA table_info({table})")
                    )
                    columns = result.fetchall()
                    
                    print(f"  Columns:")
                    for col in columns:
                        print(f"    {col['name']} ({col['type']}) "
                              f"{'PRIMARY KEY' if col['pk'] > 0 else ''}")
                    
                    # Get row count
                    result = await conn.execute(
                        text(f"SELECT COUNT(*) FROM {table}")
                    )
                    count = result.scalar()
                    print(f"  Rows: {count}")
                    
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        await engine.dispose()
        print("\nConnection closed.")

if __name__ == "__main__":
    print("=== Testing Database Connection ===\n")
    asyncio.run(test_connection())
