"""
Test script to diagnose SQLAlchemy database URL parsing issues.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine

async def test_sqlite_connection():
    """Test SQLite database connection with different URL formats."""
    # Test different SQLite URL formats
    test_cases = [
        "sqlite+aiosqlite:///./instance/test.db",
        "sqlite+aiosqlite:///D:/Paksa%20Financial%20System/backend/instance/test.db",
        "sqlite+aiosqlite:///D:\\Paksa Financial System\\backend\\instance\\test.db",
        "sqlite+aiosqlite:///" + str(Path("./instance/test.db").absolute()).replace("\\", "/"),
        "sqlite+aiosqlite:///" + str(Path("./instance/test.db").absolute())
    ]
    
    print("\n=== Testing SQLite Database URLs ===")
    for i, url in enumerate(test_cases, 1):
        engine = None
        try:
            print(f"\nTest {i}: {url}")
            engine = create_async_engine(url)
            print("✅ URL parsed successfully!")
            print(f"Engine created: {engine}")
        except Exception as e:
            print(f"❌ Error: {e.__class__.__name__}: {e}")
        finally:
            if engine is not None:
                await engine.dispose()

if __name__ == "__main__":
    import asyncio
    
    # Create test directory if it doesn't exist
    os.makedirs("instance", exist_ok=True)
    
    # Run the test
    asyncio.run(test_sqlite_connection())
