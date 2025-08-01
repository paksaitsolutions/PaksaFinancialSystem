import os
import shutil
import filecmp
from pathlib import Path
from typing import Dict, Set, Tuple

def get_module_mapping() -> Dict[str, Path]:
    """Create a mapping of module names to their view directories."""
    src_dir = Path(r'd:\Paksa Financial System\frontend\src')
    modules_dir = src_dir / 'modules'
    return {
        'accounting': modules_dir / 'accounting' / 'views',
        'ap': modules_dir / 'accounts-payable' / 'views',
        'ar': modules_dir / 'accounts-receivable' / 'views',
        'cash': modules_dir / 'cash-management' / 'views',
        'fixed-assets': modules_dir / 'fixed-assets' / 'views',
        'hrm': modules_dir / 'hrm' / 'views',
        'inventory': modules_dir / 'inventory' / 'views',
        'payroll': modules_dir / 'payroll' / 'views',
        'procurement': modules_dir / 'procurement' / 'views',
        'projects': modules_dir / 'projects' / 'views',
        'reports': modules_dir / 'reports' / 'views',
        'settings': modules_dir / 'settings' / 'views',
        'treasury': modules_dir / 'treasury' / 'views',
        'auth': modules_dir / 'auth' / 'views',
        'dashboard': modules_dir / 'dashboard' / 'views',
        'compliance': modules_dir / 'compliance' / 'views',
    }

def ensure_directories_exist(module_map: Dict[str, Path]) -> None:
    """Ensure all target view directories exist."""
    for path in module_map.values():
        path.mkdir(parents=True, exist_ok=True)

def is_file_different(file1: Path, file2: Path) -> bool:
    """Check if two files are different."""
    try:
        return not filecmp.cmp(file1, file2, shallow=False)
    except FileNotFoundError:
        return True

def move_views() -> None:
    """Move all views from src/views to their respective module folders."""
    src_dir = Path(r'd:\Paksa Financial System\frontend\src')
    views_dir = src_dir / 'views'
    backup_dir = src_dir / 'views_backup'
    
    # Create a backup of the views directory
    if not backup_dir.exists():
        shutil.copytree(views_dir, backup_dir)
        print(f"Backup created at: {backup_dir}")
    
    module_map = get_module_mapping()
    ensure_directories_exist(module_map)
    
    # Track moved files and conflicts
    moved_files = set()
    conflicts = []
    
    # First pass: Move all view files to their module folders
    for view_path in views_dir.rglob('*.vue'):
        # Skip files in the root of views directory that don't have a module folder
        if view_path.parent == views_dir:
            continue
            
        # Get the module name from the parent directory
        module_name = view_path.parent.name
        
        # Skip if the module doesn't exist in our map
        if module_name not in module_map:
            print(f"Warning: No module mapping found for {view_path}")
            continue
            
        # Get the target directory
        target_dir = module_map[module_name]
        target_path = target_dir / view_path.name
        
        # If the file already exists in the target, check if it's different
        if target_path.exists() and is_file_different(view_path, target_path):
            conflicts.append((view_path, target_path))
            continue
            
        # Move the file
        print(f"Moving {view_path.relative_to(views_dir)} to {target_path.relative_to(src_dir)}")
        shutil.move(str(view_path), str(target_path))
        moved_files.add(view_path.relative_to(views_dir))
    
    # Handle conflicts
    if conflicts:
        print("\nFound the following conflicts (files with the same name but different content):")
        for i, (source, target) in enumerate(conflicts, 1):
            print(f"\n{i}. Conflict: {source.relative_to(views_dir)}")
            print(f"   Source size: {source.stat().st_size} bytes")
            print(f"   Target size: {target.stat().st_size} bytes")
            
            # Show a preview of the differences
            with open(source, 'r', encoding='utf-8') as f1, open(target, 'r', encoding='utf-8') as f2:
                src_lines = f1.readlines()
                tgt_lines = f2.readlines()
                
                diff = set(src_lines) - set(tgt_lines)
                print("\nDifferences (simplified):")
                for line in list(diff)[:5]:
                    print(f"  - {line.strip()}")
                if len(diff) > 5:
                    print(f"  - ... and {len(diff) - 5} more differences")
            
            action = input("\nKeep (s)ource, keep (t)arget, or (v)iew full diff? [s/t/v] ").lower()
            
            if action == 'v':
                # Show full diff
                os.system(f'fc "{source}" "{target}"')
                action = input("\nKeep (s)ource or keep (t)arget? [s/t] ").lower()
            
            if action == 's':
                print(f"Keeping source version, replacing target: {target_path}")
                shutil.move(str(source), str(target_path))
                moved_files.add(source.relative_to(views_dir))
            else:
                print(f"Keeping target version, removing source: {source}")
                os.remove(source)
    
    # Clean up empty directories
    for dirpath, dirnames, filenames in os.walk(views_dir, topdown=False):
        if dirpath != str(views_dir):  # Don't remove the root views directory yet
            try:
                if not os.listdir(dirpath):  # Check if directory is empty
                    print(f"Removing empty directory: {dirpath}")
                    os.rmdir(dirpath)
            except Exception as e:
                print(f"Error removing directory {dirpath}: {e}")
    
    # Remove the views directory if it's empty
    try:
        if not os.listdir(views_dir):
            print(f"\nRemoving empty views directory: {views_dir}")
            os.rmdir(views_dir)
        else:
            print(f"\nViews directory not empty, keeping: {views_dir}")
            print("Remaining files/directories:")
            for item in os.listdir(views_dir):
                print(f"  - {item}")
    except Exception as e:
        print(f"Error removing views directory: {e}")
    
    # Print summary
    print("\n" + "="*50)
    print("View Organization Summary:")
    print(f"- Moved {len(moved_files)} files to module view folders")
    print(f"- Resolved {len(conflicts)} file conflicts")
    print(f"- Backup available at: {backup_dir}")
    print("="*50)

def update_router_references():
    """Update router references to point to new view locations."""
    router_file = Path(r'd:\Paksa Financial System\frontend\src\router\index.ts')
    if not router_file.exists():
        print("Router file not found. Skipping router reference updates.")
        return
    
    # Read the router file
    with open(router_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update import paths
    updated_content = content
    module_map = get_module_mapping()
    
    for module_name, module_path in module_map.items():
        old_import = f'@/views/{module_name}/'
        new_import = f'@/modules/{module_path.parent.name}/views/'
        updated_content = updated_content.replace(old_import, new_import)
    
    # Write the updated content back to the file
    if updated_content != content:
        with open(router_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("\nUpdated router import paths.")
    else:
        print("\nNo router import paths needed updating.")

if __name__ == "__main__":
    print("Starting view organization...")
    move_views()
    update_router_references()
    print("\nView organization complete!")
