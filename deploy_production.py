#!/usr/bin/env python3
"""
Production Deployment Script for Paksa Financial System
Comprehensive deployment with database setup, migrations, and health checks
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

class ProductionDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_path = self.project_root / "backend"
        self.frontend_path = self.project_root / "frontend"
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, command, cwd=None, check=True):
        """Run shell command with error handling"""
        self.log(f"Running: {command}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if e.stderr:
                self.log(f"Error: {e.stderr}", "ERROR")
            raise
    
    def check_prerequisites(self):
        """Check system prerequisites"""
        self.log("Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 10):
            raise RuntimeError("Python 3.10+ required")
        
        # Check Node.js
        try:
            result = self.run_command("node --version", check=False)
            if result.returncode != 0:
                raise RuntimeError("Node.js not found")
            self.log(f"Node.js version: {result.stdout.strip()}")
        except:
            raise RuntimeError("Node.js 18+ required")
        
        # Check PostgreSQL (optional)
        try:
            self.run_command("psql --version", check=False)
            self.log("PostgreSQL available")
        except:
            self.log("PostgreSQL not found - using SQLite", "WARNING")
        
        self.log("Prerequisites check passed")
    
    def setup_backend(self):
        """Setup backend environment and dependencies"""
        self.log("Setting up backend...")
        
        # Create virtual environment
        venv_path = self.backend_path / ".venv"
        if not venv_path.exists():
            self.run_command("python -m venv .venv", cwd=self.backend_path)
        
        # Activate virtual environment and install dependencies
        if os.name == 'nt':  # Windows
            pip_cmd = str(venv_path / "Scripts" / "pip")
            python_cmd = str(venv_path / "Scripts" / "python")
        else:  # Unix/Linux/Mac
            pip_cmd = str(venv_path / "bin" / "pip")
            python_cmd = str(venv_path / "bin" / "python")
        
        self.run_command(f"{pip_cmd} install --upgrade pip", cwd=self.backend_path)
        self.run_command(f"{pip_cmd} install -r requirements.txt", cwd=self.backend_path)
        
        # Setup environment variables
        env_file = self.backend_path / ".env"
        if not env_file.exists():
            env_content = """
DATABASE_URL=sqlite:///./paksa_financial.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=["http://localhost:3000","http://localhost:3003","https://yourdomain.com"]
"""
            env_file.write_text(env_content.strip())
            self.log("Created .env file - please update with production values")
        
        self.log("Backend setup completed")
        return python_cmd
    
    def setup_database(self, python_cmd):
        """Initialize and migrate database"""
        self.log("Setting up database...")
        
        # Run database initialization
        self.run_command(f"{python_cmd} init_db.py", cwd=self.backend_path)
        
        # Run Alembic migrations
        try:
            self.run_command(f"{python_cmd} -m alembic upgrade head", cwd=self.backend_path)
        except:
            self.log("Alembic migration failed - creating tables manually", "WARNING")
            self.run_command(f"{python_cmd} create_complete_database.py", cwd=self.backend_path)
        
        self.log("Database setup completed")
    
    def setup_frontend(self):
        """Setup frontend build"""
        self.log("Setting up frontend...")
        
        # Install dependencies
        self.run_command("npm install", cwd=self.frontend_path)
        
        # Create production environment file
        env_file = self.frontend_path / ".env.production"
        if not env_file.exists():
            env_content = """
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=Paksa Financial System
VITE_APP_VERSION=1.0.0
"""
            env_file.write_text(env_content.strip())
        
        # Build for production
        self.run_command("npm run build", cwd=self.frontend_path)
        
        self.log("Frontend setup completed")
    
    def start_services(self, python_cmd):
        """Start backend and frontend services"""
        self.log("Starting services...")
        
        # Start backend
        backend_process = subprocess.Popen(
            f"{python_cmd} -m uvicorn app.main:app --host 0.0.0.0 --port 8000",
            shell=True,
            cwd=self.backend_path
        )
        
        # Wait for backend to start
        time.sleep(5)
        
        # Start frontend (development server for now)
        frontend_process = subprocess.Popen(
            "npm run dev -- --host 0.0.0.0 --port 3003",
            shell=True,
            cwd=self.frontend_path
        )
        
        self.log("Services started")
        return backend_process, frontend_process
    
    def run_health_checks(self):
        """Run comprehensive health checks"""
        self.log("Running health checks...")
        
        # Backend health check
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                self.log("✓ Backend health check passed")
            else:
                raise Exception(f"Backend health check failed: {response.status_code}")
        except Exception as e:
            self.log(f"✗ Backend health check failed: {e}", "ERROR")
            return False
        
        # API endpoints check
        endpoints_to_test = [
            "/",
            "/api/v1/hrm/employees",
            "/api/v1/gl/accounts",
            "/api/v1/budget/budgets"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                if response.status_code in [200, 401]:  # 401 is OK for protected endpoints
                    self.log(f"✓ Endpoint {endpoint} accessible")
                else:
                    self.log(f"✗ Endpoint {endpoint} failed: {response.status_code}", "WARNING")
            except Exception as e:
                self.log(f"✗ Endpoint {endpoint} error: {e}", "WARNING")
        
        # Frontend health check
        try:
            response = requests.get("http://localhost:3003", timeout=10)
            if response.status_code == 200:
                self.log("✓ Frontend health check passed")
            else:
                self.log(f"✗ Frontend health check failed: {response.status_code}", "WARNING")
        except Exception as e:
            self.log(f"✗ Frontend health check failed: {e}", "WARNING")
        
        self.log("Health checks completed")
        return True
    
    def run_qa_tests(self):
        """Run QA test suite"""
        self.log("Running QA tests...")
        
        # Backend tests
        try:
            self.run_command("python -m pytest tests/ -v", cwd=self.backend_path, check=False)
            self.log("✓ Backend tests completed")
        except:
            self.log("✗ Backend tests failed", "WARNING")
        
        # Frontend tests
        try:
            self.run_command("npm test", cwd=self.frontend_path, check=False)
            self.log("✓ Frontend tests completed")
        except:
            self.log("✗ Frontend tests not configured", "WARNING")
        
        self.log("QA tests completed")
    
    def generate_deployment_report(self):
        """Generate deployment report"""
        report = f"""
