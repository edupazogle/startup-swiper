#!/bin/bash

# Quick start script for the FastAPI + LiteLLM application

echo "=========================================="
echo "Startup Swiper API - Quick Start"
echo "=========================================="
echo ""

# Check if in correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found!"
    echo "Please run this script from the /api directory"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Found Python: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    echo "❗ Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY for GPT models"
    echo "   - ANTHROPIC_API_KEY for Claude models"
    echo ""
    read -p "Press Enter to continue (you can add keys later)..."
else
    echo "✓ Found .env file"
fi
echo ""

# Create logs directory
echo "📁 Setting up logs directory..."
mkdir -p logs/llm
echo "✓ Logs directory ready: logs/llm"
echo ""

# Start the API
echo "=========================================="
echo "🚀 Starting FastAPI server..."
echo "=========================================="
echo ""
echo "API will be available at:"
echo "  • Main API: http://localhost:8000"
echo "  • Docs: http://localhost:8000/docs"
echo "  • ReDoc: http://localhost:8000/redoc"
echo ""
echo "LLM logs will be saved to: logs/llm/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
