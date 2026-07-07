@echo off
setlocal

:: Move to the directory where the script is located
cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python to continue.
    pause
    exit /b 1
)

:: Check if the virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    
    echo Installing dependencies...
    :: We install the package in editable mode with 'app' dependencies
    pip install -e .[app]
) else (
    echo Activating existing virtual environment...
    call .venv\Scripts\activate.bat
)

echo Starting Streamlit app...
streamlit run web\app.py

endlocal
