@echo off
echo 🚀 Starting Timetable Scraper Development Environment

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install backend dependencies
echo Installing backend dependencies...
pip install -r backend\requirements.txt

REM Install frontend dependencies
echo Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo ✅ Setup complete!
echo.
echo To start the application:
echo 1. Backend: cd backend ^&^& python app.py
echo 2. Frontend: cd frontend ^&^& npm start
echo.
echo URLs:
echo - Frontend: http://localhost:3000
echo - Backend: http://localhost:5000

pause