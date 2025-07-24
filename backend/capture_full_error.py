import sys
import os
import traceback

def main():
    # Open file with UTF-8 encoding and buffering disabled (buffering=1 means line buffered)
    with open('full_error_output.txt', 'w', encoding='utf-8', buffering=1) as f:
        def log(message):
            print(message, file=f)
            f.flush()  # Ensure immediate write
            os.fsync(f.fileno())  # Force write to disk
        
        try:
            log("=" * 80)
            log("Starting full error capture...")
            log("=" * 80 + "\n")
            
            log(f"Python version: {sys.version}")
            log(f"Current working directory: {os.getcwd()}")
            
            log("\nPython path:")
            for path in sys.path:
                log(f"  {path}")
            
            log("\n" + "=" * 80)
            log("Attempting to import from app.modules.core.database...")
            log("=" * 80)
            
            try:
                from app.modules.core import database
                log("[SUCCESS] Successfully imported database module!")
                log(f"Module location: {database.__file__}")
            except ImportError as e:
                log(f"[ERROR] ImportError: {e}")
                log("\nFull traceback:")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
                for line in traceback_details:
                    log(line.rstrip())
            
            log("\n" + "=" * 80)
            log("Test completed")
            log("=" * 80)
            
        except Exception as e:
            log(f"\n[ERROR] Unexpected error in capture script: {type(e).__name__}: {e}")
            log("\nTraceback:")
            traceback.print_exc(file=f)

if __name__ == "__main__":
    main()
