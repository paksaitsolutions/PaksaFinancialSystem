import re
from pathlib import Path

def remove_unused_imports():
    """Remove obvious unused imports from TypeScript and Vue files"""
    frontend_path = Path("src")
    fixed_files = []
    
    for file_path in list(frontend_path.rglob("*.ts")) + list(frontend_path.rglob("*.vue")):
        if 'node_modules' in str(file_path):
            continue
            
        try:
            content = file_path.read_text(encoding='utf-8')
            original = content
            
            # Find all imports
            import_pattern = r"import\s+(?:{[^}]+}|[\w]+)\s+from\s+['\"]([^'\"]+)['\"];?\n"
            imports = list(re.finditer(import_pattern, content))
            
            lines_to_remove = []
            for match in imports:
                import_line = match.group(0)
                import_path = match.group(1)
                
                # Extract imported names
                if '{' in import_line:
                    names_match = re.search(r'{([^}]+)}', import_line)
                    if names_match:
                        names = [n.strip().split(' as ')[0].strip() for n in names_match.group(1).split(',')]
                else:
                    name_match = re.search(r'import\s+([\w]+)\s+from', import_line)
                    if name_match:
                        names = [name_match.group(1)]
                    else:
                        continue
                
                # Check if any name is used in the rest of the file
                rest_of_file = content[match.end():]
                used = any(re.search(rf'\b{re.escape(name)}\b', rest_of_file) for name in names)
                
                if not used:
                    lines_to_remove.append(import_line)
            
            # Remove unused imports
            for line in lines_to_remove:
                content = content.replace(line, '')
            
            # Clean up multiple blank lines
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            if content != original:
                file_path.write_text(content, encoding='utf-8')
                fixed_files.append(str(file_path.relative_to(frontend_path)))
                
        except Exception as e:
            pass
    
    return fixed_files

if __name__ == "__main__":
    print("Removing unused imports...")
    fixed = remove_unused_imports()
    print(f"\nFixed {len(fixed)} files:")
    for f in fixed[:20]:
        print(f"  - {f}")
    if len(fixed) > 20:
        print(f"  ... and {len(fixed) - 20} more")
