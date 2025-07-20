# Force cleanup script for node_modules
Write-Host "=== Force Cleanup Script ===" -ForegroundColor Cyan

# Function to find and kill processes using files in a directory
function Stop-ProcessesUsingPath {
    param (
        [string]$path
    )
    
    Write-Host "Finding processes using files in: $path" -ForegroundColor Yellow
    
    try {
        $processes = Get-Process | Where-Object { 
            $_.Modules | Where-Object { $_.FileName -like "$path*" } 
        }
        
        if ($processes) {
            Write-Host "Found processes using files in the directory:" -ForegroundColor Yellow
            $processes | Format-Table Id, ProcessName, Path -AutoSize
            
            $confirmation = Read-Host "Do you want to stop these processes? (Y/N)"
            if ($confirmation -eq 'Y' -or $confirmation -eq 'y') {
                $processes | Stop-Process -Force
                Write-Host "Processes stopped." -ForegroundColor Green
            } else {
                Write-Host "Process cleanup skipped." -ForegroundColor Yellow
            }
        } else {
            Write-Host "No processes found using files in the directory." -ForegroundColor Green
        }
    } catch {
        Write-Host "Error finding processes: $_" -ForegroundColor Red
    }
}

# Main cleanup process
$nodeModulesPath = Join-Path $PSScriptRoot "node_modules"

# Check if node_modules exists
if (Test-Path $nodeModulesPath) {
    Write-Host "Found node_modules directory at: $nodeModulesPath" -ForegroundColor Yellow
    
    # Try to stop processes using the directory
    Stop-ProcessesUsingPath -path $nodeModulesPath
    
    # Try to remove the directory
    try {
        Write-Host "Attempting to remove node_modules directory..." -ForegroundColor Yellow
        Remove-Item -Path $nodeModulesPath -Recurse -Force -ErrorAction Stop
        Write-Host "Successfully removed node_modules directory." -ForegroundColor Green
    } catch {
        Write-Host "Failed to remove node_modules: $_" -ForegroundColor Red
        Write-Host "You may need to close any applications using these files and try again." -ForegroundColor Yellow
        Write-Host "Alternatively, you can try restarting your computer to release file locks." -ForegroundColor Yellow
    }
} else {
    Write-Host "node_modules directory not found at: $nodeModulesPath" -ForegroundColor Green
}

# Check for package-lock.json and remove it
$packageLockPath = Join-Path $PSScriptRoot "package-lock.json"
if (Test-Path $packageLockPath) {
    try {
        Remove-Item -Path $packageLockPath -Force -ErrorAction Stop
        Write-Host "Removed package-lock.json" -ForegroundColor Green
    } catch {
        Write-Host "Failed to remove package-lock.json: $_" -ForegroundColor Red
    }
} else {
    Write-Host "package-lock.json not found." -ForegroundColor Green
}

Write-Host "=== Cleanup Complete ===" -ForegroundColor Cyan
Write-Host "You can now try running 'npm install' to reinstall dependencies." -ForegroundColor Cyan
