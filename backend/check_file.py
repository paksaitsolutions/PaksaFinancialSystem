import os

def check_file():
    file_path = 'paksa_financial.db'
    print(f"Checking file: {os.path.abspath(file_path)}")
    
    # Check if file exists
    exists = os.path.exists(file_path)
    print(f"File exists: {exists}")
    
    if exists:
        # Get file stats
        stats = os.stat(file_path)
        print(f"File size: {stats.st_size} bytes")
        print(f"Last modified: {stats.st_mtime}")
        print(f"File permissions: {oct(stats.st_mode)[-3:]}")
        
        # Try to read the file
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
                print(f"File header (hex): {header.hex()}")
                print(f"First 16 bytes as text: {header}")
                
                # Check if it's a valid SQLite database
                if header.startswith(b'SQLite format 3\000'):
                    print("This appears to be a valid SQLite database.")
                else:
                    print("Warning: This does not appear to be a valid SQLite database.")
                    
        except Exception as e:
            print(f"Error reading file: {e}")
    
if __name__ == "__main__":
    check_file()
