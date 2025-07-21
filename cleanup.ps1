# Paksa Financial System - Cleanup and Reorganization Script
# This script will:
# 1. Clean Python cache files
# 2. Remove test and build artifacts
# 3. Clean Node.js and Vite caches
# 4. Remove temporary and backup files
# 5. Organize frontend structure
# 6. Organize backend structure
# 7. Remove empty directories

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to write colored output
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

# Function to remove Python cache files and test artifacts
function Remove-PythonCache {
    Write-Status "Cleaning Python cache files and test artifacts..."
    
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
                if ($pattern -match "^\w" -and -not ($pattern -match "\*")) {
                    # It's a directory pattern
                    Get-ChildItem -Path $path -Directory -Recurse -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
                        try {
                            Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction Stop
                            $totalRemoved++
                            Write-Status "Removed directory: $($_.FullName)" -Status "SUCCESS"
                        } catch {
                            Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
                        }
                    }
                } else {
                    # It's a file pattern
                    Get-ChildItem -Path $path -Include $pattern -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
                        try {
                            Remove-Item -Path $_.FullName -Force -ErrorAction Stop
                            $totalRemoved++
                            Write-Status "Removed file: $($_.FullName)" -Status "SUCCESS"
                        } catch {
                            Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
                        }
                    }
                }
            }
        }
    }
    
    Write-Status "Removed $totalRemoved Python cache files/directories" -Status "SUCCESS"
}

# Function to clean Node.js and frontend build artifacts
function Remove-NodeArtifacts {
    Write-Status "Cleaning Node.js and frontend build artifacts..."
    
    $frontendPath = "d:\Paksa Financial System\frontend"
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
        "*.log"
    )
    
    $totalRemoved = 0
    
    if (Test-Path $frontendPath) {
        # Remove package-lock.json and yarn.lock
        $lockFiles = @("package-lock.json", "yarn.lock")
        foreach ($lockFile in $lockFiles) {
            $lockFilePath = Join-Path $frontendPath $lockFile
            if (Test-Path $lockFilePath) {
                try {
                    Remove-Item -Path $lockFilePath -Force -ErrorAction Stop
                    $totalRemoved++
                    Write-Status "Removed lock file: $lockFilePath" -Status "SUCCESS"
                } catch {
                    Write-Status "Failed to remove $lockFilePath : $_" -Status "WARNING"
                }
            }
        }
        
        # Remove other patterns
        foreach ($pattern in $patterns) {
            if ($pattern -match "^\w" -and -not ($pattern -match "\*")) {
                # It's a directory pattern
                Get-ChildItem -Path $frontendPath -Directory -Recurse -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
                    try {
                        Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction Stop
                        $totalRemoved++
                        Write-Status "Removed directory: $($_.FullName)" -Status "SUCCESS"
                    } catch {
                        Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
                    }
                }
            } else {
                # It's a file pattern
                Get-ChildItem -Path $frontendPath -Include $pattern -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
                    try {
                        Remove-Item -Path $_.FullName -Force -ErrorAction Stop
                        $totalRemoved++
                        Write-Status "Removed file: $($_.FullName)" -Status "SUCCESS"
                    } catch {
                        Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
                    }
                }
            }
        }
    }
    
    Write-Status "Removed $totalRemoved Node.js/frontend artifacts" -Status "SUCCESS"
}

# Function to remove temporary and backup files
function Remove-TemporaryFiles {
    Write-Status "Removing temporary and backup files..."
    
    $tempFiles = Get-ChildItem -Path "d:\Paksa Financial System" -Recurse -File -Include @("*.tmp", "*.bak", "*.swp", "~*") -ErrorAction SilentlyContinue
    $totalRemoved = 0
    
    foreach ($file in $tempFiles) {
        try {
            Remove-Item -Path $file.FullName -Force -ErrorAction Stop
            $totalRemoved++
            Write-Status "Removed temporary file: $($file.FullName)" -Status "SUCCESS"
        } catch {
            Write-Status "Failed to remove $($file.FullName): $_" -Status "WARNING"
        }
    }
    
    Write-Status "Removed $totalRemoved temporary/backup files" -Status "SUCCESS"
}

