@echo off
echo ========================================================
echo [Github Login Helper]
echo Running GitHub CLI Login...
echo.
echo Follow these steps:
echo 1. Select 'GitHub.com' (Press Enter)
echo 2. Select 'HTTPS' (Press Enter)
echo 3. Select 'Yes' to authenticate Git (Press Enter)
echo 4. Select 'Login with a web browser' (Press Enter)
echo.
echo ========================================================

"C:\Program Files\GitHub CLI\gh.exe" auth login

echo.
echo Login process finished.
pause
