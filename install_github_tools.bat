@echo off
echo ========================================================
echo [Github & Git Installation Helper]
echo Installing Git and GitHub CLI via Winget...
echo You may be prompted to allow changes (User Account Control).
echo Please click 'Yes' if prompted.
echo ========================================================

echo.
echo 1. Installing Git...
winget install --id Git.Git -e --source winget
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git installation failed. Please try installing manually from https://git-scm.com/download/win
) else (
    echo [SUCCESS] Git installed successfully.
)

echo.
echo 2. Installing GitHub CLI...
winget install --id GitHub.cli -e --source winget
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] GitHub CLI installation failed. Please try installing manually from https://cli.github.com/
) else (
    echo [SUCCESS] GitHub CLI installed successfully.
)

echo.
echo ========================================================
echo [IMPORTANT] installation complete!
echo.
echo To use Git and GitHub CLI, you MUST restart your terminal or computer.
echo.
echo After restarting, run this command in your terminal to login:
echo     gh auth login
echo.
echo Press any key to close this window...
pause > nul
