"""
Script to verify SQLite database file and its contents.
"""
import os
import sys
import sqlite3
from pathlib import Path

def verify_database():
    """Verify the SQLite database file and its contents."""
    # Define paths
    project_root = Path(__file__).parent
    db_path = project_root / 'instance' / 'paksa_finance.db'
    
    print("Verifying database setup...")
    print("=" * 60)
    
    # Check if database file exists
    if not db_path.exists():
        print(f"❌ Error: Database file not found at: {db_path}")
        print("\nPlease run the database initialization script first:")
        print("  python init_db_fixed.py")
        return False
    
    print(f"✅ Database file found at: {db_path}")
    print(f"   Size: {db_path.stat().st_size / 1024:.2f} KB")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        print("\nTables in database:")
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"- {table}: {', '.join(columns)}")
        
        # Check users
        if 'users' in tables:
            cursor.execute("SELECT id, email, first_name, last_name, is_superuser FROM users")
            users = cursor.fetchall()
            print("\nUsers:")
            for user in users:
                print(f"  - ID: {user[0]}, Email: {user[1]}, Name: {user[2]} {user[3]}, Is Admin: {bool(user[4])}")
        
        # Check roles
        if 'roles' in tables:
            cursor.execute("SELECT id, name, is_system FROM roles")
            roles = cursor.fetchall()
            print("\nRoles:")
            for role in roles:
                print(f"  - ID: {role[0]}, Name: {role[1]}, Is System: {bool(role[2])}")
        
        # Check user_roles
        if 'user_roles' in tables and 'users' in tables and 'roles' in tables:
            cursor.execute("""
                SELECT u.email, r.name 
                FROM user_roles ur
                JOIN users u ON ur.user_id = u.id
                JOIN roles r ON ur.role_id = r.id
            """)
            user_roles = cursor.fetchall()
            print("\nUser Roles:")
            for user_role in user_roles:
                print(f"  - User: {user_role[0]}, Role: {user_role[1]}")
        
        conn.close()
        print("\n✅ Database verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error verifying database: {str(e)}")
        return False

if __name__ == "__main__":
    verify_database()
