# Script to clean up old backup directories in the frontend
# This script will remove backup directories that are no longer needed

$backupDir = Join-Path -Path $PSScriptRoot -ChildPath "..\frontend\backups"
$oldStoresDir = Join-Path -Path $backupDir -ChildPath "old-stores"
$storesBackupDir = Join-Path -Path $backupDir -ChildPath "stores-backup-20250718-162423"

# Check if directories exist and remove them
if (Test-Path -Path $oldStoresDir) {
    Write-Host "Removing directory: $oldStoresDir"
    Remove-Item -Path $oldStoresDir -Recurse -Force
}

if (Test-Path -Path $storesBackupDir) {
    Write-Host "Removing directory: $storesBackupDir"
    Remove-Item -Path $storesBackupDir -Recurse -Force
}

# Check if the backups directory is now empty
$remainingItems = Get-ChildItem -Path $backupDir -Force
if ($remainingItems.Count -eq 0) {
    # If backups directory is empty, remove it as well
    Write-Host "Backups directory is empty, removing: $backupDir"
    Remove-Item -Path $backupDir -Recurse -Force
}

Write-Host "Cleanup completed successfully!" -ForegroundColor Green
