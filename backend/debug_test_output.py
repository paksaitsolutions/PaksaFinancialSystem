"""
Script to capture complete test output and identify any errors.
"""
import subprocess
import sys

def run_tests():
    """Run tests and capture complete output."""
    cmd = [
        sys.executable,
        "-m", "pytest",
        "tests/",
        "-v",
        "--log-cli-level=INFO",
        "--tb=long"
    ]
    
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        # Run with text mode and capture output
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Print complete output
        print("\n=== STDOUT ===")
        print(result.stdout)
        print("\n=== STDERR ===")
        print(result.stderr)
        
    except subprocess.CalledProcessError as e:
        print(f"\nCommand failed with exit code {e.returncode}")
        print("\n=== STDOUT ===")
        print(e.stdout)
        print("\n=== STDERR ===")
        print(e.stderr)

if __name__ == "__main__":
    run_tests()
