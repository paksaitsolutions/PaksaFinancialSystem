import sqlite3
import os

def test_sqlite():
    db_path = 'paksa_finance.db'
    print(f"Checking SQLite database at: {os.path.abspath(db_path)}")
    
    # Check if file exists
    if not os.path.exists(db_path):
        print("Database file does not exist. Creating a new one...")
        
    # Connect to SQLite database (will create if doesn't exist)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if we can execute a simple query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\nTables in the database:")
        if tables:
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("No tables found in the database.")
            
        # Show SQLite version
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        print(f"\nSQLite version: {version[0]}")
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    test_sqlite()
