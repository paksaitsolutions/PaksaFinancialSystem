# PowerShell script to remove the stores directory
$baseDir = Split-Path -Parent $PSScriptRoot
$storesDir = Join-Path $baseDir "src\stores"

Write-Host "=== Store Cleanup Tool ===" -ForegroundColor Cyan

# Check if directory exists
if (Test-Path $storesDir) {
    # List all files and directories that will be removed
    Write-Host "The following will be removed:" -ForegroundColor Yellow
    Get-ChildItem -Path $storesDir -Recurse -Force | Select-Object FullName | Format-Table -AutoSize
    
    # Ask for confirmation
    $confirmation = Read-Host "Do you want to continue? (Y/N)"
    
    if ($confirmation -eq 'Y' -or $confirmation -eq 'y') {
        try {
            # Create a backup
            $backupDir = Join-Path $baseDir "backups\stores-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
            Write-Host "Creating backup at $backupDir..." -ForegroundColor Yellow
            New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
            Copy-Item -Path "$storesDir\*" -Destination $backupDir -Recurse -Force
            
            # Remove the stores directory
            Write-Host "Removing $storesDir..." -ForegroundColor Yellow
            Remove-Item -Path $storesDir -Recurse -Force -ErrorAction Stop
            
            # Recreate an empty stores directory with a README
            New-Item -ItemType Directory -Path $storesDir | Out-Null
            Set-Content -Path (Join-Path $storesDir "README.md") -Value "# Stores Directory

This directory is intentionally left empty. All stores have been moved to their respective module directories under `src/modules/`."
            
            Write-Host "Cleanup completed successfully!" -ForegroundColor Green
            Write-Host "Backup created at: $backupDir" -ForegroundColor Cyan
        }
        catch {
            Write-Host "Error during cleanup: $_" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "Cleanup cancelled by user." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Stores directory not found at: $storesDir" -ForegroundColor Yellow
}
