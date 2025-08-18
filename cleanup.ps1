# Paksa Financial System - Cleanup and Reorganization Script
# This script will:
# 1. Clean Python cache files
# 2. Organize frontend structure
# 3. Organize backend structure
# 4. Remove empty directories

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
        default    { "Cyan" }
    }
    
    Write-Host "[$timestamp] [$Status] $Message" -ForegroundColor $color
}

# Function to remove Python cache files
function Remove-PythonCache {
    Write-Status "Cleaning Python cache files..."
    
    $paths = @(
        "d:\Paksa Financial System\backend"
        # Add other paths if needed
    )
    
    $totalRemoved = 0
    
    foreach ($path in $paths) {
        if (Test-Path $path) {
            # Remove __pycache__ directories
            $cacheDirs = Get-ChildItem -Path $path -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue
            $cacheDirs | ForEach-Object {
                try {
                    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction Stop
                    $totalRemoved++
                    Write-Status "Removed: $($_.FullName)" -Status "SUCCESS"
                } catch {
                    Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
                }
            }
            
            # Remove .pyc, .pyo, .pyd files
            $cacheFiles = Get-ChildItem -Path $path -Include @("*.pyc", "*.pyo", "*.pyd") -Recurse -File -ErrorAction SilentlyContinue
            $cacheFiles | ForEach-Object {
                try {
                    Remove-Item -Path $_.FullName -Force -ErrorAction Stop
                    $totalRemoved++
                    Write-Status "Removed: $($_.FullName)" -Status "SUCCESS"
                } catch {
                    Write-Status "Failed to remove $($_.FullName): $_" -Status "WARNING"
                }
            }
        }
    }
    
    Write-Status "Removed $totalRemoved Python cache files/directories" -Status "SUCCESS"
}

# Function to organize frontend structure
function Optimize-FrontendStructure {
    Write-Status "Organizing frontend structure..."
    
    $frontendPath = "d:\Paksa Financial System\frontend\src"
    
    # 1. Consolidate stores directory
    $storesPath = Join-Path $frontendPath "stores"
    $storePath = Join-Path $frontendPath "store"
    
    if (Test-Path $storesPath) {
        Write-Status "Found duplicate 'stores' directory. Merging into 'store'..."
        
        # Create store directory if it doesn't exist
        if (-not (Test-Path $storePath)) {
            New-Item -ItemType Directory -Path $storePath | Out-Null
            Write-Status "Created directory: $storePath" -Status "SUCCESS"
        }
        
        # Move all files from stores to store
        Get-ChildItem -Path $storesPath -Recurse -File | ForEach-Object {
            $relativePath = $_.FullName.Substring($storesPath.Length)
            $targetPath = Join-Path $storePath $relativePath.TrimStart('\\')
            $targetDir = Split-Path -Parent $targetPath
            
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            
            # If file exists, check which one is newer
            if (Test-Path $targetPath) {
                $existingFile = Get-Item $targetPath
                if ($_.LastWriteTime -gt $existingFile.LastWriteTime) {
                    Move-Item -Path $_.FullName -Destination $targetPath -Force
                    Write-Status "Updated (newer): $relativePath" -Status "SUCCESS"
                } else {
                    Write-Status "Skipped (older or same): $relativePath" -Status "WARNING"
                }
            } else {
                Move-Item -Path $_.FullName -Destination $targetPath -Force
                Write-Status "Moved: $relativePath" -Status "SUCCESS"
            }
        }
        
        # Remove empty directories
        Remove-Item -Path $storesPath -Recurse -Force
        Write-Status "Removed empty directory: $storesPath" -Status "SUCCESS"
    }
    
    # 2. Consolidate duplicate service files
    $jsService = Join-Path $frontendPath "services\accounting\reconciliationService.js"
    $tsService = Join-Path $frontendPath "services\gl\reconciliationService.ts"
    
    if (Test-Path $jsService -and Test-Path $tsService) {
        Write-Status "Found both JS and TS versions of reconciliationService"
        
        # Keep the TypeScript version as it's the newer standard
        Remove-Item -Path $jsService -Force
        Write-Status "Removed JS version (keeping TypeScript): $jsService" -Status "SUCCESS"
        
        # Update any imports that might reference the old path
        $tsContent = Get-Content -Path $tsService -Raw
        $updatedContent = $tsContent -replace "from '.*accounting/reconciliationService'", "from '../services/gl/reconciliationService'"
        $updatedContent | Set-Content -Path $tsService -NoNewline
        Write-Status "Updated imports in TypeScript service file" -Status "SUCCESS"
    }
    
    Write-Status "Frontend structure organization complete" -Status "SUCCESS"
}

