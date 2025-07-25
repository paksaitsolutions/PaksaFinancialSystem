#!/usr/bin/env python3
"""
Security Testing Suite Runner
Runs comprehensive security tests and generates reports
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime

class SecurityTestRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {},
            "recommendations": []
        }
    
    def run_penetration_tests(self):
        """Run penetration testing suite"""
        print("🔍 Running Penetration Tests...")
        
        cmd = [
            "python", "-m", "pytest", 
            "tests/security/test_penetration.py",
            "-v", "--tb=short", "--json-report", "--json-report-file=penetration_results.json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.results["tests"]["penetration"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        if result.returncode == 0:
            print("✅ Penetration tests PASSED")
        else:
            print("❌ Penetration tests FAILED")
            print(result.stdout)
    
    def run_performance_tests(self):
        """Run database performance tests"""
        print("⚡ Running Performance Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/performance/test_database_optimization.py",
            "-v", "--tb=short"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.results["tests"]["performance"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        if result.returncode == 0:
            print("✅ Performance tests PASSED")
        else:
            print("❌ Performance tests FAILED")
            print(result.stdout)
    
    def run_security_review_tests(self):
        """Run security review tests"""
        print("🔒 Running Security Review Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/security/test_security_review.py",
            "-v", "--tb=short"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.results["tests"]["security_review"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        if result.returncode == 0:
            print("✅ Security review tests PASSED")
        else:
            print("❌ Security review tests FAILED")
            print(result.stdout)
    
    def run_integration_tests(self):
        """Run security integration tests"""
        print("🔗 Running Integration Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/integration/test_security_integration.py",
            "-v", "--tb=short"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.results["tests"]["integration"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        if result.returncode == 0:
            print("✅ Integration tests PASSED")
        else:
            print("❌ Integration tests FAILED")
            print(result.stdout)
    
    def run_static_security_analysis(self):
        """Run static security analysis"""
        print("🔍 Running Static Security Analysis...")
        
        # Run bandit security scanner
        cmd = ["bandit", "-r", "app/", "-f", "json", "-o", "bandit_results.json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.results["tests"]["static_analysis"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        # Run safety check for dependencies
        cmd = ["safety", "check", "--json"]
        safety_result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.results["tests"]["dependency_check"] = {
            "exit_code": safety_result.returncode,
            "stdout": safety_result.stdout,
            "stderr": safety_result.stderr,
            "passed": safety_result.returncode == 0
        }
        
        if result.returncode == 0 and safety_result.returncode == 0:
            print("✅ Static analysis PASSED")
        else:
            print("❌ Static analysis found issues")
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for test in self.results["tests"].values() if test["passed"])
        
        self.results["summary"] = {
            "total_test_suites": total_tests,
            "passed_test_suites": passed_tests,
            "failed_test_suites": total_tests - passed_tests,
            "overall_status": "PASSED" if passed_tests == total_tests else "FAILED"
        }
        
        # Generate recommendations
        if not self.results["tests"].get("penetration", {}).get("passed", False):
            self.results["recommendations"].append(
                "CRITICAL: Fix penetration test failures before production"
            )
        
        if not self.results["tests"].get("performance", {}).get("passed", False):
            self.results["recommendations"].append(
                "HIGH: Address performance issues for production readiness"
            )
        
        if not self.results["tests"].get("static_analysis", {}).get("passed", False):
            self.results["recommendations"].append(
                "MEDIUM: Review static analysis findings"
            )
    
    def save_report(self):
        """Save test report"""
        report_file = f"security_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Report saved to: {report_file}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🔒 SECURITY TEST SUMMARY")
        print("="*60)
        
        summary = self.results["summary"]
        print(f"Total Test Suites: {summary['total_test_suites']}")
        print(f"Passed: {summary['passed_test_suites']}")
        print(f"Failed: {summary['failed_test_suites']}")
        print(f"Overall Status: {summary['overall_status']}")
        
        if self.results["recommendations"]:
            print("\n📋 RECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                print(f"  • {rec}")
        
        print("\n" + "="*60)
        
        if summary["overall_status"] == "PASSED":
            print("✅ ALL SECURITY TESTS PASSED - READY FOR PRODUCTION")
        else:
            print("❌ SECURITY TESTS FAILED - DO NOT DEPLOY")
        
        print("="*60)

def main():
    """Main test runner"""
    print("🚀 Starting Comprehensive Security Testing Suite")
    print("="*60)
    
    runner = SecurityTestRunner()
    
    try:
        # Run all test suites
        runner.run_penetration_tests()
        runner.run_performance_tests()
        runner.run_security_review_tests()
        runner.run_integration_tests()
        runner.run_static_security_analysis()
        
        # Generate summary and report
        runner.generate_summary()
        runner.save_report()
        runner.print_summary()
        
        # Exit with appropriate code
        if runner.results["summary"]["overall_status"] == "PASSED":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()