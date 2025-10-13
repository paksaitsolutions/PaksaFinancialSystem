#!/usr/bin/env python3
"""
Create missing database tables
"""
from app.core.database import engine, init_db
from app.models.base import Base
from app.models.core_models import *
import asyncio

def create_missing_tables():
    """Create any missing tables"""
    print("Creating missing database tables...")
    
    # Create all tables defined in models
    Base.metadata.create_all(bind=engine)
    
    print("All tables created successfully!")
    
    # List all tables
    import sqlite3
    conn = sqlite3.connect('paksa_financial.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    print(f"\nTotal tables in database: {len(tables)}")
    for table in tables:
        print(f"- {table[0]}")
    
    conn.close()

if __name__ == "__main__":
    create_missing_tables()