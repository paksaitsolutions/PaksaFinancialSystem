"""
Simple script to initialize SQLite database for Paksa Financial System.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Ensure the instance directory exists
instance_path = project_root / 'instance'
instance_path.mkdir(exist_ok=True)

def init_db():
    """Initialize the SQLite database."""
    import sqlite3
    from datetime import datetime, timedelta
    from passlib.context import CryptContext
    
    # Database file path
    db_path = instance_path / 'paksa_finance.db'
    
    # Remove existing database if it exists
    if db_path.exists():
        print(f"Removing existing database: {db_path}")
        db_path.unlink()
    
    print(f"Creating new SQLite database: {db_path}")
    
    # Connect to SQLite database (will create if it doesn't exist)
    conn = sqlite3.connect(db_path)
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
        is_verified BOOLEAN DEFAULT 0,
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
    
    # Create admin role
    cursor.execute("""
    INSERT INTO roles (name, description, is_system) 
    VALUES (?, ?, ?)
    """, ("System Administrator", "Full system access with all permissions", 1))
    
    # Get the admin role ID
    cursor.execute("SELECT last_insert_rowid()")
    admin_role_id = cursor.fetchone()[0]
    
    # Hash the admin password
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("Paksa@123")
    
    # Create admin user
    cursor.execute("""
    INSERT INTO users (email, hashed_password, first_name, last_name, is_active, is_superuser, is_verified)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("admin@paksa.finance", hashed_password, "Admin", "User", 1, 1, 1))
    
    # Get the admin user ID
    cursor.execute("SELECT last_insert_rowid()")
    admin_user_id = cursor.fetchone()[0]
    
    # Assign admin role to admin user
    cursor.execute("""
    INSERT INTO user_roles (user_id, role_id)
    VALUES (?, ?)
    """, (admin_user_id, admin_role_id))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nDatabase initialized successfully!")
    print("Admin user created with the following credentials:")
    print(f"Email: admin@paksa.finance")
    print(f"Password: Paksa@123")
    print("\nYou can now start the backend server and login with these credentials.")

if __name__ == "__main__":
    init_db()
