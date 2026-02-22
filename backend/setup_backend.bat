@echo off
cd /d "%~dp0"
echo Recreating Virtual Environment...
if exist venv (
    echo Removing existing venv...
    rmdir /s /q venv
)
echo Creating new venv...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo Failed to create venv. Make sure Python is installed and in your PATH.
    pause
    exit /b 1
)
echo Installing dependencies...
venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)
echo Setup complete! You can now run the backend using run_backend.bat
pause
