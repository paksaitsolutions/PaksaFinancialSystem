import re
from pathlib import Path

def add_component_docs():
    """Add basic JSDoc documentation to Vue components"""
    frontend_path = Path("src/components")
    fixed_files = []
    
    for vue_file in frontend_path.rglob("*.vue"):
        try:
            content = vue_file.read_text(encoding='utf-8')
            
            # Skip if already has documentation
            if '/**' in content or '@component' in content:
                continue
            
            # Find script tag
            script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            if not script_match:
                continue
            
            script_content = script_match.group(1)
            
            # Check if it's a component (has defineComponent or export default)
            if 'defineComponent' not in script_content and 'export default' not in script_content:
                continue
            
            # Extract component name from file name
            comp_name = vue_file.stem
            
            # Create documentation
            doc = f"""/**
 * {comp_name} Component
 * 
 * @component
 */
"""
            
            # Find where to insert (after imports, before defineComponent or export)
            insert_pos = None
            
            # Try to find last import
            imports = list(re.finditer(r'^import\s+.*?;?\s*$', script_content, re.MULTILINE))
            if imports:
                last_import = imports[-1]
                insert_pos = last_import.end()
            else:
                # Insert at start of script
                insert_pos = 0
            
            # Insert documentation
            new_script = script_content[:insert_pos] + '\n\n' + doc + script_content[insert_pos:]
            new_content = content.replace(script_content, new_script)
            
            vue_file.write_text(new_content, encoding='utf-8')
            fixed_files.append(str(vue_file.relative_to(Path("src"))))
            
        except Exception as e:
            pass
    
    return fixed_files

if __name__ == "__main__":
    print("Adding component documentation...")
    fixed = add_component_docs()
    print(f"\nAdded docs to {len(fixed)} files:")
    for f in fixed[:20]:
        print(f"  - {f}")
    if len(fixed) > 20:
        print(f"  ... and {len(fixed) - 20} more")
