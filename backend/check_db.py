import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_database():
    # Database URL - should match your configuration
    DATABASE_URL = "sqlite+aiosqlite:///./paksa_finance.db"
    
    print(f"Connecting to database at: {DATABASE_URL}")
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        # Test connection
        async with engine.begin() as conn:
            print("Successfully connected to the database")
            
            # List all tables
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            )
            tables = result.scalars().all()
            
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table}")
                
                # Get table info
                try:
                    table_info = await conn.execute(
                        text(f"PRAGMA table_info({table});")
                    )
                    print(f"  Columns:")
                    for col in table_info:
                        print(f"  - {col['name']} ({col['type']})")
                except Exception as e:
                    print(f"  Could not get info for table {table}: {e}")
                
    except Exception as e:
        print(f"Error connecting to the database: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_database())
