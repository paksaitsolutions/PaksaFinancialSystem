#!/usr/bin/env python3
"""
Install required dependencies for report generation
"""
import subprocess
import sys

def install_packages():
    packages = [
        'reportlab',
        'pandas',
        'openpyxl'
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")

if __name__ == "__main__":
    install_packages()
    print("\nReport dependencies installation completed!")