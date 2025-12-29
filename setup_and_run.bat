@echo off
echo ========================================
echo Lead Generation Engine - Setup Script
echo ========================================
echo.

REM Step 1: Remove old venv if it exists
echo [1/4] Cleaning up old virtual environment...
if exist venv (
    echo Removing old venv directory...
    rmdir /s /q venv 2>nul
    if exist venv (
        echo WARNING: Could not delete venv. Please close any running Python processes and try again.
        pause
        exit /b 1
    )
)
echo Old venv cleaned up successfully.
echo.

REM Step 2: Create new virtual environment
echo [2/4] Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    echo Make sure Python is installed and added to PATH.
    pause
    exit /b 1
)
echo Virtual environment created successfully.
echo.

REM Step 3: Install requirements
echo [3/4] Installing dependencies from requirements.txt...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

REM Step 4: Run Streamlit app
echo [4/4] Starting Streamlit application...
echo.
echo ========================================
echo Application is starting...
echo Press Ctrl+C to stop the server
echo ========================================
echo.
streamlit run app.py

REM Deactivate virtual environment when done
deactivate
