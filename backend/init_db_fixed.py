"""
Robust script to initialize SQLite database for Paksa Financial System.
"""
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from passlib.context import CryptContext

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def init_database():
    """Initialize the SQLite database with required tables and admin user."""
    # Ensure the instance directory exists
    instance_path = project_root / 'instance'
    instance_path.mkdir(exist_ok=True)
    
    db_path = instance_path / 'paksa_finance.db'
    
    print(f"Initializing database at: {db_path.absolute()}")
    
    # Remove existing database if it exists
    if db_path.exists():
        print("Removing existing database...")
        os.remove(db_path)
    
    # Connect to SQLite database (will create if it doesn't exist)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        hashed_password TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        is_active BOOLEAN DEFAULT 1,
        is_superuser BOOLEAN DEFAULT 0,
        is_verified BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create roles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        is_system BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create user_roles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_roles (
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, role_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
    )
    """)
    
    # Create refresh_tokens table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL UNIQUE,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)
    
    # Create admin role
    cursor.execute("""
    INSERT OR IGNORE INTO roles (name, description, is_system) 
    VALUES (?, ?, ?)
    """, ("System Administrator", "Full system access with all permissions", 1))
    
    # Get or create admin role ID
    cursor.execute("SELECT id FROM roles WHERE name = ?", ("System Administrator",))
    admin_role = cursor.fetchone()
    
    if admin_role:
        admin_role_id = admin_role[0]
    else:
        cursor.execute("SELECT last_insert_rowid()")
        admin_role_id = cursor.fetchone()[0]
    
    # Hash the admin password
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    admin_email = "admin@paksa.finance"
    admin_password = "Paksa@123"  # This should be the same as in .env
    hashed_password = pwd_context.hash(admin_password)
    
    # Create admin user
    cursor.execute("""
    INSERT OR REPLACE INTO users (email, hashed_password, first_name, last_name, is_active, is_superuser, is_verified)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (admin_email, hashed_password, "Admin", "User", 1, 1, 1))
    
    # Get admin user ID
    cursor.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
    admin_user = cursor.fetchone()
    
    if admin_user:
        admin_user_id = admin_user[0]
    else:
        cursor.execute("SELECT last_insert_rowid()")
        admin_user_id = cursor.fetchone()[0]
    
    # Assign admin role to admin user
    cursor.execute("""
    INSERT OR REPLACE INTO user_roles (user_id, role_id)
    VALUES (?, ?)
    """, (admin_user_id, admin_role_id))
    
    # Create a test refresh token that expires in 7 days
    from datetime import datetime, timedelta
    expires_at = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    test_token = "test_refresh_token_123456"
    
    cursor.execute("""
    INSERT OR REPLACE INTO refresh_tokens (user_id, token, expires_at)
    VALUES (?, ?, ?)
    """, (admin_user_id, test_token, expires_at))
    
    # Commit changes and close connection
    conn.commit()
    
    # Verify the data was inserted
    print("\nVerifying database setup:")
    print("-" * 40)
    
    # Check users
    cursor.execute("SELECT id, email, is_superuser FROM users")
    users = cursor.fetchall()
    print("Users:")
    for user in users:
        print(f"  - ID: {user[0]}, Email: {user[1]}, Is Admin: {bool(user[2])}")
    
    # Check roles
    cursor.execute("SELECT id, name, is_system FROM roles")
    roles = cursor.fetchall()
    print("\nRoles:")
    for role in roles:
        print(f"  - ID: {role[0]}, Name: {role[1]}, Is System: {bool(role[2])}")
    
    # Check user_roles
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
    
    # Check refresh_tokens
    cursor.execute("""
    SELECT u.email, rt.token, rt.expires_at 
    FROM refresh_tokens rt
    JOIN users u ON rt.user_id = u.id
    """)
    tokens = cursor.fetchall()
    print("\nRefresh Tokens:")
    for token in tokens:
        print(f"  - User: {token[0]}, Token: {token[1][:10]}..., Expires: {token[2]}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("DATABASE INITIALIZATION COMPLETE!")
    print("=" * 60)
    print(f"\nAdmin user created with the following credentials:")
    print(f"  Email:    {admin_email}")
    print(f"  Password: {admin_password}")
    print("\nYou can now start the backend server and login with these credentials.")
    print("\nDatabase location:", db_path.absolute())
    print("\nTo start the backend server, run:")
    print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    init_database()
