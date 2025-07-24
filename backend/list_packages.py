"""
List all installed Python packages in the current environment.
"""
import subprocess
import sys

def main():
    print("📦 Installed Python Packages:")
    print("=" * 50)
    
    try:
        # Use pip to list all installed packages
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Print the list of installed packages
        if result.stdout:
            print("\n".join(sorted(result.stdout.splitlines())))
        else:
            print("No packages found or error occurred.")
            
    except subprocess.CalledProcessError as e:
        print(f"Error listing packages: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
