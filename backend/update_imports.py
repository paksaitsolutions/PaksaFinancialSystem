"""
Script to update imports from old to new module locations.

Features:
- Updates imports to new module structure
- Handles various import styles (single-line, multi-line, parenthesized)
- Supports relative and absolute imports
- Creates backups before modifying files
- Dry-run mode to preview changes
- Detailed logging
"""

import os
import re
import shutil
import logging
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('import_updater.log')
    ]
)
logger = logging.getLogger(__name__)

# Define import patterns to update
IMPORT_REPLACEMENTS = [
    # Database imports
    (r'from\s+app\.db\.base\b', 'from app.core.db.base'),
    (r'from\s+app\.db\.base_class\b', 'from app.core.db.base'),
    (r'from\s+app\.db\.init_db\b', 'from app.core.db.init_db'),
    (r'from\s+app\.db\.session\b', 'from app.core.db.session'),
    (r'from\s+app\.db\.utils\b', 'from app.core.db.utils'),
    
    # Core imports
    (r'from\s+app\.core\.database\b', 'from app.core.db.base'),
    (r'from\s+app\.core\.db\.base_class\b', 'from app.core.db.base'),
    
    # Model imports
    (r'from\s+app\.models\.base\b', 'from app.core.db.base'),
    (r'from\s+app\.models\.base_class\b', 'from app.core.db.base'),
    
    # Utils imports
    (r'from\s+app\.utils\.db\b', 'from app.core.db.utils'),
    
    # Relative imports (handled separately)
]

# Define directories to skip
SKIP_DIRS = {
    'venv', '.venv', '__pycache__', '.git', '.mypy_cache',
    'node_modules', 'dist', 'build', 'migrations', 'tests'
}

@dataclass
class ImportUpdateStats:
    """Track statistics about import updates."""
    files_processed: int = 0
    files_updated: int = 0
    imports_updated: int = 0
    errors: List[Tuple[Path, str]] = field(default_factory=list)

def create_backup(file_path: Path) -> Optional[Path]:
    """Create a backup of the file before making changes."""
    try:
        backup_path = file_path.with_suffix(f'{file_path.suffix}.bak')
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup for {file_path}: {e}")
        return None

def update_imports_in_file(file_path: Path, dry_run: bool = False) -> int:
    """
    Update imports in a single file.
    
    Args:
        file_path: Path to the file to update
        dry_run: If True, only show what would be changed
        
    Returns:
        Number of import statements updated
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = content = f.read()
        
        update_count = 0
        
        # Apply each replacement pattern
        for pattern, replacement in IMPORT_REPLACEMENTS:
            # Handle both simple and callable replacements
            if callable(replacement):
                def replacer(match):
                    result = replacement(match)
                    if result != match.group(0):
                        nonlocal update_count
                        update_count += 1
                    return result
                content, _ = re.subn(pattern, replacer, content, flags=re.MULTILINE)
            else:
                new_content, count = re.subn(
                    pattern, 
                    replacement, 
                    content, 
                    flags=re.MULTILINE
                )
                if count > 0:
                    content = new_content
                    update_count += count
        
        # Handle relative imports (e.g., from ..core.db.base -> from ..core.db.base)
        rel_pattern = r'(from\s+\.+\.?)(db\.)(\w+)'
        def update_relative_import(match):
            dots = match.group(1)
            module = match.group(3)
            return f"{dots}core.db.{module}"
            
        content, rel_count = re.subn(
            rel_pattern, 
            update_relative_import, 
            content,
            flags=re.MULTILINE
        )
        update_count += rel_count
        
        # Only write if changes were made and not in dry-run mode
        if content != original_content and not dry_run:
            # Create backup before modifying
            backup_path = create_backup(file_path)
            if backup_path:
                logger.debug(f"Created backup at {backup_path}")
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Updated {update_count} imports in {file_path}")
        elif content != original_content:
            logger.info(f"[DRY RUN] Would update {update_count} imports in {file_path}")
        
        return update_count if content != original_content else 0
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}", exc_info=True)
        return 0

def process_directory(
    root_dir: Path, 
    stats: ImportUpdateStats,
    dry_run: bool = False,
    verbose: bool = False
) -> None:
    """
    Recursively process all Python files in a directory.
    
    Args:
        root_dir: Directory to process
        stats: Statistics tracker
        dry_run: If True, only show what would be changed
        verbose: If True, show detailed progress
    """
    for item in root_dir.iterdir():
        # Skip hidden directories and files
        if item.name.startswith('.') or item.name in SKIP_DIRS:
            continue
            
        if item.is_dir():
            process_directory(item, stats, dry_run, verbose)
            continue
            
        if item.suffix == '.py':
            stats.files_processed += 1
            
            if verbose and stats.files_processed % 100 == 0:
                logger.info(f"Processed {stats.files_processed} files...")
            
            try:
                updated = update_imports_in_file(item, dry_run)
                if updated > 0:
                    stats.files_updated += 1
                    stats.imports_updated += updated
            except Exception as e:
                stats.errors.append((item, str(e)))
                logger.error(f"Failed to process {item}: {e}", exc_info=True)

def print_summary(stats: ImportUpdateStats) -> None:
    """Print a summary of the import updates."""
    logger.info("\n" + "=" * 50)
    logger.info("IMPORT UPDATE SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Files processed:  {stats.files_processed}")
    logger.info(f"Files updated:     {stats.files_updated}")
    logger.info(f"Total imports updated: {stats.imports_updated}")
    
    if stats.errors:
        logger.warning("\nErrors occurred while processing the following files:")
        for file_path, error in stats.errors:
            logger.warning(f"- {file_path}: {error}")
    
    logger.info("=" * 50 + "\n")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Update Python import statements.')
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be changed without making any changes'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress information'
    )
    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='Path to the directory to process (default: current directory)'
    )
    return parser.parse_args()

def main() -> None:
    """Main function to run the import updater."""
    args = parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    root_dir = Path(args.path).resolve()
    if not root_dir.exists():
        logger.error(f"Directory not found: {root_dir}")
        return
    
    logger.info(f"Starting import updates in: {root_dir}")
    if args.dry_run:
        logger.info("DRY RUN MODE: No files will be modified")
    
    stats = ImportUpdateStats()
    
    try:
        process_directory(root_dir, stats, args.dry_run, args.verbose)
        print_summary(stats)
        
        if not args.dry_run and stats.files_updated > 0:
            logger.info("Backup files with .bak extension have been created.")
        
        if stats.errors:
            logger.warning(f"Completed with {len(stats.errors)} errors. Check the log for details.")
        else:
            logger.info("Completed successfully!")
            
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0 if not stats.errors else 1

if __name__ == "__main__":
    exit(main())
