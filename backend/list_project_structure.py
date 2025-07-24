"""
Script to list the project structure for debugging purposes.
"""
import os
from pathlib import Path

def list_directory(path, indent=0, max_depth=3, current_depth=0):
    """Recursively list directory contents with indentation."""
    if current_depth > max_depth:
        return
        
    prefix = '  ' * current_depth
    try:
        for item in os.scandir(path):
            if item.is_dir():
                print(f"{prefix}📁 {item.name}")
                list_directory(item.path, indent, max_depth, current_depth + 1)
            else:
                if item.name.endswith(('.py', '.env', '.txt', '.md', '.json')):
                    print(f"{prefix}📄 {item.name}")
    except PermissionError:
        print(f"{prefix}🔒 [Permission Denied] {path}")
    except Exception as e:
        print(f"{prefix}❌ [Error] {path}: {str(e)}")

def main():
    print("Project Structure:")
    print("================")
    current_dir = Path.cwd()
    print(f"📁 {current_dir.name}")
    list_directory(current_dir, max_depth=2)

if __name__ == "__main__":
    main()
