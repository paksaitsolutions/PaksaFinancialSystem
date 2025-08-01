import os
import shutil
from pathlib import Path

# Define the source and target directories
src_dir = Path('frontend/src/views')
target_dir = Path('frontend/src/views')

# Define the mapping of files to their target modules
file_mapping = {
    'Dashboard.vue': 'dashboard/Dashboard.vue',
    'HRMView.vue': 'hrm/HRMView.vue',
    'Home.vue': 'home/Home.vue',
    'ModuleView.vue': 'common/ModuleView.vue',
    'NotFound.vue': 'common/NotFound.vue',
    'PlaceholderView.vue': 'common/PlaceholderView.vue',
    'TestAuth.vue': 'auth/TestAuth.vue',
    'TestView.vue': 'test/TestView.vue',
    'UnderConstruction.vue': 'common/UnderConstruction.vue',
}

def move_files():
    """Move files to their respective module folders and update router references."""
    # Create target directories if they don't exist
    for target in file_mapping.values():
        target_path = target_dir / target
        target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Move files
    for src_file, target_file in file_mapping.items():
        src_path = src_dir / src_file
        target_path = target_dir / target_file
        
        if src_path.exists():
            # If target exists, show diff
            if target_path.exists():
                print(f"File {src_file} already exists at {target_path}")
                # You might want to add a diff here
            else:
                print(f"Moving {src_file} to {target_path}")
                shutil.move(str(src_path), str(target_path))
    
    # Check for empty directories
    for root, dirs, files in os.walk(src_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):
                    print(f"Removing empty directory: {dir_path}")
                    os.rmdir(dir_path)
            except Exception as e:
                print(f"Error removing directory {dir_path}: {e}")

def update_router_references():
    """Update router references to point to the new locations."""
    router_file = Path('frontend/src/router/index.ts')
    if not router_file.exists():
        print("Router file not found")
        return
    
    # Read the router file
    with open(router_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update import paths
    for src_file, target_file in file_mapping.items():
        old_path = f'@/views/{src_file.replace(".vue", "")}'
        new_path = f'@/views/{target_file.replace(".vue", "")}'
        
        if old_path in content:
            print(f"Updating import from {old_path} to {new_path}")
            content = content.replace(old_path, new_path)
    
    # Write the updated content back to the file
    with open(router_file, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    print("Starting view organization...")
    move_files()
    update_router_references()
    print("View organization complete!")
