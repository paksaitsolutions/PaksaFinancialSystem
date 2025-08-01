import os
import re
from pathlib import Path

# Define the root directory
root_dir = Path('frontend/src')

# Define the mapping of old paths to new paths
path_mapping = {
    '@/views/UnderConstruction.vue': '@/views/common/UnderConstruction.vue',
    '@/views/ModuleView.vue': '@/views/common/ModuleView.vue',
    # Add more mappings as needed
}

def update_file_references(file_path):
    """Update import references in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated = False
        for old_path, new_path in path_mapping.items():
            if old_path in content:
                content = content.replace(old_path, new_path)
                updated = True
        
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def find_and_update_references():
    """Find and update references in all relevant files."""
    # File extensions to check
    extensions = ('.ts', '.js', '.vue')
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(extensions):
                file_path = Path(root) / file
                update_file_references(file_path)

def check_for_duplicate_views():
    """Check for any remaining duplicate view files."""
    view_files = {}
    for root, _, files in os.walk(root_dir):
        if 'node_modules' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.vue'):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(root_dir)
                
                if file in view_files:
                    print(f"Duplicate found: {file}")
                    print(f"  - {view_files[file]}")
                    print(f"  - {rel_path}")
                else:
                    view_files[file] = rel_path

if __name__ == "__main__":
    print("Checking for duplicate view files...")
    check_for_duplicate_views()
    
    print("\nUpdating view references...")
    find_and_update_references()
    
    print("\nCleanup complete!")