# Function to organize backend structure
function Optimize-BackendStructure {
    Write-Status "Organizing backend structure..."
    
    $backendPath = "d:\Paksa Financial System\backend"
    
    # 1. Consolidate API endpoints
    $apiV1Dirs = Get-ChildItem -Path $backendPath -Directory -Recurse | 
        Where-Object { $_.Name -eq "v1" -and $_.Parent.Name -eq "api" } |
        Select-Object -ExpandProperty FullName | Sort-Object
    
    if ($apiV1Dirs.Count -gt 1) {
        Write-Status "Found multiple api/v1 directories. Consolidating..." -Status "WARNING"
        
        # The first one will be our primary API directory
        $primaryApi = $apiV1Dirs[0]
        Write-Status "Primary API directory: $primaryApi" -Status "INFO"
        
        # Process other API directories
        for ($i = 1; $i -lt $apiV1Dirs.Count; $i++) {
            $currentApi = $apiV1Dirs[$i]
            Write-Status "Merging API directory: $currentApi" -Status "INFO"
            
            # Move all files to primary API directory
            Get-ChildItem -Path $currentApi -Recurse -File | ForEach-Object {
                $relativePath = $_.FullName.Substring($currentApi.Length)
                $targetPath = Join-Path $primaryApi $relativePath.TrimStart('\\')
                $targetDir = Split-Path -Parent $targetPath
                
                if (-not (Test-Path $targetDir)) {
                    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
                }
                
                # If file exists, check content and keep the newer version
                if (Test-Path $targetPath) {
                    $existingFile = Get-Item $targetPath
                    if ($_.LastWriteTime -gt $existingFile.LastWriteTime) {
                        Move-Item -Path $_.FullName -Destination $targetPath -Force
                        Write-Status "  Updated (newer): $relativePath" -Status "SUCCESS"
                    } else {
                        Write-Status "  Skipped (older or same): $relativePath" -Status "WARNING"
                    }
                } else {
                    Move-Item -Path $_.FullName -Destination $targetPath -Force
                    Write-Status "  Moved: $relativePath" -Status "SUCCESS"
                }
            }
            
            # Remove empty directories
            try {
                Remove-Item -Path $currentApi -Recurse -Force -ErrorAction Stop
                Write-Status "  Removed empty directory: $currentApi" -Status "SUCCESS"
            } catch {
                Write-Status "  Could not remove directory (may not be empty): $currentApi" -Status "WARNING"
            }
        }
    }
    
    Write-Status "Backend structure organization complete" -Status "SUCCESS"
}

# Function to remove empty directories
function Remove-EmptyDirectories {
    param(
        [string]$path
    )
    
    Write-Status "Removing empty directories in: $path" -Status "INFO"
    
    do {
        $dirs = Get-ChildItem -Path $path -Directory -Recurse | 
                Where-Object { 
                    $_.GetFiles('*', 'AllDirectories').Count -eq 0 -and 
                    $_.GetDirectories().Count -eq 0 
                } |
                Select-Object -ExpandProperty FullName |
                Sort-Object -Property Length -Descending
        
        $count = $dirs.Count
        if ($count -gt 0) {
            Write-Status "  Found $count empty directories to remove" -Status "INFO"
            $dirs | ForEach-Object {
                try {
                    Remove-Item -Path $_ -Force -ErrorAction Stop
                    Write-Status "  Removed empty directory: $_" -Status "SUCCESS"
                } catch {
                    Write-Status "  Failed to remove directory $_: $_" -Status "WARNING"
                }
            }
        } else {
            Write-Status "  No more empty directories to remove" -Status "SUCCESS"
        }
    } while ($count -gt 0)
}

# Main execution
Write-Status "Starting Paksa Financial System cleanup and reorganization" -Status "INFO"
Write-Status "==================================================" -Status "INFO"

# 1. Clean Python cache files
Remove-PythonCache

# 2. Organize frontend structure
Optimize-FrontendStructure

# 3. Organize backend structure
Optimize-BackendStructure

# 4. Remove empty directories from both frontend and backend
Remove-EmptyDirectories -path "d:\Paksa Financial System\frontend"
Remove-EmptyDirectories -path "d:\Paksa Financial System\backend"

Write-Status "==================================================" -Status "INFO"
Write-Status "Cleanup and reorganization completed successfully!" -Status "SUCCESS"
Write-Status "Please review the changes and test the application." -Status "INFO"
