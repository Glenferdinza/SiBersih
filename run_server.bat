@echo off
echo ========================================
echo   SiBersih - Setup & Run Server
echo ========================================
echo.

echo Checking virtual environment...
if not exist .venv (
    echo Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo   Database Migration
echo ========================================
echo.
echo Running migrations...
python manage.py migrate

echo.
echo ========================================
echo   Setup Initial Data
echo ========================================
echo.
python manage.py setup_initial_data

echo.
echo ========================================
echo   Starting Development Server
echo ========================================
echo.
echo Server will start at http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver

pause
