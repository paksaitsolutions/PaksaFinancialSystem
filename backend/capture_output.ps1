$ErrorActionPreference = "Stop"

# Create a timestamp for the output file
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "import_output_${timestamp}.txt"

# Define the Python command to run
$pythonCmd = @"
import sys
import os
import traceback

try:
    print("=" * 80)
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    print("\nPython path:")
    for path in sys.path:
        print(f"  {path}")
    
    print("\n" + "=" * 80)
    print("Attempting to import from app.modules.core.database...")
    
    try:
        from app.modules.core import database
        print("[SUCCESS] Successfully imported database module!")
        print(f"Module location: {database.__file__}")
    except ImportError as e:
        print(f"[ERROR] ImportError: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("Test completed")
    
except Exception as e:
    print(f"\n[CRITICAL] Unexpected error: {type(e).__name__}: {e}")
    print("\nTraceback:")
    traceback.print_exc()
"@

# Write the Python script to a temporary file
$tempScript = [System.IO.Path]::GetTempFileName() + ".py"
$pythonCmd | Out-File -FilePath $tempScript -Encoding utf8 -Force

# Run the Python script and capture the output
try {
    Write-Host "Running Python script and capturing output to $outputFile..."
    
    # Use Start-Process to run Python with the script and capture all output
    $process = Start-Process -FilePath "python" -ArgumentList $tempScript -NoNewWindow -PassThru -Wait -RedirectStandardOutput $outputFile -RedirectStandardError "${outputFile}.err"
    
    # Display the output
    Write-Host "`nOutput from Python script:"
    Write-Host ("-" * 80)
    Get-Content $outputFile | ForEach-Object { Write-Host $_ }
    
    # Check for any errors
    if (Test-Path "${outputFile}.err" -And (Get-Item "${outputFile}.err").Length -gt 0) {
        Write-Host "`nErrors from Python script:"
        Write-Host ("-" * 80)
        Get-Content "${outputFile}.err" | ForEach-Object { Write-Host $_ }
    }
    
    Write-Host "`nScript execution completed. Output saved to $outputFile"
    if (Test-Path "${outputFile}.err") {
        Write-Host "Error output saved to ${outputFile}.err"
    }
} 
catch {
    Write-Host "Error running Python script: $_" -ForegroundColor Red
}
finally {
    # Clean up the temporary script file
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
