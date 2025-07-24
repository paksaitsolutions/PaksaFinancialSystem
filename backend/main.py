"""
Paksa Financial System - Main Application Entry Point
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This is the main entry point for the Paksa Financial System application.
It runs the FastAPI application using uvicorn.
"""

import os
import sys
from typing import Dict

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# This allows running the app with: python main.py
if __name__ == "__main__":
    import uvicorn
    # Use the string module path to avoid circular imports
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
