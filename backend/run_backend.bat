@echo off
cd /d "%~dp0"
echo Starting WasteWise Backend...
"venv\Scripts\python.exe" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
if %ERRORLEVEL% neq 0 (
    echo.
    echo Backend failed to start.
    pause
)
