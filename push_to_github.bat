@echo off
title Push OptiFlow to GitHub
cls
echo =======================================================
echo          Push OptiFlow to Your GitHub
echo =======================================================
echo.
echo Make sure you have created an empty repository on GitHub:
echo https://github.com/new (Name: optiflow)
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/USERNAME/optiflow.git): "
if "%REPO_URL%"=="" (
    echo [!] No repository URL entered. Exiting.
    pause
    exit /b
)
echo.
echo [*] Configuring remote origin: %REPO_URL%
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo [*] Pushing main branch to GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] OptiFlow successfully published to GitHub!
) else (
    echo.
    echo [NOTE] If prompted by Windows Git Credential Manager, sign in via your browser.
)
echo.
pause
