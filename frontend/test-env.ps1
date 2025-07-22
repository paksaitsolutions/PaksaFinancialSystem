Write-Host "=== Environment Test ===" -ForegroundColor Green
Write-Host "Current Directory: $(Get-Location)"
Write-Host "Node Version: $(node --version)"
Write-Host "NPM Version: $(npm --version)"
Write-Host "Vite Version: $(npx vite --version)"

Write-Host "`n=== Running Vite with Debug ===" -ForegroundColor Green
$env:DEBUG = 'vite:*'
$env:NODE_OPTIONS = '--trace-warnings --unhandled-rejections=strict'

# Run Vite and capture output
$process = Start-Process -FilePath "node" -ArgumentList "node_modules/vite/bin/vite.js" -NoNewWindow -PassThru -RedirectStandardOutput "vite-output.log" -RedirectStandardError "vite-error.log"

Write-Host "Vite started with PID: $($process.Id)"
Write-Host "Waiting 5 seconds..."
Start-Sleep -Seconds 5

if (-not $process.HasExited) {
    Write-Host "Vite is still running. Stopping it now..." -ForegroundColor Yellow
    Stop-Process -Id $process.Id -Force
}

Write-Host "`n=== Vite Output ===" -ForegroundColor Green
Get-Content "vite-output.log" -ErrorAction SilentlyContinue

Write-Host "`n=== Vite Errors ===" -ForegroundColor Red
Get-Content "vite-error.log" -ErrorAction SilentlyContinue

Write-Host "`nTest complete. Check the log files for details." -ForegroundColor Green
