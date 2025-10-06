@echo off
REM Activate virtual environment (if present) and run the scheduler once.
setlocal EnableDelayedExpansion
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%\.."
if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
)
REM Run the Python module. Forward any extra args.
python -m src.scraper.main --once %*
set EXITCODE=%ERRORLEVEL%
exit /b %EXITCODE%
