#!/usr/bin/env python3
"""Test backup and recovery procedures"""
import subprocess
import os
import time
import requests
from datetime import datetime

class BackupRecoveryTest:
    def __init__(self):
        self.backup_dir = "/backups"
        self.test_results = []
    
    def log_result(self, test_name, success, message=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {test_name}: {message}")
    
    def test_backup_creation(self):
        """Test backup script execution"""
        try:
            result = subprocess.run(
                ["./backup.sh"], 
                cwd="/workspaces/PaksaFinancialSystem/ops/backup",
                capture_output=True, 
                text=True, 
                timeout=300
            )
            
            if result.returncode == 0:
                # Check if backup files were created
                timestamp = datetime.now().strftime("%Y%m%d")
                db_backups = [f for f in os.listdir(self.backup_dir) 
                             if f.startswith(f"db_backup_{timestamp}")]
                
                if db_backups:
                    self.log_result("Backup Creation", True, f"Created {len(db_backups)} backup files")
                    return db_backups[0].replace("db_backup_", "").replace(".sql.gz", "")
                else:
                    self.log_result("Backup Creation", False, "No backup files found")
                    return None
            else:
                self.log_result("Backup Creation", False, f"Backup script failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.log_result("Backup Creation", False, "Backup script timed out")
            return None
        except Exception as e:
            self.log_result("Backup Creation", False, f"Exception: {str(e)}")
            return None
    
    def test_application_health(self):
        """Test application health before/after restore"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                self.log_result("Application Health", True, "Application is healthy")
                return True
            else:
                self.log_result("Application Health", False, f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Application Health", False, f"Health check exception: {str(e)}")
            return False
    
    def test_restore_procedure(self, backup_timestamp):
        """Test restore script execution"""
        if not backup_timestamp:
            self.log_result("Restore Procedure", False, "No backup timestamp provided")
            return False
        
        try:
            result = subprocess.run(
                ["./restore.sh", backup_timestamp],
                cwd="/workspaces/PaksaFinancialSystem/ops/backup",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.log_result("Restore Procedure", True, "Restore completed successfully")
                return True
            else:
                self.log_result("Restore Procedure", False, f"Restore failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_result("Restore Procedure", False, "Restore script timed out")
            return False
        except Exception as e:
            self.log_result("Restore Procedure", False, f"Exception: {str(e)}")
            return False
    
    def run_full_test(self):
        """Run complete backup and recovery test"""
        print("Starting Backup and Recovery Test Suite")
        print("=" * 50)
        
        # Test 1: Check initial application health
        initial_health = self.test_application_health()
        
        # Test 2: Create backup
        backup_timestamp = self.test_backup_creation()
        
        # Test 3: Test restore procedure (if backup was successful)
        if backup_timestamp and initial_health:
            # Wait a moment before restore
            time.sleep(5)
            restore_success = self.test_restore_procedure(backup_timestamp)
            
            # Test 4: Check application health after restore
            if restore_success:
                time.sleep(10)  # Wait for application to start
                self.test_application_health()
        
        # Print summary
        print("\n" + "=" * 50)
        print("Test Summary:")
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        print(f"Passed: {passed}/{total}")
        
        if passed == total:
            print("✅ All backup and recovery tests passed!")
            return True
        else:
            print("❌ Some tests failed. Check logs for details.")
            return False

if __name__ == "__main__":
    tester = BackupRecoveryTest()
    success = tester.run_full_test()
    exit(0 if success else 1)