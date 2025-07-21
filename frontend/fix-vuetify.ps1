<#
.SYNOPSIS
    Resets Vite cache and fixes Vuetify dependency issues
.DESCRIPTION
    This script will:
    1. Stop any running Node.js processes
    2. Clear Vite cache and build artifacts
    3. Clean npm cache
    4. Reinstall dependencies
    5. Update Vite and Vuetify to latest versions
    6. Start the development server
#>

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to write colored output
function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

try {
    # Stop any running Node.js processes
    Write-Info "Stopping any running Node.js processes..."
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

    # Remove Vite cache and build artifacts
    $cacheDirs = @(
        "node_modules\.vite",
        "dist",
        ".vite",
        ".sass-cache"
    )

    foreach ($dir in $cacheDirs) {
        if (Test-Path $dir) {
            Write-Info "Removing $dir..."
            Remove-Item -Recurse -Force $dir
        }
    }

    # Clean npm cache
    Write-Info "Cleaning npm cache..."
    npm cache clean --force

    # Remove lock files and node_modules
    $filesToRemove = @(
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock"
    )

    foreach ($file in $filesToRemove) {
        if (Test-Path $file) {
            Write-Info "Removing $file..."
            Remove-Item -Force $file
        }
    }

    # Remove node_modules if it exists
    if (Test-Path "node_modules") {
        Write-Info "Removing node_modules..."
        Remove-Item -Recurse -Force node_modules
    }

    # Install dependencies
    Write-Info "Installing dependencies..."
    npm install

    # Update Vite and Vuetify to latest versions
    Write-Info "Updating Vite and Vuetify..."
    npm install --save-dev vite@latest @vitejs/plugin-vue@latest
    npm install vuetify@latest @mdi/font@latest sass sass-loader@latest

    # Check Vite and Vuetify versions
    Write-Info "Checking installed versions..."
    npm list vite @vitejs/plugin-vue vuetify @mdi/font

    Write-Success "✅ Reset and update completed successfully!"
    Write-Host "\nNext steps:"
    Write-Host "1. Start the development server: npm run dev" -ForegroundColor Green
    Write-Host "2. If issues persist, check the browser console for errors" -ForegroundColor Yellow
    Write-Host "3. Ensure your Vuetify components are properly imported in your main.js/ts file" -ForegroundColor Cyan

} catch {
    Write-Host "❌ An error occurred: $_" -ForegroundColor Red
    exit 1
}
