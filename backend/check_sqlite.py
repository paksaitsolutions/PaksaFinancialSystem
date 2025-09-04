import sqlite3
import os

def check_db():
    db_path = os.path.abspath("paksa_finance.db")
    print(f"Checking database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database file does not exist!")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database!")
        else:
            print("\nTables in database:")
            for table in tables:
                table_name = table[0]
                print(f"\nTable: {table_name}")
                
                # Get table info
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                print("Columns:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"  Rows: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error accessing database: {str(e)}")

if __name__ == "__main__":
    check_db()
