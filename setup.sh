#!/bin/bash

# Investory - Quick Start Script
# This script sets up both backend and frontend for development

set -e

echo "🚀 Investory - Quick Start"
echo "============================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✅ Prerequisites met!"
echo ""

# Setup Backend
echo "📦 Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your Alpha Vantage API key"
fi

echo "✅ Backend setup complete!"
echo ""

# Setup Frontend
echo "📦 Setting up React frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "✅ Frontend setup complete!"
echo ""

# Instructions
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "  python main.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open your browser to: http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "  - README.md           : Overview and features"
echo "  - docs/API.md         : API documentation"
echo "  - docs/DEPLOYMENT.md  : Production deployment guide"
echo ""
echo "💡 Don't forget to:"
echo "  1. Get a free Alpha Vantage API key at: https://www.alphavantage.co/support/#api-key"
echo "  2. Add it to backend/.env file"
echo ""
echo "Happy investing! 📈"
