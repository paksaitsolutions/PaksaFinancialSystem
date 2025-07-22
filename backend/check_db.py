"""
Simple script to check the SQLite database contents.
"""
import sqlite3
from pathlib import Path

def check_db():
    db_path = Path("instance/paksa_finance.db")
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}")
        return
    
    print(f"Checking database at: {db_path.absolute()}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Check users table
        if any('users' in table for table in tables):
            print("\nUsers:")
            cursor.execute("SELECT id, email, first_name, last_name, is_superuser FROM users")
            for row in cursor.fetchall():
                print(f"ID: {row[0]}, Email: {row[1]}, Name: {row[2]} {row[3]}, Is Admin: {bool(row[4])}")
        
        # Check roles table
        if any('roles' in table for table in tables):
            print("\nRoles:")
            cursor.execute("SELECT id, name, is_system FROM roles")
            for row in cursor.fetchall():
                print(f"ID: {row[0]}, Name: {row[1]}, Is System: {bool(row[2])}")
        
        # Check user_roles table
        if any('user_roles' in table for table in tables):
            print("\nUser Roles:")
            cursor.execute("""
                SELECT u.email, r.name 
                FROM user_roles ur
                JOIN users u ON ur.user_id = u.id
                JOIN roles r ON ur.role_id = r.id
            """)
            for row in cursor.fetchall():
                print(f"User: {row[0]}, Role: {row[1]}")
        
        conn.close()
        print("\nDatabase check completed successfully!")
        
    except Exception as e:
        print(f"\nError checking database: {e}")

if __name__ == "__main__":
    check_db()
