@echo off
echo Running ESLint and Prettier...

echo.
echo Installing linting dependencies...
npm install

echo.
echo Running ESLint (auto-fix)...
npx eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix

echo.
echo Running Prettier (format)...
npx prettier --write src/

echo.
echo Linting complete!
pause