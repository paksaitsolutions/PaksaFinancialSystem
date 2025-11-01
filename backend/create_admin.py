#!/usr/bin/env python3
"""Create admin user for testing"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password
import uuid

def create_admin_user():
    db = next(get_db())
    
    # Check if admin user exists
    admin_user = db.query(User).filter(User.email == 'admin@paksa.com').first()
    
    if admin_user:
        print(f"Admin user exists: {admin_user.email}")
        print(f"Is active: {admin_user.is_active}")
        print(f"Is superuser: {admin_user.is_superuser}")
        
        # Test password
        password_valid = verify_password('admin123', admin_user.hashed_password)
        print(f"Password 'admin123' is valid: {password_valid}")
        
        if not password_valid:
            print("Updating password...")
            admin_user.hashed_password = get_password_hash('admin123')
            db.commit()
            print("Password updated")
    else:
        print("Creating admin user...")
        admin_user = User(
            id=uuid.uuid4(),
            email='admin@paksa.com',
            hashed_password=get_password_hash('admin123'),
            first_name='System',
            last_name='Administrator',
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully")
    
    # Test authentication
    auth_result = User.authenticate(db, 'admin@paksa.com', 'admin123')
    print(f"Authentication test: {'SUCCESS' if auth_result else 'FAILED'}")

if __name__ == "__main__":
    create_admin_user()