@echo off
echo Cleaning up project...

REM Remove node_modules
if exist node_modules (
  echo Removing node_modules...
  rmdir /s /q node_modules
)

REM Remove package-lock.json
if exist package-lock.json (
  echo Removing package-lock.json...
  del package-lock.json
)

REM Remove Vite cache
if exist node_modules\.vite (
  echo Removing Vite cache...
  rmdir /s /q node_modules\.vite
)

echo Cleanup complete!
pause
