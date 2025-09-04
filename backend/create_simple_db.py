"""
Create a simple SQLite database in the backend directory.
"""
import os
import sqlite3

def create_database():
    # Database path in the backend directory
    db_path = os.path.join(os.path.dirname(__file__), "paksa_financial.db")
    
    print(f"Creating database at: {os.path.abspath(db_path)}")
    
    try:
        # Connect to SQLite database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a test table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Insert test data
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("Test Entry",))
        
        # Commit changes
        conn.commit()
        
        # Verify data
        cursor.execute("SELECT * FROM test_table")
        rows = cursor.fetchall()
        
        print("\n✅ Database created successfully!")
        print(f"\nTest data in database:")
        for row in rows:
            print(f"- ID: {row[0]}, Name: {row[1]}, Created: {row[2]}")
            
        print(f"\nDatabase location: {os.path.abspath(db_path)}")
        
    except Exception as e:
        print(f"\n❌ Error creating database: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    create_database()
