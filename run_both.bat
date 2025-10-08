@echo off
REM Start frontend in a new window
start "Frontend" cmd /k "cd /d %~dp0frontend && npm start"

REM Start backend in the current window
cd /d %~dp0
call ".venv\Scripts\python.exe" backend\app.py