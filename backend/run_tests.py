"""
Test runner script for the Paksa Financial System backend.
This script helps diagnose and run tests with proper import paths.
"""
import os
import sys
import pytest
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def run_tests():
    """Run tests with proper import paths and configuration."""
    print("\n" + "="*80)
    print("Paksa Financial System - Test Runner")
    print("="*80)
    
    # Set environment variable for test mode
    os.environ["ENVIRONMENT"] = "test"
    
    # Run pytest with custom arguments
    test_args = [
        "-v",  # Verbose output
        "--tb=long",  # Show full traceback
        "--disable-warnings",  # Disable warnings for cleaner output
        "--rootdir={}".format(project_root),
        "tests"  # Run all tests in the tests directory
    ]
    
    print("\nRunning tests with the following configuration:")
    print(f"- Python path: {sys.path}")
    print(f"- Working directory: {os.getcwd()}")
    print(f"- Test arguments: {' '.join(test_args)}")
    
    # Run the tests
    return pytest.main(test_args)

if __name__ == "__main__":
    sys.exit(run_tests())
