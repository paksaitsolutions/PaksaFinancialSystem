"""
Utility to add permissions to all endpoints automatically.
"""
import os
import re
from pathlib import Path

def add_permissions_to_endpoints():
    """Add permission checks to all API endpoints."""
    
    # Permission mapping for different modules
    MODULE_PERMISSIONS = {
        'inventory': {
            'read': 'Permission.INVENTORY_READ',
            'write': 'Permission.INVENTORY_WRITE', 
            'delete': 'Permission.INVENTORY_DELETE'
        },
        'tax': {
            'read': 'Permission.TAX_READ',
            'write': 'Permission.TAX_WRITE',
            'delete': 'Permission.TAX_DELETE'
        },
        'accounts_receivable': {
            'read': 'Permission.AR_READ',
            'write': 'Permission.AR_WRITE',
            'delete': 'Permission.AR_DELETE'
        }
    }
    
    # HTTP method to permission mapping
    METHOD_PERMISSION_MAP = {
        'GET': 'read',
        'POST': 'write',
        'PUT': 'write',
        'PATCH': 'write',
        'DELETE': 'delete'
    }
    
    # Find all endpoint files
    api_dir = Path(__file__).parent.parent / 'api' / 'endpoints'
    
    for module_dir in api_dir.iterdir():
        if module_dir.is_dir() and module_dir.name in MODULE_PERMISSIONS:
            module_name = module_dir.name
            permissions = MODULE_PERMISSIONS[module_name]
            
            for py_file in module_dir.glob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                    
                print(f"Processing {py_file}")
                add_permissions_to_file(py_file, permissions, METHOD_PERMISSION_MAP)

def add_permissions_to_file(file_path, permissions, method_map):
    """Add permissions to a specific file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if permissions import already exists
    if 'from app.core.permissions import' not in content:
        # Add import after other core imports
        import_pattern = r'(from app\.core\.api_response import[^\n]+\n)'
        replacement = r'\1from app.core.permissions import require_permission, Permission\n'
        content = re.sub(import_pattern, replacement, content)
    
    # Find all router decorators and add permissions
    router_pattern = r'@router\.(get|post|put|patch|delete)\([^)]+\)\s*\nasync def ([^(]+)\(\s*\*,\s*\n(\s+)([^:]+):'
    
    def add_permission_param(match):
        method = match.group(1).upper()
        func_name = match.group(2)
        indent = match.group(3)
        params = match.group(4)
        
        # Skip if permission already exists
        if '_: bool = Depends(require_permission' in params:
            return match.group(0)
        
        # Determine permission based on method
        perm_type = method_map.get(method, 'read')
        permission = permissions.get(perm_type, 'Permission.READ')
        
        # Add permission parameter
        new_params = params + f',\n{indent}_: bool = Depends(require_permission({permission})),'
        
        return f"@router.{match.group(1)}({match.group(0).split('(', 1)[1].split(')', 1)[0]})\nasync def {func_name}(\n{indent}*,\n{indent}{new_params}:"
    
    content = re.sub(router_pattern, add_permission_param, content, flags=re.MULTILINE)
    
    with open(file_path, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    add_permissions_to_endpoints()