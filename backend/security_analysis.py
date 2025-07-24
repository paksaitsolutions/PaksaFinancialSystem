"""
Security Analysis Script for Paksa Financial System Backend

This script analyzes the backend structure for potential security vulnerabilities.
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

class SecurityAnalyzer:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir).absolute()
        self.vulnerabilities: List[Dict] = []
        self.secrets_patterns = [
            r'password\s*[=:]\s*["\'].*?["\']',
            r'api[_-]?key\s*[=:]\s*["\'].*?["\']',
            r'secret[_-]?key\s*[=:]\s*["\'].*?["\']',
            r'token\s*[=:]\s*["\'].*?["\']',
            r'secret\s*[=:]\s*["\'].*?["\']',
            r'pwd\s*[=:]\s*["\'].*?["\']',
            r'pass\s*[=:]\s*["\'].*?["\']',
            r'credential\s*[=:]\s*["\'].*?["\']',
            r'DATABASE_URL\s*[=:]\s*["\'].*?["\']',
            r'REDIS_URL\s*[=:]\s*["\'].*?["\']',
        ]
        
        self.dangerous_functions = [
            'eval', 'exec', 'pickle.loads', 'yaml.load',
            'subprocess.Popen', 'os.system', 'os.popen',
            'pickle.load', 'marshal.load', 'shelve.open'
        ]
        
        self.insecure_deserialization_patterns = [
            r'pickle\.loads?\(',
            r'marshal\.loads?\('
        ]
        
        self.sql_injection_patterns = [
            r'execute\([^)]*\+',
            r'execute\([^)]*%s',
            r'execute\([^)]*\%\('
        ]
        
        self.xss_patterns = [
            r'Flask\.render_template_string\(',
            r'Jinja2\.Template\('
        ]

    def add_vulnerability(self, file_path: str, line_num: int, vuln_type: str, description: str, severity: str):
        """Add a vulnerability to the results."""
        self.vulnerabilities.append({
            'file': str(file_path.relative_to(self.root)),
            'line': line_num,
            'type': vuln_type,
            'description': description,
            'severity': severity
        })

    def check_file_permissions(self):
        """Check for insecure file permissions."""
        sensitive_files = [
            '*.pem', '*.key', '*.crt', '*.cert',
            '*.p12', '*.pfx', '*.p7b', '*.p7c',
            '*.p7m', '*.p7s', '*.p8', '*.p10',
            '*.p12', '*.pfx', '*.p7b', '*.p7c',
            '.env', 'config.ini', 'settings.py',
            '*.config', '*.conf', '*.yaml', '*.yml',
            '*.json', '*.xml', '*.properties',
            '*.db', '*.sqlite', '*.sqlite3', '*.db3'
        ]
        
        for pattern in sensitive_files:
            for file in self.root.rglob(pattern):
                if file.is_file():
                    try:
                        mode = file.stat().st_mode
                        if mode & 0o777 > 0o600:  # More permissive than 600
                            self.add_vulnerability(
                                file, 0,
                                'Insecure File Permissions',
                                f'File has overly permissive permissions: {oct(mode)[-3:]}',
                                'High'
                            )
                    except Exception as e:
                        print(f"Error checking permissions for {file}: {e}")

    def check_for_secrets(self, file_path: Path):
        """Check for hardcoded secrets in a file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            for i, line in enumerate(content.split('\n'), 1):
                for pattern in self.secrets_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip common false positives
                        if any(term in line.lower() for term in ['example', 'your_', 'placeholder']):
                            continue
                        self.add_vulnerability(
                            file_path, i,
                            'Hardcoded Secret',
                            f'Potential hardcoded secret found: {line.strip()[:100]}',
                            'Critical'
                        )
        except Exception as e:
            print(f"Error scanning {file_path} for secrets: {e}")

    def check_dangerous_functions(self, file_path: Path):
        """Check for dangerous function calls."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            for i, line in enumerate(content.split('\n'), 1):
                for func in self.dangerous_functions:
                    if func in line and not line.strip().startswith('#'):
                        self.add_vulnerability(
                            file_path, i,
                            'Dangerous Function',
                            f'Use of potentially dangerous function: {func}',
                            'High'
                        )
                
                # Check for SQL injection patterns
                for pattern in self.sql_injection_patterns:
                    if re.search(pattern, line):
                        self.add_vulnerability(
                            file_path, i,
                            'Potential SQL Injection',
                            'Potential SQL injection vulnerability - string concatenation in SQL query',
                            'Critical'
                        )
                
                # Check for XSS patterns
                for pattern in self.xss_patterns:
                    if re.search(pattern, line):
                        self.add_vulnerability(
                            file_path, i,
                            'Potential XSS',
                            'Potential XSS vulnerability - unsanitized template rendering',
                            'High'
                        )
                
                # Check for insecure deserialization
                for pattern in self.insecure_deserialization_patterns:
                    if re.search(pattern, line):
                        self.add_vulnerability(
                            file_path, i,
                            'Insecure Deserialization',
                            'Potential insecure deserialization vulnerability',
                            'Critical'
                        )
        except Exception as e:
            print(f"Error scanning {file_path} for dangerous functions: {e}")

    def check_dependencies(self):
        """Check for vulnerable dependencies."""
        requirements_files = [
            self.root / 'requirements.txt',
            self.root / 'pyproject.toml',
            self.root / 'setup.py'
        ]
        
        for req_file in requirements_files:
            if req_file.exists():
                self.add_vulnerability(
                    req_file, 0,
                    'Dependency Check',
                    'Consider running a dependency checker like safety or dependabot',
                    'Medium'
                )

    def check_authentication(self):
        """Check for authentication and authorization issues."""
        auth_files = [
            'auth.py', 'security.py', 'middleware/auth.py',
            'app/core/security.py', 'app/api/deps.py'
        ]
        
        for auth_file in auth_files:
            file_path = self.root / auth_file
            if file_path.exists():
                self.check_auth_implementation(file_path)

    def check_auth_implementation(self, file_path: Path):
        """Check authentication implementation for common issues."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Check for weak password hashing
            if 'md5(' in content or 'sha1(' in content:
                self.add_vulnerability(
                    file_path, 0,
                    'Weak Hashing Algorithm',
                    'Avoid using MD5 or SHA1 for password hashing. Use bcrypt or Argon2 instead.',
                    'High'
                )
                
            # Check for JWT implementation issues
            if 'jwt.encode(' in content and 'algorithm=' not in content:
                self.add_vulnerability(
                    file_path, 0,
                    'Insecure JWT Configuration',
                    'JWT encoding without explicit algorithm specified',
                    'High'
                )
                
        except Exception as e:
            print(f"Error checking authentication in {file_path}: {e}")

    def scan_directory(self):
        """Scan the entire directory for vulnerabilities."""
        print(f"Scanning {self.root} for security vulnerabilities...\n")
        
        # Check file permissions
        print("Checking file permissions...")
        self.check_file_permissions()
        
        # Check for secrets in files
        print("Scanning for hardcoded secrets...")
        for ext in ['.py', '.env', '.yaml', '.yml', '.json', '.sh']:
            for file_path in self.root.rglob(f'*{ext}'):
                if file_path.is_file() and 'venv' not in str(file_path):
                    self.check_for_secrets(file_path)
        
        # Check for dangerous code patterns
        print("Scanning for dangerous code patterns...")
        for file_path in self.root.rglob('*.py'):
            if file_path.is_file() and 'venv' not in str(file_path):
                self.check_dangerous_functions(file_path)
        
        # Check dependencies
        print("Checking dependencies...")
        self.check_dependencies()
        
        # Check authentication
        print("Checking authentication implementation...")
        self.check_authentication()
        
        # Sort vulnerabilities by severity
        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        self.vulnerabilities.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        # Print summary
        print("\n" + "="*80)
        print(f"Security Scan Complete. Found {len(self.vulnerabilities)} potential issues.")
        
        # Group by severity
        by_severity = {}
        for vuln in self.vulnerabilities:
            by_severity.setdefault(vuln['severity'], []).append(vuln)
        
        # Print summary by severity
        for severity in ['Critical', 'High', 'Medium', 'Low']:
            count = len(by_severity.get(severity, []))
            print(f"{severity}: {count}")
        
        print("="*80 + "\n")
        
        # Save detailed report
        report_path = self.root / 'security_scan_report.json'
        with open(report_path, 'w') as f:
            json.dump(self.vulnerabilities, f, indent=2)
        
        print(f"Detailed report saved to: {report_path}")
        
        return self.vulnerabilities

def main():
    analyzer = SecurityAnalyzer('.')
    vulnerabilities = analyzer.scan_directory()
    
    # Print all vulnerabilities
    for i, vuln in enumerate(vulnerabilities, 1):
        print(f"\n{i}. [{vuln['severity']}] {vuln['type']}")
        print(f"   File: {vuln['file']}:{vuln['line']}")
        print(f"   Description: {vuln['description']}")
    
    print("\nScan complete.")

if __name__ == "__main__":
    main()
