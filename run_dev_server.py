import subprocess
import sys
import os

def run_server():
    """Run the FastAPI development server."""
    # Set the working directory to the backend folder
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
    os.chdir(backend_dir)
    
    # Print the command being run
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]
    print(f"Starting FastAPI server with: {' '.join(cmd)}")
    print(f"Server will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Run the server
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        print("\nMake sure you have uvicorn installed. You can install it with:")
        print("pip install uvicorn")
        return False
    return True

if __name__ == "__main__":
    run_server()
