import sqlite3
import os

def inspect_database():
    db_path = 'paksa_financial.db'
    print(f"Inspecting database at: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print("Error: Database file does not exist.")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return
            
        print("\n=== Tables in the database ===")
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 8))
            
            # Get table schema
            try:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                if not columns:
                    print("  No columns found")
                    continue
                    
                print("  Columns:")
                for col in columns:
                    col_id, name, col_type, notnull, default_value, pk = col
                    print(f"    {name} ({col_type}){' PRIMARY KEY' if pk else ''} "
                          f"{'NOT NULL' if notnull else ''} "
                          f"DEFAULT {default_value if default_value is not None else 'NULL'}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"  Rows: {count}")
                
                # Show first few rows if table has data
                if count > 0:
                    print("  Sample data:")
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    col_names = [desc[0] for desc in cursor.description]
                    print("    " + " | ".join(col_names))
                    print("    " + "-" * (sum(len(str(c)) + 3 for c in col_names) - 1))
                    
                    for row in rows:
                        print("    " + " | ".join(str(r) for r in row))
                
            except sqlite3.Error as e:
                print(f"  Error inspecting table {table_name}: {e}")
                
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    inspect_database()
