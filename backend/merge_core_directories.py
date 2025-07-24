"""
Script to merge app/modules/core into app/core, preserving existing files in app/core.
"""
import os
import shutil
from pathlib import Path

# Define source and destination directories
BACKEND_DIR = Path(__file__).parent.absolute()
MODULES_CORE_DIR = BACKEND_DIR / "app" / "modules" / "core"
CORE_DIR = BACKEND_DIR / "app" / "core"

# Files to exclude from merging (already exist in core with custom changes)
EXCLUDE_FILES = {
    "__pycache__",
    ".pytest_cache",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "*.bak",
    "*_old.py",
    "*.swp"
}

def should_exclude(file_path: Path) -> bool:
    """Check if a file should be excluded from copying."""
    # Check if any part of the path matches an exclude pattern
    for part in file_path.parts:
        if part in EXCLUDE_FILES or any(part.endswith(ext) for ext in ['.pyc', '.pyo', '.pyd', '.bak', '.swp']):
            return True
    return False

def merge_directories(src: Path, dst: Path):
    """
    Recursively merge src directory into dst directory.
    Files in dst take precedence over files in src.
    """
    print(f"Merging {src} into {dst}")
    
    # Ensure destination exists
    dst.mkdir(parents=True, exist_ok=True)
    
    # Process each item in source directory
    for item in src.iterdir():
        if should_exclude(item):
            print(f"  Skipping excluded: {item}")
            continue
            
        dst_item = dst / item.name
        
        # If destination exists and is a file, skip it (don't overwrite)
        if dst_item.exists() and dst_item.is_file():
            print(f"  Skipping existing file: {dst_item}")
            continue
            
        # If source is a directory, recurse
        if item.is_dir():
            print(f"  Creating directory: {dst_item}")
            merge_directories(item, dst_item)
        else:
            # If destination doesn't exist, copy the file
            print(f"  Copying file: {item} -> {dst_item}")
            shutil.copy2(str(item), str(dst_item))

def main():
    print("Starting core directory merge...")
    print(f"Source: {MODULES_CORE_DIR}")
    print(f"Destination: {CORE_DIR}")
    
    if not MODULES_CORE_DIR.exists():
        print(f"Error: Source directory not found: {MODULES_CORE_DIR}")
        return
        
    if not CORE_DIR.exists():
        print(f"Warning: Destination directory not found, creating: {CORE_DIR}")
        CORE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Perform the merge
    merge_directories(MODULES_CORE_DIR, CORE_DIR)
    
    print("\nMerge completed successfully!")
    print("\nNext steps:")
    print("1. Review the changes in the destination directory.")
    print("2. Update any imports in the codebase to point to the new locations.")
    print("3. Run tests to ensure everything works as expected.")
    print("4. Once verified, you can remove the source directory if desired.")

if __name__ == "__main__":
    main()
