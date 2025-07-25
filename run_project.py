#!/usr/bin/env python3
"""
Paksa Financial System - Project Runner
Starts both backend and frontend services
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

class ProjectRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.project_root = Path(__file__).parent
        
    def check_requirements(self):
        """Check if required dependencies are available"""
        print("🔍 Checking requirements...")
        
        # Check Python
        try:
            result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
            print(f"✅ Python: {result.stdout.strip()}")
        except:
            print("❌ Python not found")
            return False
            
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            print(f"✅ Node.js: {result.stdout.strip()}")
        except:
            print("❌ Node.js not found")
            return False
            
        return True
    
    def setup_backend(self):
        """Setup backend environment"""
        print("🔧 Setting up backend...")
        
        backend_dir = self.project_root / "backend"
        os.chdir(backend_dir)
        
        # Install Python dependencies
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Backend dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install backend dependencies")
            return False
            
        return True
    
    def setup_frontend(self):
        """Setup frontend environment"""
        print("🔧 Setting up frontend...")
        
        frontend_dir = self.project_root / "frontend"
        os.chdir(frontend_dir)
        
        # Install Node.js dependencies
        try:
            subprocess.run(["npm", "install"], check=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            return False
            
        return True
    
    def start_backend(self):
        """Start the backend server"""
        print("🚀 Starting backend server...")
        
        backend_dir = self.project_root / "backend"
        os.chdir(backend_dir)
        
        # Start FastAPI server
        self.backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
        
        print("✅ Backend server starting on http://localhost:8000")
        return True
    
    def start_frontend(self):
        """Start the frontend development server"""
        print("🚀 Starting frontend server...")
        
        frontend_dir = self.project_root / "frontend"
        os.chdir(frontend_dir)
        
        # Start Vue.js development server
        self.frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ])
        
        print("✅ Frontend server starting on http://localhost:3000")
        return True
    
    def cleanup(self):
        """Cleanup processes on exit"""
        print("\n🛑 Shutting down servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            print("✅ Backend server stopped")
            
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            print("✅ Frontend server stopped")
    
    def run(self):
        """Main run method"""
        print("🚀 PAKSA FINANCIAL SYSTEM - STARTING UP")
        print("=" * 50)
        
        try:
            # Check requirements
            if not self.check_requirements():
                print("❌ Requirements check failed")
                return False
            
            # Setup backend
            if not self.setup_backend():
                print("❌ Backend setup failed")
                return False
            
            # Setup frontend
            if not self.setup_frontend():
                print("❌ Frontend setup failed")
                return False
            
            # Start services
            self.start_backend()
            time.sleep(3)  # Give backend time to start
            
            self.start_frontend()
            
            print("\n" + "=" * 50)
            print("🎉 PAKSA FINANCIAL SYSTEM IS RUNNING!")
            print("=" * 50)
            print("📊 Backend API: http://localhost:8000")
            print("📊 API Docs: http://localhost:8000/api/docs")
            print("🖥️  Frontend: http://localhost:3000")
            print("=" * 50)
            print("Press Ctrl+C to stop the servers")
            
            # Wait for processes
            try:
                while True:
                    if self.backend_process.poll() is not None:
                        print("❌ Backend process died")
                        break
                    if self.frontend_process.poll() is not None:
                        print("❌ Frontend process died")
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Received shutdown signal")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            self.cleanup()
        
        return True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    runner = ProjectRunner()
    success = runner.run()
    
    if success:
        print("✅ Project stopped successfully")
    else:
        print("❌ Project failed to start")
        sys.exit(1)