@echo off
echo Cleaning up...
rmdir /s /q node_modules
rmdir /s /q .vite
rmdir /s /q dist

echo Installing dependencies...
call npm install

echo Done! You can now start the development server with: npm run dev
