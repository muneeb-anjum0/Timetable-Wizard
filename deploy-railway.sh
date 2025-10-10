#!/bin/bash
# Railway Deployment Script

echo "🚀 Deploying to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway. Please run:"
    echo "railway login"
    exit 1
fi

echo "✅ Railway CLI found and logged in"

# Deploy backend
echo "📦 Deploying backend..."
cd backend
railway up --service backend

# Deploy frontend  
echo "🎨 Deploying frontend..."
cd ../frontend
railway up --service frontend

echo "🎉 Deployment complete!"
echo "📝 Don't forget to set environment variables in Railway dashboard"