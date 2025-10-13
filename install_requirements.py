#!/usr/bin/env python3
"""
Cross-platform requirements installer for Paksa Financial System
Automatically detects the platform and installs appropriate dependencies
"""

import os
import sys
import subprocess
import platform

def get_platform():
    """Detect the current platform"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system in ["linux", "darwin"]:
        return "linux"
    else:
        return "linux"  # Default to linux for unknown platforms

def install_requirements(requirements_file):
    """Install requirements from the specified file"""
    try:
        print(f"Installing requirements from {requirements_file}...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        print("Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def main():
    """Main installation function"""
    current_platform = get_platform()
    print(f"Detected platform: {current_platform}")
    
    # Determine which requirements file to use
    if current_platform == "windows":
        requirements_file = "requirements-windows.txt"
    else:
        requirements_file = "requirements-linux.txt"
    
    # Check if platform-specific file exists, fallback to main requirements.txt
    if not os.path.exists(requirements_file):
        print(f"{requirements_file} not found, using requirements.txt")
        requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print("No requirements file found!")
        sys.exit(1)
    
    # Install requirements
    success = install_requirements(requirements_file)
    
    if not success:
        print("Installation failed!")
        sys.exit(1)
    
    print("All dependencies installed successfully!")

if __name__ == "__main__":
    main()