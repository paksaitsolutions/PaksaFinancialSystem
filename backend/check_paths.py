"""
Script to check Python paths and module structure
"""
import os
import sys

def print_paths():
    print("\n=== Python Path ===")
    for i, path in enumerate(sys.path):
        print(f"{i+1}. {path}")
    
    print("\n=== Current Directory Structure ===")
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith('.py'):
                print(f"{subindent}{f}")

if __name__ == "__main__":
    print("Current working directory:", os.getcwd())
    print_paths()
    
    # Test if we can find the app module
    try:
        import app
        print("\n✓ Successfully imported app module")
        print(f"App module location: {app.__file__}")
    except ImportError as e:
        print(f"\n✗ Could not import app module: {e}")
    
    # Test if we can find main.py
    main_path = os.path.join(os.getcwd(), 'main.py')
    print(f"\nMain.py exists: {os.path.exists(main_path)}")
    if os.path.exists(main_path):
        print(f"Main.py path: {main_path}")
