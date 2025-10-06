#!/bin/bash

# Quick start script for local development

echo "🚀 Starting Timetable Scraper Development Environment"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/Scripts/activate  # For Windows Git Bash
# source .venv/bin/activate    # For Linux/Mac

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && python app.py"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "URLs:"
echo "- Frontend: http://localhost:3000"
echo "- Backend: http://localhost:5000"