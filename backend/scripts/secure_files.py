"""
Secure sensitive files and directories with proper permissions.

This script ensures that sensitive files like .env, configuration files,
and keys have restricted permissions to prevent unauthorized access.
"""
import os
import stat
from pathlib import Path
from typing import List, Set, Tuple

# Sensitive file extensions
SENSITIVE_EXTENSIONS = {
    '.key', '.pem', '.crt', '.cert', '.p12', '.pfx',  # Certificates and keys
    '.env', '.ini', '.cfg', '.conf', '.yaml', '.yml',  # Config files
    '.json', '.xml', '.properties', '.secret',
}

# Sensitive file names (case-insensitive)
SENSITIVE_NAMES = {
    '.env', 'config', 'secrets', 'credentials', 'passwords',
    'settings', 'config.py', 'settings.py', 'secrets.py',
    'docker-compose.yml', 'docker-compose.yaml', 'docker-compose.override.yml',
    'kubeconfig', '.kube', '.aws', '.ssh', '.docker', '.npmrc',
    '.pypirc', '.git-credentials', '.netrc', '.pgpass', '.s3cfg',
    'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519',
}

# Directories that should have restricted access
RESTRICTED_DIRS = {
    'instance', 'migrations', 'logs', 'data', 'secrets',
    'certs', 'keys', 'config', 'credentials',
}

# Default secure file permissions (octal)
SECURE_FILE_PERMS = 0o640  # rw-r-----
SECURE_DIR_PERMS = 0o750   # rwxr-x---

# Maximum permissions (octal)
MAX_FILE_PERMS = 0o644  # rw-r--r--
MAX_DIR_PERMS = 0o755   # rwxr-xr-x

def is_sensitive_file(filepath: Path) -> bool:
    """Check if a file is considered sensitive based on name and extension."""
    # Check extension
    if filepath.suffix.lower() in SENSITIVE_EXTENSIONS:
        return True
    
    # Check filename (case-insensitive)
    if filepath.name.lower() in SENSITIVE_NAMES:
        return True
    
    # Check if in sensitive directory
    for part in filepath.parts:
        if part.lower() in SENSITIVE_NAMES or part.lower() in RESTRICTED_DIRS:
            return True
    
    return False

def secure_file(filepath: Path) -> Tuple[bool, str]:
    """Apply secure permissions to a file."""
    try:
        if not filepath.exists():
            return False, f"File not found: {filepath}"
        
        current_mode = filepath.stat().st_mode
        
        # For sensitive files, restrict permissions
        if is_sensitive_file(filepath):
            # Remove group and other write permissions
            new_mode = current_mode & ~0o077
            # Set secure permissions
            new_mode = (new_mode & ~0o777) | SECURE_FILE_PERMS
            filepath.chmod(new_mode)
            return True, f"Secured: {filepath} (mode: {oct(new_mode & 0o777)})"
        
        # For non-sensitive files, ensure they're not too permissive
        if current_mode & 0o077:  # If group/other have any permissions
            new_mode = current_mode & ~0o077  # Remove group/other permissions
            filepath.chmod(new_mode)
            return True, f"Restricted: {filepath} (mode: {oct(new_mode & 0o777)})"
            
        return False, f"No change needed: {filepath}"
    except Exception as e:
        return False, f"Error securing {filepath}: {str(e)}"

def secure_directory(dirpath: Path) -> Tuple[bool, List[str]]:
    """Recursively secure a directory and its contents."""
    results = []
    changed = False
    
    try:
        if not dirpath.exists():
            return False, [f"Directory not found: {dirpath}"]
        
        # Skip virtual environments and git directories
        if any(part.startswith(('.', '__')) and part not in ('.git',) for part in dirpath.parts):
            return False, [f"Skipping hidden directory: {dirpath}"]
        
        # Secure the directory itself
        current_mode = dirpath.stat().st_mode
        
        # For sensitive directories, restrict permissions
        if dirpath.name in RESTRICTED_DIRS or is_sensitive_file(dirpath):
            new_mode = (current_mode & ~0o777) | SECURE_DIR_PERMS
            dirpath.chmod(new_mode)
            results.append(f"Secured directory: {dirpath} (mode: {oct(new_mode & 0o777)})")
            changed = True
        # For non-sensitive directories, ensure they're not too permissive
        elif current_mode & 0o007:  # If 'other' has any permissions
            new_mode = current_mode & ~0o007  # Remove 'other' permissions
            dirpath.chmod(new_mode)
            results.append(f"Restricted directory: {dirpath} (mode: {oct(new_mode & 0o777)})")
            changed = True
        
        # Process directory contents
        for item in dirpath.iterdir():
            if item.is_file():
                file_changed, msg = secure_file(item)
                if file_changed:
                    changed = True
                results.append(msg)
            elif item.is_dir():
                dir_changed, dir_msgs = secure_directory(item)
                if dir_changed:
                    changed = True
                results.extend(dir_msgs)
        
        return changed, results
    except Exception as e:
        return False, [f"Error securing directory {dirpath}: {str(e)}"]

def main():
    """Main function to secure sensitive files and directories."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Secure sensitive files and directories.')
    parser.add_argument('--path', type=str, default='.',
                       help='Path to the directory to secure (default: current directory)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    
    args = parser.parse_args()
    root_path = Path(args.path).resolve()
    
    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}")
        return
    
    print(f"Securing files in: {root_path}")
    print("Note: This script will restrict permissions on sensitive files and directories.")
    
    if args.dry_run:
        print("\nDRY RUN - No changes will be made.\n")
    
    # Secure the root directory and its contents
    changed, results = secure_directory(root_path)
    
    # Print results
    for msg in results:
        print(msg)
    
    if args.dry_run:
        print("\nDry run complete. No changes were made.")
    else:
        print(f"\nDone. Secured {len([m for m in results if m.startswith(('Secured', 'Restricted'))])} items.")

if __name__ == "__main__":
    main()
