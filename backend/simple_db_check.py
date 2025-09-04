import sqlite3

def check_db():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('paksa_financial.db')
        cursor = conn.cursor()
        
        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
        else:
            print("Tables in the database:")
            for table in tables:
                print(f"- {table[0]}")
                
                # Get column info for each table
                cursor.execute(f"PRAGMA table_info({table[0]})")
                columns = cursor.fetchall()
                print(f"  Columns: {', '.join(col[1] for col in columns)}")
                
        conn.close()
        print("\nDatabase check completed successfully!")
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_db()
