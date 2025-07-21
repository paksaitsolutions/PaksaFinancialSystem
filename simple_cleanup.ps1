# Simple Cleanup Script for Paksa Financial System
# This script performs basic cleanup operations

# Set error action preference
$ErrorActionPreference = "Continue"

# Function to write status messages
function Write-Status {
    param(
        [string]$Message,
        [string]$Status = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Status) {
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR"   { "Red" }
        default   { "Cyan" }
    }
    
    Write-Host "[$timestamp] [$Status] $Message" -ForegroundColor $color
}

# Function to clean Python cache files
function Remove-PythonCache {
    Write-Status "Cleaning Python cache files..."
    
    $paths = @(
        "d:\Paksa Financial System\backend",
        "d:\Paksa Financial System\tests"
    )
    
    $patterns = @(
        "__pycache__",
        "*.pyc",
        "*.pyo", 
        "*.pyd",
        "*.py,cover",
        ".coverage",
        ".pytest_cache",
        ".mypy_cache",
        ".hypothesis",
        ".tox",
        ".eggs",
        "*.egg-info",
        "build",
        "dist"
    )
    
    $totalRemoved = 0
    
    foreach ($path in $paths) {
        if (Test-Path $path) {
            foreach ($pattern in $patterns) {
                Get-ChildItem -Path $path -Include $pattern -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
                    try {
                        Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction Stop
                        $totalRemoved++
                        Write-Status "Removed: $($_.FullName)" -Status "SUCCESS"
                    } catch {
                        Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
                    }
                }
            }
        }
    }
    
    Write-Status "Removed $totalRemoved Python cache files/directories" -Status "SUCCESS"
}

# Function to clean Node.js artifacts
function Remove-NodeArtifacts {
    Write-Status "Cleaning Node.js and frontend build artifacts..."
    
    $frontendPath = "d:\Paksa Financial System\frontend"
    if (-not (Test-Path $frontendPath)) {
        Write-Status "Frontend directory not found at $frontendPath" -Status "WARNING"
        return
    }
    
    $patterns = @(
        "node_modules",
        ".vite",
        "dist",
        ".nuxt",
        ".next",
        "out",
        "build",
        "coverage",
        ".cache",
        "*.log",
        "package-lock.json",
        "yarn.lock"
    )
    
    $totalRemoved = 0
    
    foreach ($pattern in $patterns) {
        Get-ChildItem -Path $frontendPath -Include $pattern -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
            try {
                Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction Stop
                $totalRemoved++
                Write-Status "Removed: $($_.FullName)" -Status "SUCCESS"
            } catch {
                Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
            }
        }
    }
    
    Write-Status "Removed $totalRemoved Node.js/frontend artifacts" -Status "SUCCESS"
}

# Function to remove temporary files
function Remove-TemporaryFiles {
    Write-Status "Removing temporary and backup files..."
    
    $patterns = @("*.tmp", "*.bak", "*.swp", "~*")
    $totalRemoved = 0
    
    foreach ($pattern in $patterns) {
        Get-ChildItem -Path "d:\Paksa Financial System" -Include $pattern -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
            try {
                Remove-Item -Path $_.FullName -Force -ErrorAction Stop
                $totalRemoved++
                Write-Status "Removed: $($_.FullName)" -Status "SUCCESS"
            } catch {
                Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
            }
        }
    }
    
    Write-Status "Removed $totalRemoved temporary/backup files" -Status "SUCCESS"
}

# Function to remove empty directories
function Remove-EmptyDirectories {
    Write-Status "Removing empty directories..."
    
    $basePath = "d:\Paksa Financial System"
    $emptyDirs = @()
    
    # Find all empty directories
    Get-ChildItem -Path $basePath -Directory -Recurse -Force -ErrorAction SilentlyContinue | 
        Where-Object { -not (Get-ChildItem -Path $_.FullName -Recurse -File -Force -ErrorAction SilentlyContinue) } | 
        Sort-Object -Property FullName -Descending | 
        ForEach-Object { $emptyDirs += $_.FullName }
    
    # Remove empty directories
    $removedCount = 0
    foreach ($dir in $emptyDirs) {
        try {
            if (Test-Path $dir) {
                Remove-Item -Path $dir -Force -Recurse -ErrorAction Stop
                $removedCount++
                Write-Status "Removed empty directory: $dir" -Status "SUCCESS"
            }
        } catch {
            Write-Status "Failed to remove empty directory $dir : $_" -Status "WARNING"
        }
    }
    
    Write-Status "Removed $removedCount empty directories" -Status "SUCCESS"
}

# Main execution
Write-Status "Starting cleanup process..." -Status "INFO"

# Run cleanup functions
Remove-PythonCache
Remove-NodeArtifacts
Remove-TemporaryFiles
Remove-EmptyDirectories

Write-Status "Cleanup completed!" -Status "SUCCESS"
