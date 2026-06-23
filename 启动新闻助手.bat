@echo off
chcp 65001 >nul

set "PYDIR=%LOCALAPPDATA%\Programs\Python\Python312"
set "SCRIPT=%~dp0news_digest.py"

if exist "%PYDIR%\python.exe" (
    "%PYDIR%\python.exe" "%SCRIPT%"
    if errorlevel 1 pause
    goto :EOF
)

python "%SCRIPT%" 2>nul
if not errorlevel 1 goto :EOF

py "%SCRIPT%" 2>nul
if not errorlevel 1 goto :EOF

echo Error: Python not found. Please install Python 3.12 from Microsoft Store.
pause