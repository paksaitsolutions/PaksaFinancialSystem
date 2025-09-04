import sqlite3
import os

def check_database():
    db_path = os.path.abspath("paksa_finance.db")
    print(f"Checking database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ No tables found in the database!")
        else:
            print("\n✅ Found tables:")
            for table in tables:
                table_name = table[0]
                print(f"\nTable: {table_name}")
                
                # Get table info
                try:
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    
                    print("Columns:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
                except Exception as e:
                    print(f"  Error reading columns: {str(e)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error accessing database: {str(e)}")
        return False

if __name__ == "__main__":
    check_database()
