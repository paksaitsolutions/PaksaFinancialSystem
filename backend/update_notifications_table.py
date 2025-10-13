#!/usr/bin/env python3
"""
Update notifications table schema
"""
import sqlite3
from datetime import datetime

def update_notifications_table():
    conn = sqlite3.connect('paksa_financial.db')
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(notifications)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns
        if 'notification_type' not in columns:
            cursor.execute("ALTER TABLE notifications ADD COLUMN notification_type TEXT DEFAULT 'info'")
            print("Added notification_type column")
        
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE notifications ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            print("Added created_at column")
        
        if 'priority' not in columns:
            cursor.execute("ALTER TABLE notifications ADD COLUMN priority TEXT DEFAULT 'normal'")
            print("Added priority column")
        
        if 'is_read' not in columns:
            cursor.execute("ALTER TABLE notifications ADD COLUMN is_read BOOLEAN DEFAULT 0")
            print("Added is_read column")
        
        conn.commit()
        print("Notifications table updated successfully")
        
    except Exception as e:
        print(f"Error updating table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_notifications_table()