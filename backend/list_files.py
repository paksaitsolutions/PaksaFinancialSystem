"""
Script to list all files in the backend directory and its subdirectories.
"""
import os
from pathlib import Path

def list_files(directory, max_depth=5, current_depth=0, ignore_dirs=None):
    """Recursively list all files in the given directory."""
    if ignore_dirs is None:
        ignore_dirs = {'__pycache__', '.git', '.idea', 'venv', 'env', 'node_modules'}
    
    # Get all entries in the directory
    try:
        entries = os.listdir(directory)
    except PermissionError:
        print(f"  " * current_depth + f"🔒 Permission denied: {directory}")
        return
    except FileNotFoundError:
        print(f"  " * current_depth + f"❌ Directory not found: {directory}")
        return
    
    # Sort entries with directories first, then files
    dirs = []
    files = []
    
    for entry in entries:
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            dirs.append(entry)
        else:
            files.append(entry)
    
    # Print files in the current directory
    for file in sorted(files):
        file_path = os.path.join(directory, file)
        file_size = os.path.getsize(file_path)
        print(f"  " * current_depth + f"📄 {file} ({file_size} bytes)")
    
    # Recursively process subdirectories
    if current_depth < max_depth:
        for dir_name in sorted(dirs):
            if dir_name not in ignore_dirs:
                full_path = os.path.join(directory, dir_name)
                print(f"  " * current_depth + f"📁 {dir_name}/")  # Print directory name
                list_files(full_path, max_depth, current_depth + 1, ignore_dirs)

def main():
    """Main function to list files in the backend directory."""
    backend_dir = Path(__file__).parent
    print(f"🔍 Listing files in: {backend_dir}")
    
    # Check if directory exists
    if not backend_dir.exists() or not backend_dir.is_dir():
        print(f"❌ Directory does not exist: {backend_dir}")
        return
    
    # List all files
    print(f"📁 {backend_dir.name}/")
    list_files(backend_dir, max_depth=5)
    
    # Check for common database files
    print("\n🔍 Checking for common database files...")
    db_extensions = ['.db', '.sqlite', '.sqlite3', '.db3']
    db_files_found = False
    
    for ext in db_extensions:
        for db_file in backend_dir.glob(f"*{ext}"):
            db_size = db_file.stat().st_size
            print(f"✅ Found database file: {db_file.name} ({db_size} bytes)")
            db_files_found = True
    
    if not db_files_found:
        print("❌ No database files found with common extensions.")
    
    # Check for .env file
    env_file = backend_dir / ".env"
    if env_file.exists():
        print(f"\n✅ Found .env file: {env_file}")
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
                print(f"   Contains {len(lines)} lines (sensitive content not shown)")
        except Exception as e:
            print(f"   Could not read .env file: {e}")
    else:
        print("\n❌ No .env file found in the backend directory.")

if __name__ == "__main__":
    main()
