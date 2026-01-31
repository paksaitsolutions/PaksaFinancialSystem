#!/usr/bin/env python3
"""
Add copyright headers to all Python files
Copyright (c) 2024 Paksa IT Solutions
"""

import os
from pathlib import Path

COPYRIGHT_HEADER = '''"""
Copyright (c) 2024 Paksa IT Solutions
All rights reserved.

This software is proprietary to Paksa IT Solutions.
Unauthorized copying or distribution is prohibited.

Project: Paksa Financial System
Website: https://paksa.com
"""

'''

def add_copyright_header(file_path: Path):
    """Add copyright header to Python file if not present."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already has copyright
    if 'Paksa IT Solutions' in content[:500]:
        return False
    
    # Add header
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(COPYRIGHT_HEADER + content)
    
    return True

def process_directory(directory: Path):
    """Process all Python files in directory."""
    count = 0
    for py_file in directory.rglob('*.py'):
        # Skip virtual environment and migrations
        if '.venv' in str(py_file) or 'alembic' in str(py_file):
            continue
        
        if add_copyright_header(py_file):
            print(f"Added header to: {py_file}")
            count += 1
    
    return count

if __name__ == "__main__":
    backend_dir = Path(__file__).parent
    count = process_directory(backend_dir / 'app')
    print(f"\nAdded copyright headers to {count} files")