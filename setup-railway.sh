#!/bin/bash
# Quick setup script for Railway deployment

echo "🔧 Setting up Timetable Wizard for Railway deployment..."

# Create .env files from examples
echo "📝 Creating environment files..."

# Backend .env
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env - Please edit with your values"
else
    echo "⚠️  backend/.env already exists"
fi

# Frontend .env
if [ ! -f "frontend/.env" ]; then
    cp frontend/.env.example frontend/.env
    echo "✅ Created frontend/.env - Please edit with your values"
else
    echo "⚠️  frontend/.env already exists"
fi

# Install dependencies locally (optional)
echo "📦 Installing dependencies..."

# Backend dependencies
echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Frontend dependencies
echo "Installing Node.js dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit backend/.env with your Supabase credentials"
echo "2. Edit frontend/.env with your backend URL (after Railway deployment)"
echo "3. Set up your Supabase database using the SQL in RAILWAY_DEPLOYMENT.md"
echo "4. Deploy to Railway using the instructions in RAILWAY_DEPLOYMENT.md"
echo ""
echo "🚀 Ready for Railway deployment!"