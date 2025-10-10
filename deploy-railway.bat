@echo off
REM Railway Deployment Script for Windows

echo 🚀 Deploying to Railway...

REM Check if Railway CLI is installed
where railway >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Railway CLI not found. Please install it first:
    echo npm install -g @railway/cli
    exit /b 1
)

REM Check if logged in
railway whoami >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Not logged in to Railway. Please run:
    echo railway login
    exit /b 1
)

echo ✅ Railway CLI found and logged in

REM Deploy backend
echo 📦 Deploying backend...
cd backend
railway up --service backend

REM Deploy frontend
echo 🎨 Deploying frontend...
cd ..\frontend
railway up --service frontend

echo 🎉 Deployment complete!
echo 📝 Don't forget to set environment variables in Railway dashboard