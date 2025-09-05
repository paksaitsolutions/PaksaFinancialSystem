@echo off
echo Creating placeholder components for missing routes...

mkdir "src\modules\accounting\views" 2>nul
mkdir "src\modules\accounts-payable\views" 2>nul
mkdir "src\modules\accounts-payable\views\invoices" 2>nul
mkdir "src\modules\accounts-receivable\views" 2>nul
mkdir "src\modules\cash-management\views" 2>nul
mkdir "src\modules\inventory\views" 2>nul
mkdir "src\modules\fixed-assets\views" 2>nul
mkdir "src\modules\budget\views" 2>nul
mkdir "src\modules\payroll\views" 2>nul
mkdir "src\modules\tax\views" 2>nul
mkdir "src\modules\reports\views" 2>nul
mkdir "src\modules\ai-bi\views" 2>nul
mkdir "src\modules\super-admin\views" 2>nul
mkdir "src\modules\settings\views" 2>nul
mkdir "src\views\approvals" 2>nul
mkdir "src\views\common" 2>nul

echo Placeholder components created successfully!
echo Run the development server to test routes.
pause