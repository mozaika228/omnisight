#!/usr/bin/env bash
# Linux/Mac setup script for OmniSight local development

set -e

echo "🚀 OmniSight Local Setup (Linux/Mac)"
echo "===================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.10+ required. Install from https://www.python.org/"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 18+ required. Install from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Create venv
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install Node dependencies
echo "🎨 Installing Node.js dependencies..."
cd apps/web
npm install
cd ../../

# Setup .env
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start PostgreSQL: brew install postgresql && brew services start postgresql"
echo "2. Start Redis: brew install redis && redis-server"
echo "3. Start Qdrant: (download from GitHub)"
echo "4. Activate venv: source venv/bin/activate"
echo "5. Start backend: uvicorn apps.api.main:app --reload"
echo "6. Start frontend: cd apps/web && npm run dev"
echo ""
echo "Access: http://localhost:3000"
