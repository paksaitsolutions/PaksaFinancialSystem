"""
Test runner script for all financial modules.
Run this script to execute comprehensive tests for all modules.
"""
import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all module tests and generate coverage report"""
    
    # Test files to run
    test_files = [
        "tests/test_gl_module_enhanced.py",
        "tests/test_ap_module.py", 
        "tests/test_ar_module.py",
        "tests/test_cash_module.py",
        "tests/test_budget_module.py",
        "tests/test_payroll_module.py",
        "tests/test_tax_module.py",
        "tests/test_fixed_assets_module.py"
    ]
    
    print("🧪 Running Paksa Financial System Module Tests")
    print("=" * 50)
    
    # Run tests with coverage
    cmd = [
        "python", "-m", "pytest",
        "--verbose",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=60"
    ] + test_files
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ All tests passed!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Some tests failed!")
        print(e.stdout)
        print(e.stderr)
        return False

def run_individual_module(module_name):
    """Run tests for a specific module"""
    
    module_map = {
        "gl": "tests/test_gl_module_enhanced.py",
        "ap": "tests/test_ap_module.py",
        "ar": "tests/test_ar_module.py", 
        "cash": "tests/test_cash_module.py",
        "budget": "tests/test_budget_module.py",
        "payroll": "tests/test_payroll_module.py",
        "tax": "tests/test_tax_module.py",
        "fixed-assets": "tests/test_fixed_assets_module.py"
    }
    
    if module_name not in module_map:
        print(f"❌ Unknown module: {module_name}")
        print(f"Available modules: {', '.join(module_map.keys())}")
        return False
    
    test_file = module_map[module_name]
    print(f"🧪 Running {module_name.upper()} module tests")
    print("=" * 30)
    
    cmd = [
        "python", "-m", "pytest",
        "--verbose",
        "--tb=short",
        test_file
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ {module_name.upper()} tests passed!")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {module_name.upper()} tests failed!")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific module
        module = sys.argv[1].lower()
        success = run_individual_module(module)
    else:
        # Run all tests
        success = run_tests()
    
    sys.exit(0 if success else 1)