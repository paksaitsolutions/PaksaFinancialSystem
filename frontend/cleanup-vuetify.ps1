# Cleanup script to remove Vuetify-related files and code

# Remove Vuetify CSS/SCSS files
$vuetifyFiles = @(
    "src\scss\settings.scss",
    "src\assets\styles\compatibility.css",
    "src\assets\scss\themes\_dark.scss",
    "src\assets\scss\themes\_light.scss",
    "src\assets\scss\main.scss",
    "src\assets\scss\variables\_colors.scss",
    "src\assets\scss\variables\_typography.scss"
)

foreach ($file in $vuetifyFiles) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force
        Write-Host "Removed: $file"
    }
}

# Remove Vuetify plugin files
$vuetifyPluginFiles = @(
    "src\plugins\theme.ts"
)

foreach ($file in $vuetifyPluginFiles) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force
        Write-Host "Removed: $file"
    }
}

# Remove node_modules and package-lock.json to ensure clean installation
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force node_modules
    Write-Host "Removed: node_modules"
}

if (Test-Path "package-lock.json") {
    Remove-Item -Force package-lock.json
    Write-Host "Removed: package-lock.json"
}

Write-Host "\nCleanup complete. Please run 'npm install' to reinstall dependencies."
