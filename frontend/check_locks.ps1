# Script to check for processes locking files in node_modules
Write-Host "=== Checking for processes locking files in node_modules ===" -ForegroundColor Cyan

$nodeModulesPath = Join-Path $PSScriptRoot "node_modules"

if (Test-Path $nodeModulesPath) {
    Write-Host "Found node_modules directory at: $nodeModulesPath" -ForegroundColor Yellow
    
    # Using handle.exe (from Sysinternals) to find file locks
    $handlePath = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Microsoft.Sysinternals.ProcessExplorer_Microsoft.Winget.Source_8wekyb3d8bbwe\handle.exe"
    
    if (-not (Test-Path $handlePath)) {
        Write-Host "Handle.exe not found. Downloading from Sysinternals..." -ForegroundColor Yellow
        $url = "https://download.sysinternals.com/files/Handle.zip"
        $zipPath = Join-Path $env:TEMP "Handle.zip"
        $extractPath = Join-Path $env:TEMP "Handle"
        
        try {
            # Download Handle.zip
            Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
            
            # Extract the zip file
            if (-not (Test-Path $extractPath)) {
                New-Item -ItemType Directory -Path $extractPath | Out-Null
            }
            Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
            
            # Find handle.exe in the extracted files
            $handlePath = Get-ChildItem -Path $extractPath -Recurse -Filter "handle.exe" | Select-Object -First 1 -ExpandProperty FullName
            
            if (-not $handlePath) {
                throw "Could not find handle.exe in the downloaded files"
            }
            
            Write-Host "Downloaded handle.exe to: $handlePath" -ForegroundColor Green
        } catch {
            Write-Host "Error downloading or extracting handle.exe: $_" -ForegroundColor Red
            Write-Host "Please download it manually from: https://docs.microsoft.com/en-us/sysinternals/downloads/handle" -ForegroundColor Yellow
            exit 1
        }
    }
    
    # Run handle.exe to find processes locking files in node_modules
    try {
        Write-Host "Checking for processes locking files in node_modules..." -ForegroundColor Yellow
        $processes = & $handlePath -nobanner -a $nodeModulesPath 2>$null | 
            Where-Object { $_ -match '^(?<process>\S+)\s+pid: (?<pid>\d+)\s+type: (?<type>\w+)\s+(?<name>\S+)' } | 
            ForEach-Object {
                [PSCustomObject]@{
                    ProcessName = $matches['process']
                    ProcessId = $matches['pid']
                    HandleType = $matches['type']
                    FilePath = $matches['name']
                }
            }
        
        if ($processes) {
            Write-Host "Found processes with handles to files in node_modules:" -ForegroundColor Yellow
            $processes | Format-Table -AutoSize
            
            $confirmation = Read-Host "Do you want to stop these processes? (Y/N)"
            if ($confirmation -eq 'Y' -or $confirmation -eq 'y') {
                $processes | ForEach-Object {
                    $processId = $_.ProcessId
                    $processName = $_.ProcessName
                    try {
                        Stop-Process -Id $processId -Force -ErrorAction Stop
                        Write-Host "Stopped process: $processName (PID: $processId)" -ForegroundColor Green
                    } catch {
                        Write-Host "Failed to stop process $processName (PID: $processId): $_" -ForegroundColor Red
                    }
                }
                
                # Try to remove node_modules again after stopping processes
                try {
                    Remove-Item -Path $nodeModulesPath -Recurse -Force -ErrorAction Stop
                    Write-Host "Successfully removed node_modules directory." -ForegroundColor Green
                } catch {
                    Write-Host "Failed to remove node_modules after stopping processes: $_" -ForegroundColor Red
                    Write-Host "You may need to restart your computer to release all file locks." -ForegroundColor Yellow
                }
            } else {
                Write-Host "Process cleanup skipped. You may need to manually close applications using node_modules." -ForegroundColor Yellow
            }
        } else {
            Write-Host "No processes found with handles to files in node_modules." -ForegroundColor Green
            Write-Host "Attempting to remove node_modules..." -ForegroundColor Yellow
            
            try {
                Remove-Item -Path $nodeModulesPath -Recurse -Force -ErrorAction Stop
                Write-Host "Successfully removed node_modules directory." -ForegroundColor Green
            } catch {
                Write-Host "Failed to remove node_modules: $_" -ForegroundColor Red
                Write-Host "You may need to restart your computer to release file locks." -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "Error checking for file locks: $_" -ForegroundColor Red
    }
} else {
    Write-Host "node_modules directory not found at: $nodeModulesPath" -ForegroundColor Green
}

Write-Host "=== Script Complete ===" -ForegroundColor Cyan
