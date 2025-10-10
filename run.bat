@echo off

start "Timetable Wizard - Frontend" cmd /k "cd /d "%~dp0frontend" && echo ======================================= && echo    TIMETABLE WIZARD - FRONTEND SERVER && echo ======================================= && echo Starting React development server... && echo. && npm start"

timeout /t 2 /nobreak >nul

start "Timetable Wizard - Backend" cmd /k "cd /d "%~dp0backend" && echo ======================================= && echo     TIMETABLE WIZARD - BACKEND SERVER && echo ======================================= && echo Starting Python backend server... && echo. && python app.py"