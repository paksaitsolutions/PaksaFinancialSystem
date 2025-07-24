"""
Debug script for running and diagnosing test issues.
This script captures all output to a file for analysis.
"""
import os
import sys
import pytest
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"test_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the test environment."""
    # Add project root to Python path
    project_root = str(Path(__file__).resolve().parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Set environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["PYTHONUNBUFFERED"] = "1"
    
    logger.info(f"Project root: {project_root}")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Working directory: {os.getcwd()}")

def run_tests():
    """Run tests with detailed output."""
    test_args = [
        "-v",
        "--tb=long",
        "--disable-warnings",
        "--rootdir=.",
        "tests"
    ]
    
    logger.info(f"Running tests with args: {' '.join(test_args)}")
    return pytest.main(test_args)

def main():
    """Main function to run the debug tests."""
    try:
        setup_environment()
        logger.info("Starting test execution...")
        result = run_tests()
        logger.info(f"Test execution completed with exit code: {result}")
        return result
    except Exception as e:
        logger.exception("Error running tests:")
        return 1
    finally:
        logger.info(f"Log file saved to: {log_file.absolute()}")

if __name__ == "__main__":
    sys.exit(main())
