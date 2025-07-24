@echo off
REM Script to secure sensitive files with proper permissions

setlocal enabledelayedexpansion

:: Set Python executable (use the one from the virtual environment if available)
if exist "%VIRTUAL_ENV%\Scripts\python.exe" (
    set PYTHON="%VIRTUAL_ENV%\Scripts\python.exe"
) else (
    set PYTHON=python
)

echo Securing sensitive files in %CD%
echo ====================================

:: First do a dry run to show what will be changed
%PYTHON% scripts\secure_files.py --dry-run

:: Ask for confirmation
set /p CONFIRM=Do you want to apply these changes? (y/n) 
if /i "!CONFIRM!"=="y" (
    echo Applying changes...
    %PYTHON% scripts\secure_files.py
    echo.
    echo Security settings applied successfully.
) else (
    echo Operation cancelled.
)

pause
