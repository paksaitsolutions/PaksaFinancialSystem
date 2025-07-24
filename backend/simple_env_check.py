"""
Simple script to check Python environment and directory structure.
"""
import os
import sys
import platform
from pathlib import Path

def main():
    print("=" * 80)
    print("Simple Environment Check")
    print("=" * 80)
    
    # Basic info
    print("\nPython Info:")
    print(f"Version: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    
    # Current directory
    current_dir = Path.cwd()
    print(f"\nCurrent Directory: {current_dir}")
    
    # List files in current directory
    print("\nFiles in current directory:")
    for f in current_dir.iterdir():
        print(f"  - {f.name}")
    
    # Check for app directory
    app_dir = current_dir / "app"
    print(f"\nApp directory exists: {app_dir.exists()}")
    
    if app_dir.exists():
        print("\nApp directory structure:")
        for f in app_dir.rglob("*.py"):
            print(f"  - {f.relative_to(current_dir)}")
    
    # Python path
    print("\nPython Path:")
    for i, path in enumerate(sys.path, 1):
        print(f"  {i}. {path}")

if __name__ == "__main__":
    main()