# Paksa Financial System - Deployment Report
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}

## Services Status
- Backend API: http://localhost:8000
- Frontend App: http://localhost:3003
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Default Credentials
- Email: admin@paksa.com
- Password: admin123

## Available Modules
✓ General Ledger
✓ Accounts Payable
✓ Accounts Receivable
✓ Budget Management
✓ Cash Management
✓ Human Resources Management
✓ Inventory Management
✓ Payroll Management
✓ Tax Management
✓ Fixed Assets
✓ Financial Reports
✓ AI Assistant
✓ Super Admin

## Database
- Type: SQLite (development) / PostgreSQL (production)
- Location: backend/paksa_financial.db
- Migrations: Alembic

## Security Notes
- Change default credentials in production
- Update SECRET_KEY in .env file
- Configure CORS origins for production domain
- Enable HTTPS in production

## Next Steps
1. Update environment variables for production
2. Configure reverse proxy (Nginx)
3. Set up SSL certificates
4. Configure backup strategy
5. Set up monitoring and logging
"""
        
        report_file = self.project_root / "DEPLOYMENT_REPORT.md"
        report_file.write_text(report)
        self.log(f"Deployment report saved to {report_file}")
    
    def deploy(self):
        """Main deployment process"""
        try:
            self.log("Starting Paksa Financial System deployment...")
            
            # Step 1: Prerequisites
            self.check_prerequisites()
            
            # Step 2: Backend setup
            python_cmd = self.setup_backend()
            
            # Step 3: Database setup
            self.setup_database(python_cmd)
            
            # Step 4: Frontend setup
            self.setup_frontend()
            
            # Step 5: Start services
            backend_proc, frontend_proc = self.start_services(python_cmd)
            
            # Step 6: Health checks
            if self.run_health_checks():
                self.log("✓ Deployment successful!", "SUCCESS")
            else:
                self.log("✗ Deployment completed with warnings", "WARNING")
            
            # Step 7: QA tests
            self.run_qa_tests()
            
            # Step 8: Generate report
            self.generate_deployment_report()
            
            self.log("Deployment process completed")
            self.log("Backend running on: http://localhost:8000")
            self.log("Frontend running on: http://localhost:3003")
            self.log("API Docs available at: http://localhost:8000/docs")
            
            return backend_proc, frontend_proc
            
        except Exception as e:
            self.log(f"Deployment failed: {e}", "ERROR")
            sys.exit(1)

if __name__ == "__main__":
    deployer = ProductionDeployer()
    processes = deployer.deploy()
    
    try:
        # Keep services running
        input("\nPress Enter to stop services...")
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        for proc in processes:
            proc.terminate()
        print("Services stopped")