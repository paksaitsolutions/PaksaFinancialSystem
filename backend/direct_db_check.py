import sqlite3
import os

def check_database():
    db_path = 'paksa_financial.db'
    print(f"Checking database at: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print("Error: Database file does not exist!")
        return False
    
    try:
        # Try to connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check SQLite version
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"SQLite version: {version}")
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return False
            
        print("\n=== Tables in the database ===")
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 8))
            
            # Get table info
            try:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print("  Columns:")
                for col in columns:
                    col_id, name, col_type, notnull, default_val, pk = col
                    print(f"    {name} ({col_type}) "
                          f"{'PRIMARY KEY' if pk else ''} "
                          f"{'NOT NULL' if notnull else ''} "
                          f"DEFAULT {default_val if default_val is not None else 'NULL'}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  Rows: {count}")
                
                # Show first few rows if table has data
                if count > 0:
                    print("  Sample data (first 5 rows):")
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    col_names = [desc[0] for desc in cursor.description]
                    print("    " + " | ".join(col_names))
                    print("    " + "-" * (sum(len(str(c)) + 3 for c in col_names) - 1))
                    
                    for row in rows:
                        print("    " + " | ".join(str(r) for r in row))
                        
            except sqlite3.Error as e:
                print(f"  Error reading table {table_name}: {e}")
                
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    print("=== Direct Database Check ===\n")
    success = check_database()
    if success:
        print("\nDatabase check completed successfully!")
    else:
        print("\nDatabase check failed.")
