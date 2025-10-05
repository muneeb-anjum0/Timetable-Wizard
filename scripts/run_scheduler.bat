@echo off
REM Activate venv and (later) run the scheduler
setlocal EnableDelayedExpansion
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%\..
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)
REM Placeholder: the actual run command will go here later, e.g.:
REM python -m src.scraper.main --run-scheduler
echo Scheduler placeholder. Implementation will be added later.