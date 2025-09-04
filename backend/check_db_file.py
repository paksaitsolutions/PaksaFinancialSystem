import os
import sys

def check_db_file():
    db_path = 'paksa_financial.db'
    print(f"Checking database file: {os.path.abspath(db_path)}")
    
    # Check if file exists
    if not os.path.exists(db_path):
        print("Error: Database file does not exist.")
        return False
    
    # Check file size
    size = os.path.getsize(db_path)
    print(f"File size: {size} bytes")
    
    # Try to read first 100 bytes
    try:
        with open(db_path, 'rb') as f:
            header = f.read(100)
            print("\nFirst 100 bytes (hex):")
            print(header.hex())
            
            print("\nFirst 100 bytes (text):")
            print(header.decode('ascii', errors='replace'))
            
            # Check SQLite header
            if header.startswith(b'SQLite format 3\x00'):
                print("\nThis appears to be a valid SQLite database file.")
            else:
                print("\nWarning: This does not appear to be a valid SQLite database file.")
                
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Database File Check ===\n")
    if check_db_file():
        print("\nFile check completed successfully.")
    else:
        print("\nFile check failed.")
        sys.exit(1)
