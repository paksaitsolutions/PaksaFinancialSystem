"""
Minimal SQLite database test script.
"""
import os
import sys
from pathlib import Path
import sqlite3

# Set absolute path to the database
DB_PATH = Path(r"D:\Paksa Financial System\backend\instance\paksa_finance.db")

# Ensure the instance directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

print(f"Using database at: {DB_PATH}")

# Test SQLite connection
try:
    # Test basic SQLite connection
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Test a simple query
    cursor.execute("SELECT sqlite_version()")
    version = cursor.fetchone()
    print(f"SQLite version: {version[0]}")
    
    # Close the connection
    conn.close()
    
    # Test with aiosqlite
    import asyncio
    import aiosqlite
    
    async def test_async_connection():
        async with aiosqlite.connect(str(DB_PATH)) as db:
            async with db.execute("SELECT sqlite_version()") as cursor:
                version = await cursor.fetchone()
                print(f"aiosqlite version: {version[0]}")
    
    asyncio.run(test_async_connection())
    
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    
    # Check directory permissions
    print("\n=== Directory Info ===")
    print(f"Directory exists: {DB_PATH.parent.exists()}")
    print(f"Directory is writable: {os.access(DB_PATH.parent, os.W_OK)}")
    print(f"Directory path: {DB_PATH.parent.absolute()}")
    
    # Try to create a test file
    try:
        test_file = DB_PATH.parent / "test_file.txt"
        with open(test_file, 'w') as f:
            f.write("test")
        test_file.unlink()
        print("Successfully created and deleted test file in directory")
    except Exception as e:
        print(f"Failed to create test file: {e}")
