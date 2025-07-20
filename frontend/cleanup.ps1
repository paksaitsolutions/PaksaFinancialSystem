Write-Host "Cleaning up project..." -ForegroundColor Green

# Remove node_modules
if (Test-Path "node_modules") {
    Write-Host "Removing node_modules..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force node_modules
}

# Remove package-lock.json
if (Test-Path "package-lock.json") {
    Write-Host "Removing package-lock.json..." -ForegroundColor Yellow
    Remove-Item -Force package-lock.json
}

# Remove Vite cache
if (Test-Path "node_modules\.vite") {
    Write-Host "Removing Vite cache..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "node_modules\.vite"
}

Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host "Please run 'npm install' to reinstall dependencies." -ForegroundColor Cyan
