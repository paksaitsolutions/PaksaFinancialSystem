@echo off
echo Starting Diagnostics... > diagnostics.log
echo ====================== >> diagnostics.log
echo Date: %date% %time% >> diagnostics.log
echo ====================== >> diagnostics.log

echo. >> diagnostics.log
echo === Node.js Version === >> diagnostics.log
node --version >> diagnostics.log 2>&1

echo. >> diagnostics.log
echo === NPM Version === >> diagnostics.log
npm --version >> diagnostics.log 2>&1

echo. >> diagnostics.log
echo === Vite Version === >> diagnostics.log
npx vite --version >> diagnostics.log 2>&1

echo. >> diagnostics.log
echo === NPM List === >> diagnostics.log
npm list --depth=0 >> diagnostics.log 2>&1

echo. >> diagnostics.log
echo === Environment Variables === >> diagnostics.log
set >> diagnostics.log

echo. >> diagnostics.log
echo === Directory Listing === >> diagnostics.log
dir /a >> diagnostics.log

echo. >> diagnostics.log
echo === Running Vite with Debug === >> diagnostics.log
set DEBUG=vite:*
set NODE_OPTIONS=--trace-warnings --unhandled-rejections=strict
npx vite --config vite.minimal.test.js --debug >> diagnostics.log 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo. >> diagnostics.log
    echo === Vite Failed with Error Level %ERRORLEVEL% === >> diagnostics.log
) else (
    echo. >> diagnostics.log
    echo === Vite Exited Successfully === >> diagnostics.log
)

echo. >> diagnostics.log
echo === Diagnostics Complete === >> diagnostics.log
type diagnostics.log

pause
