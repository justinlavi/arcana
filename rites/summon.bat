@echo off
REM rites\summon.bat
REM Grimoire Summoning Rite — Bootstrap (Windows)
REM
REM Checks for Python 3 and launches the cross-platform summoning script.
REM
REM Entry point (CMD):
REM   powershell -NoProfile -ExecutionPolicy Bypass -Command "$d=Join-Path $env:TEMP 'grimoire-summon'; New-Item -ItemType Directory -Force (Join-Path $d 'rites') | Out-Null; Invoke-WebRequest https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.bat -OutFile (Join-Path $d 'rites\summon.bat'); Invoke-WebRequest https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.py -OutFile (Join-Path $d 'rites\summon.py'); & (Join-Path $d 'rites\summon.bat')"
REM
REM Entry point (PowerShell):
REM   $d=Join-Path $env:TEMP 'grimoire-summon'; New-Item -ItemType Directory -Force (Join-Path $d 'rites') | Out-Null; Invoke-WebRequest https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.bat -OutFile (Join-Path $d 'rites\summon.bat'); Invoke-WebRequest https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.py -OutFile (Join-Path $d 'rites\summon.py'); & (Join-Path $d 'rites\summon.bat')

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
