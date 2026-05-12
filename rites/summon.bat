@echo off
REM rites\summon.bat
REM Grimoire Summoning Rite — Bootstrap (Windows)
REM
REM Checks for Python 3 and launches the cross-platform summoning script.
REM
REM Entry point (CMD):
REM   if exist %TEMP%\grimoire-summon rmdir /s /q %TEMP%\grimoire-summon && git clone --depth 1 <your-arcana-url> %TEMP%\grimoire-summon && %TEMP%\grimoire-summon\rites\summon.bat
REM
REM Entry point (PowerShell):
REM   Remove-Item -Recurse -Force "$env:TEMP\grimoire-summon" -ErrorAction SilentlyContinue; git clone --depth 1 <your-arcana-url> "$env:TEMP\grimoire-summon"; & "$env:TEMP\grimoire-summon\rites\summon.bat"

SET SCRIPT_DIR=%~dp0

REM Try python first (Windows default), then python3
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)" >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        python "%SCRIPT_DIR%summon.py" %*
        exit /b %ERRORLEVEL%
    )
)

where python3 >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python3 "%SCRIPT_DIR%summon.py" %*
    exit /b %ERRORLEVEL%
)

echo.
echo   Python 3 is required but not found.
echo.
echo   Download from: https://www.python.org/downloads/
echo   Make sure to check "Add Python to PATH" during installation.
echo.
pause
exit /b 1
