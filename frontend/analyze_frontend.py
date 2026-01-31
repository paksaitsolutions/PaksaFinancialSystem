import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_frontend():
    frontend_path = Path("src")
    
    results = {
        "duplicate_components": [],
        "unused_imports": [],
        "missing_docs": [],
        "form_validation": [],
        "component_organization": []
    }
    
    # Track component names
    component_names = defaultdict(list)
    
    # Analyze Vue files
    for vue_file in frontend_path.rglob("*.vue"):
        try:
            content = vue_file.read_text(encoding='utf-8')
            rel_path = str(vue_file.relative_to(frontend_path))
            
            # Extract component name
            name_match = re.search(r'name:\s*["\']([^"\']+)["\']', content)
            if name_match:
                comp_name = name_match.group(1)
                component_names[comp_name].append(rel_path)
            
            # Check for form validation
            if 'form' in content.lower() and 'validate' not in content.lower():
                results["form_validation"].append(rel_path)
            
            # Check for component documentation
            if '<script' in content and '/**' not in content:
                results["missing_docs"].append(rel_path)
                
        except Exception as e:
            pass
    
    # Find duplicates
    for name, paths in component_names.items():
        if len(paths) > 1:
            results["duplicate_components"].append({
                "name": name,
                "paths": paths
            })
    
    # Analyze TypeScript files
    for ts_file in frontend_path.rglob("*.ts"):
        if 'node_modules' in str(ts_file):
            continue
        try:
            content = ts_file.read_text(encoding='utf-8')
            rel_path = str(ts_file.relative_to(frontend_path))
            
            # Find imports
            imports = re.findall(r'import\s+.*?from\s+["\']([^"\']+)["\']', content)
            
            # Check if imports are used
            for imp in imports:
                imp_name = imp.split('/')[-1].replace('.ts', '').replace('.js', '')
                if imp_name and imp_name not in content[content.find(imp)+len(imp):]:
                    results["unused_imports"].append({
                        "file": rel_path,
                        "import": imp
                    })
        except Exception as e:
            pass
    
    # Component organization analysis
    components_dir = frontend_path / "components"
    if components_dir.exists():
        subdirs = [d for d in components_dir.iterdir() if d.is_dir()]
        for subdir in subdirs:
            files = list(subdir.glob("*.vue"))
            if len(files) > 10:
                results["component_organization"].append({
                    "dir": str(subdir.relative_to(frontend_path)),
                    "count": len(files),
                    "suggestion": "Consider splitting into subcategories"
                })
    
    return results

if __name__ == "__main__":
    print("Analyzing frontend codebase...")
    results = analyze_frontend()
    
    print("\n=== FRONTEND REFACTORING ANALYSIS ===\n")
    
    print(f"1. DUPLICATE COMPONENTS: {len(results['duplicate_components'])}")
    for dup in results['duplicate_components'][:10]:
        print(f"   - {dup['name']}: {len(dup['paths'])} instances")
        for path in dup['paths']:
            print(f"     * {path}")
    
    print(f"\n2. MISSING DOCUMENTATION: {len(results['missing_docs'])}")
    for doc in results['missing_docs'][:10]:
        print(f"   - {doc}")
    
    print(f"\n3. FORM VALIDATION ISSUES: {len(results['form_validation'])}")
    for form in results['form_validation'][:10]:
        print(f"   - {form}")
    
    print(f"\n4. COMPONENT ORGANIZATION: {len(results['component_organization'])}")
    for org in results['component_organization']:
        print(f"   - {org['dir']}: {org['count']} files - {org['suggestion']}")
    
    print(f"\n5. UNUSED IMPORTS: {len(results['unused_imports'])}")
    for imp in results['unused_imports'][:10]:
        print(f"   - {imp['file']}: {imp['import']}")
