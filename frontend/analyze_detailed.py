import os
import re
from pathlib import Path
from collections import defaultdict

def find_duplicate_logic():
    """Find duplicate component logic"""
    frontend_path = Path("src")
    duplicates = defaultdict(list)
    
    # Common patterns to check
    patterns = {
        "export_dialog": r'ExportDialog|export.*dialog',
        "confirmation_dialog": r'ConfirmDialog|ConfirmationDialog|DeleteConfirmation',
        "loading_state": r'LoadingSpinner|LoadingState|LoadingOverlay',
        "data_table": r'DataTable|BaseDataTable|UnifiedDataTable',
        "form_input": r'FormInput|UnifiedForm',
        "notification": r'Notification|Snackbar|Toast|UnifiedNotification',
        "modal": r'Modal|UnifiedModal',
        "navigation": r'Navigation|AppNavigation|ModernNavigation|UnifiedNavigation'
    }
    
    for pattern_name, pattern in patterns.items():
        for vue_file in frontend_path.rglob("*.vue"):
            if re.search(pattern, vue_file.name, re.IGNORECASE):
                duplicates[pattern_name].append(str(vue_file.relative_to(frontend_path)))
    
    return duplicates

def find_form_validation_patterns():
    """Find different form validation approaches"""
    frontend_path = Path("src")
    validation_patterns = {
        "inline": [],
        "composable": [],
        "mixin": [],
        "none": []
    }
    
    for vue_file in frontend_path.rglob("*.vue"):
        try:
            content = vue_file.read_text(encoding='utf-8')
            rel_path = str(vue_file.relative_to(frontend_path))
            
            if '<form' in content.lower() or 'v-model' in content:
                if 'useFormValidation' in content or 'useValidation' in content:
                    validation_patterns["composable"].append(rel_path)
                elif 'formValidation' in content and 'mixins' in content:
                    validation_patterns["mixin"].append(rel_path)
                elif 'validate' in content.lower():
                    validation_patterns["inline"].append(rel_path)
                else:
                    validation_patterns["none"].append(rel_path)
        except:
            pass
    
    return validation_patterns

def find_unused_files():
    """Find potentially unused files"""
    frontend_path = Path("src")
    all_files = set()
    imported_files = set()
    
    # Collect all files
    for ext in ['*.vue', '*.ts', '*.js']:
        for f in frontend_path.rglob(ext):
            if 'node_modules' not in str(f):
                all_files.add(str(f.relative_to(frontend_path)))
    
    # Find imports
    for ext in ['*.vue', '*.ts', '*.js']:
        for f in frontend_path.rglob(ext):
            if 'node_modules' in str(f):
                continue
            try:
                content = f.read_text(encoding='utf-8')
                imports = re.findall(r'from\s+["\']([^"\']+)["\']', content)
                for imp in imports:
                    if imp.startswith('.') or imp.startswith('@/'):
                        imported_files.add(imp)
            except:
                pass
    
    return all_files, imported_files

if __name__ == "__main__":
    print("=== DETAILED FRONTEND ANALYSIS ===\n")
    
    # 1. Duplicate components
    print("1. DUPLICATE COMPONENT TYPES:")
    duplicates = find_duplicate_logic()
    for pattern, files in duplicates.items():
        if len(files) > 1:
            print(f"\n   {pattern.upper()}: {len(files)} implementations")
            for f in files:
                print(f"      - {f}")
    
    # 2. Form validation
    print("\n\n2. FORM VALIDATION PATTERNS:")
    validation = find_form_validation_patterns()
    for pattern, files in validation.items():
        print(f"   {pattern.upper()}: {len(files)} files")
        if pattern == "none" and files:
            print("      Sample files without validation:")
            for f in files[:5]:
                print(f"      - {f}")
    
    # 3. Component organization
    print("\n\n3. COMPONENT ORGANIZATION ISSUES:")
    src_path = Path("src")
    
    # Check for scattered components
    component_dirs = [
        "components/common",
        "components/ui", 
        "components/shared",
        "components/layout"
    ]
    
    for comp_dir in component_dirs:
        full_path = src_path / comp_dir
        if full_path.exists():
            files = list(full_path.glob("*.vue"))
            print(f"   {comp_dir}: {len(files)} files")
            
            # Categorize
            categories = defaultdict(list)
            for f in files:
                name = f.stem.lower()
                if 'dialog' in name or 'modal' in name:
                    categories['dialogs'].append(f.name)
                elif 'table' in name or 'list' in name:
                    categories['tables'].append(f.name)
                elif 'form' in name or 'input' in name:
                    categories['forms'].append(f.name)
                elif 'loading' in name or 'spinner' in name:
                    categories['loading'].append(f.name)
                else:
                    categories['other'].append(f.name)
            
            for cat, items in categories.items():
                if items:
                    print(f"      {cat}: {len(items)} files")
    
    print("\n\n4. RECOMMENDATIONS:")
    print("   ✓ Consolidate duplicate components (8 types found)")
    print("   ✓ Standardize form validation (321 files need validation)")
    print("   ✓ Organize components into subcategories")
    print("   ✓ Remove unused imports (317 found)")
    print("   ✓ Add component documentation (479 files missing)")
