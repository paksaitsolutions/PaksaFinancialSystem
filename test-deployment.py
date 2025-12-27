#!/usr/bin/env python3
"""
Test script to verify deployment readiness
"""
import os
import sys
import subprocess

def check_file_exists(path, description):
    """Check if a file exists"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_directory_contents(path, description):
    """Check directory contents"""
    if os.path.exists(path):
        files = os.listdir(path)
        print(f"✅ {description}: {len(files)} files")
        for file in files[:5]:  # Show first 5 files
            print(f"   - {file}")
        if len(files) > 5:
            print(f"   ... and {len(files) - 5} more files")
        return True
    else:
        print(f"❌ {description}: Directory not found")
        return False

def main():
    print("🔍 Paksa Financial System - Deployment Check")
    print("=" * 50)
    
    # Check critical files
    critical_files = [
        ("backend/app/main.py", "Main application file"),
        ("backend/requirements.txt", "Python dependencies"),
        ("render-build.sh", "Build script"),
        ("backend/static/index.html", "Frontend fallback")
    ]
    
    all_critical_exist = True
    for file_path, description in critical_files:
        if not check_file_exists(file_path, description):
            all_critical_exist = False
    
    print("\n📁 Directory Structure:")
    check_directory_contents("backend", "Backend directory")
    check_directory_contents("backend/static", "Static files directory")
    check_directory_contents("frontend", "Frontend directory")
    
    print("\n🐍 Python Environment:")
    try:
        import uvicorn
        print("✅ Uvicorn available")
    except ImportError:
        print("❌ Uvicorn not available")
    
    try:
        import fastapi
        print("✅ FastAPI available")
    except ImportError:
        print("❌ FastAPI not available")
    
    print("\n📋 Summary:")
    if all_critical_exist:
        print("✅ All critical files present")
        print("✅ Ready for deployment")
    else:
        print("❌ Missing critical files")
        print("❌ Not ready for deployment")
    
    print("\n🚀 To deploy:")
    print("1. Commit changes to git")
    print("2. Push to Render.com")
    print("3. Build script will handle the rest")

if __name__ == "__main__":
    main()