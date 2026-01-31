#!/usr/bin/env python3
"""
Script to update all API endpoints to use standardized response format and pagination.
This script will update the remaining endpoint files that haven't been converted yet.
"""

import os
import re
from pathlib import Path

# Base directory for endpoints
ENDPOINTS_DIR = Path("d:/PaksaFinancialSystem/backend/app/api/endpoints")

# Files already updated
UPDATED_FILES = {
    "ap.py", "ar.py", "cash.py", "budget.py", "payroll.py"
}

# Standard imports to add
STANDARD_IMPORTS = """from app.core.api_response import success_response, paginated_response, error_response
from app.core.pagination import PaginationParams, paginate_query
from fastapi import Query"""

def update_endpoint_file(file_path):
    """Update a single endpoint file to use standardized responses."""
    print(f"Updating {file_path.name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already updated
        if 'success_response' in content:
            print(f"  ✓ {file_path.name} already updated")
            return
        
        # Add imports after existing FastAPI imports
        if 'from fastapi import' in content and 'success_response' not in content:
            # Find the last FastAPI import line
            lines = content.split('\n')
            insert_index = -1
            
            for i, line in enumerate(lines):
                if line.strip().startswith('from fastapi import') or line.strip().startswith('from sqlalchemy'):
                    insert_index = i
            
            if insert_index != -1:
                lines.insert(insert_index + 1, STANDARD_IMPORTS)
                content = '\n'.join(lines)
        
        # Update return statements to use standardized responses
        patterns = [
            # Simple return dict -> success_response
            (r'return\s+{([^}]+)}', r'return success_response(data={\1}, message="Operation completed successfully")'),
            
            # Return list -> success_response  
            (r'return\s+\[([^\]]+)\]', r'return success_response(data=[\1], message="Data retrieved successfully")'),
            
            # HTTPException -> error_response
            (r'raise HTTPException\(status_code=(\d+),\s*detail="([^"]+)"\)', 
             r'return error_response(message="\2", status_code=\1)'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        # Add pagination parameters to GET endpoints that return lists
        def add_pagination_params(match):
            func_def = match.group(0)
            if 'page:' in func_def or 'limit:' in func_def:
                return func_def  # Already has pagination
            
            # Add pagination parameters before db: Session
            if 'db: Session = Depends(get_db)' in func_def:
                func_def = func_def.replace(
                    'db: Session = Depends(get_db)',
                    'page: int = Query(1, ge=1),\n    page_size: int = Query(20, ge=1, le=100),\n    db: Session = Depends(get_db)'
                )
            
            return func_def
        
        # Find GET endpoints that likely return lists
        content = re.sub(
            r'@router\.get\([^)]*\)\s*\ndef\s+\w+\([^)]*\):',
            add_pagination_params,
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ {file_path.name} updated successfully")
        
    except Exception as e:
        print(f"  ✗ Error updating {file_path.name}: {e}")

def main():
    """Update all endpoint files."""
    print("🔄 Updating API endpoints to use standardized response format...")
    
    if not ENDPOINTS_DIR.exists():
        print(f"❌ Endpoints directory not found: {ENDPOINTS_DIR}")
        return
    
    # Get all Python files in endpoints directory
    endpoint_files = []
    for file_path in ENDPOINTS_DIR.rglob("*.py"):
        if file_path.name != "__init__.py" and file_path.name not in UPDATED_FILES:
            endpoint_files.append(file_path)
    
    print(f"📁 Found {len(endpoint_files)} endpoint files to update")
    
    # Update each file
    for file_path in endpoint_files:
        update_endpoint_file(file_path)
    
    print("\n✅ All endpoint files have been processed!")
    print("\n📋 Summary of changes made:")
    print("  • Added standardized API response imports")
    print("  • Converted return statements to use success_response()")
    print("  • Added pagination parameters to list endpoints")
    print("  • Replaced HTTPException with error_response()")
    
    print("\n⚠️  Manual review needed:")
    print("  • Verify pagination logic is correct for each endpoint")
    print("  • Check that database queries are properly paginated")
    print("  • Test endpoints to ensure they work correctly")

if __name__ == "__main__":
    main()