# Function to organize frontend structure
function Optimize-FrontendStructure {
    Write-Status "Organizing frontend structure..."
    
    $frontendPath = "d:\Paksa Financial System\frontend\src"
    
    if (-not (Test-Path $frontendPath)) {
        Write-Status "Frontend directory not found at $frontendPath" -Status "WARNING"
        return
    }
    
    # 1. Check for duplicate stores directory
    $storesPath = Join-Path $frontendPath "stores"
    $storePath = Join-Path $frontendPath "store"
    
    if ((Test-Path $storesPath) -and (Test-Path $storePath)) {
        Write-Status "Found both 'stores' and 'store' directories. Merging into 'store'..."
        
        # Move all files from stores to store
        Get-ChildItem -Path $storesPath -File -ErrorAction SilentlyContinue | ForEach-Object {
            $destination = Join-Path $storePath $_.Name
            if (-not (Test-Path $destination)) {
                try {
                    Move-Item -Path $_.FullName -Destination $destination -Force -ErrorAction Stop
                    Write-Status "Moved: $($_.Name)" -Status "SUCCESS"
                } catch {
                    Write-Status "Failed to move $($_.Name): $_" -Status "WARNING"
                }
            } else {
                Write-Status "Skipped (already exists): $($_.Name)" -Status "WARNING"
            }
        }
        
        # Remove the now empty stores directory
        try {
            Remove-Item -Path $storesPath -Force -Recurse -ErrorAction Stop
            Write-Status "Removed empty directory: $storesPath" -Status "SUCCESS"
        } catch {
            Write-Status "Failed to remove $storesPath : $_" -Status "WARNING"
        }
    }
    
    # 2. Clean up any empty directories
    Get-ChildItem -Path $frontendPath -Directory -Recurse -ErrorAction SilentlyContinue | 
        Where-Object { -not (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue) } | 
        Sort-Object -Property FullName -Descending | 
        ForEach-Object {
            try {
                Remove-Item -Path $_.FullName -Force -Recurse -ErrorAction Stop
                Write-Status "Removed empty directory: $($_.FullName)" -Status "SUCCESS"
            } catch {
                Write-Status "Failed to remove empty directory $($_.FullName): $_" -Status "WARNING"
            }
        }
    
    Write-Status "Frontend structure optimization complete" -Status "SUCCESS"
}

# Function to organize backend structure
function Optimize-BackendStructure {
    Write-Status "Organizing backend structure..."
    
    $backendPath = "d:\Paksa Financial System\backend"
    
    if (-not (Test-Path $backendPath)) {
        Write-Status "Backend directory not found at $backendPath" -Status "WARNING"
        return
    }
    
    # 1. Clean up migrations
    $migrationsPath = Join-Path $backendPath "migrations"
    if (Test-Path $migrationsPath) {
        Get-ChildItem -Path $migrationsPath -File -Filter "*.py" -Recurse | 
            Where-Object { $_.Name -ne "__init__.py" } | 
            ForEach-Object {
                try {
                    Remove-Item -Path $_.FullName -Force -ErrorAction Stop
                    Write-Status "Removed migration file: $($_.FullName)" -Status "SUCCESS"
                } catch {
                    Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
                }
            }
    }
    
    # 2. Clean up cache and test artifacts
    $patterns = @(
        "__pycache__",
        "*.pyc",
        "*.pyo", 
        "*.pyd",
        "*.py,cover",
        ".coverage",
        ".pytest_cache",
        ".mypy_cache"
    )
    
    foreach ($pattern in $patterns) {
        if ($pattern -match "^\w" -and -not ($pattern -match "\*")) {
            # It's a directory pattern
            Get-ChildItem -Path $backendPath -Directory -Recurse -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
                try {
                    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction Stop
                    Write-Status "Removed directory: $($_.FullName)" -Status "SUCCESS"
                } catch {
                    Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
                }
            }
        } else {
            # It's a file pattern
            Get-ChildItem -Path $backendPath -Include $pattern -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
                try {
                    Remove-Item -Path $_.FullName -Force -ErrorAction Stop
                    Write-Status "Removed file: $($_.FullName)" -Status "SUCCESS"
                } catch {
                    Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
                }
            }
        }
    }
    
    # 3. Clean up any empty directories
    Get-ChildItem -Path $backendPath -Directory -Recurse -ErrorAction SilentlyContinue | 
        Where-Object { -not (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue) } | 
        Sort-Object -Property FullName -Descending | 
        ForEach-Object {
            try {
                Remove-Item -Path $_.FullName -Force -Recurse -ErrorAction Stop
                Write-Status "Removed empty directory: $($_.FullName)" -Status "SUCCESS"
            } catch {
                Write-Status "Failed to remove empty directory $($_.FullName): $_" -Status "WARNING"
            }
        }
    
    Write-Status "Backend structure optimization complete" -Status "SUCCESS"
}

# Function to remove empty directories
function Remove-EmptyDirectories {
    Write-Status "Removing empty directories..."
    
    $basePath = "d:\Paksa Financial System"
    $emptyDirs = @()
    
    # First pass: find all empty directories
    Get-ChildItem -Path $basePath -Directory -Recurse -ErrorAction SilentlyContinue | 
        Where-Object { -not (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue) } | 
        Sort-Object -Property FullName -Descending | 
        ForEach-Object { $emptyDirs += $_.FullName }
    
    # Second pass: remove empty directories
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

# Main script execution
Write-Status "Starting Paksa Financial System cleanup..." "INFO"

try {
    # Clean Python cache and test artifacts
    Remove-PythonCache
    
    # Clean Node.js and frontend artifacts
    Remove-NodeArtifacts
    
    # Remove temporary and backup files
    Remove-TemporaryFiles
    
    # Organize frontend structure
    Optimize-FrontendStructure
    
    # Organize backend structure
    Optimize-BackendStructure
    
    # Remove empty directories
    Remove-EmptyDirectories
    
    Write-Status "Cleanup completed successfully!" -Status "SUCCESS"
} catch {
    Write-Status "Error during cleanup: $_" -Status "ERROR"
    exit 1
}
