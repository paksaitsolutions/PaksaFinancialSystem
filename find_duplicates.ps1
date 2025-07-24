# Find files that may be duplicates or similar
$files = Get-ChildItem -Path . -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -notmatch '\.git|__pycache__|\.venv|node_modules' }

# Group by file name and size to find potential duplicates
$potentialDuplicates = $files | 
    Group-Object -Property @{Expression={$_.Name.ToLower() + "_" + $_.Length}} | 
    Where-Object { $_.Count -gt 1 }

# Output the results
if ($potentialDuplicates.Count -gt 0) {
    Write-Host "Found $($potentialDuplicates.Count) sets of potential duplicate files:" -ForegroundColor Yellow
    $potentialDuplicates | ForEach-Object {
        Write-Host "`nFiles with name '$($_.Group[0].Name)' and size $($_.Group[0].Length):" -ForegroundColor Cyan
        $_.Group | ForEach-Object {
            Write-Host "- $($_.FullName)"
        }
    }
} else {
    Write-Host "No duplicate files found." -ForegroundColor Green
}

# Find similar file names (case insensitive)
$similarNames = $files | 
    Group-Object -Property { $_.Name.ToLower() } | 
    Where-Object { $_.Count -gt 1 } |
    Sort-Object -Property Name

# Output similar file names
if ($similarNames.Count -gt 0) {
    Write-Host "`nFound $($similarNames.Count) sets of files with similar names (case insensitive):" -ForegroundColor Yellow
    $similarNames | ForEach-Object {
        Write-Host "`nFiles named like '$($_.Name)':" -ForegroundColor Magenta
        $_.Group | ForEach-Object {
            Write-Host "- $($_.FullName)"
        }
    }
} else {
    Write-Host "`nNo files with similar names found." -ForegroundColor Green
}
