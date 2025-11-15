#!/bin/bash

# ====================
# AI Concierge MCP Setup Script
# ====================
# This script sets up the AI Concierge with MCP and NVIDIA NIM support

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_DIR="$SCRIPT_DIR"

echo "=================================================="
echo "AI Concierge MCP + NVIDIA NIM Setup"
echo "=================================================="
echo ""

# Check Python version
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "  Python version: $PYTHON_VERSION"
echo ""

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "✓ Activating virtual environment..."
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "  Virtual environment activated"
else
    echo "⚠️  No virtual environment found at $PROJECT_ROOT/.venv"
    echo "  Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "  Virtual environment created and activated"
fi
echo ""

# Install dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r "$API_DIR/requirements.txt" > /dev/null 2>&1
echo "  Dependencies installed"
echo ""

# Check environment variables
echo "✓ Checking environment configuration..."

if [ ! -f "$API_DIR/.env" ]; then
    echo "⚠️  .env file not found at $API_DIR/.env"
    echo "  Creating from template..."
    if [ -f "$API_DIR/.env.example" ]; then
        cp "$API_DIR/.env.example" "$API_DIR/.env"
        echo "  .env created from .env.example"
        echo "  ⚠️  Please update NVIDIA_API_KEY in $API_DIR/.env"
    else
        echo "✗ .env.example not found"
        exit 1
    fi
else
    if grep -q "NVIDIA_API_KEY=" "$API_DIR/.env"; then
        API_KEY=$(grep "NVIDIA_API_KEY=" "$API_DIR/.env" | cut -d'=' -f2)
        if [ -z "$API_KEY" ] || [ "$API_KEY" = "nvapi-..." ]; then
            echo "⚠️  NVIDIA_API_KEY not configured in .env"
            echo "  Please update: $API_DIR/.env"
        else
            echo "  NVIDIA_API_KEY configured (****...)"
        fi
    fi
fi
echo ""

# Verify database
echo "✓ Checking database..."
if [ ! -f "$PROJECT_ROOT/startup_swiper.db" ]; then
    echo "⚠️  Database not found at $PROJECT_ROOT/startup_swiper.db"
    echo "  You may need to initialize the database:"
    echo "    cd $API_DIR"
    echo "    python create_startup_database.py"
else
    echo "  Database found: startup_swiper.db"
fi
echo ""

# Verify MCP modules
echo "✓ Verifying MCP modules..."
if python3 -c "import mcp" 2>/dev/null; then
    echo "  MCP module: installed"
else
    echo "✗ MCP module not found"
    echo "  Installing..."
    pip install mcp
fi

if [ -f "$API_DIR/mcp_startup_server.py" ]; then
    echo "  MCP Startup Server: mcp_startup_server.py"
else
    echo "✗ MCP Startup Server not found"
fi

if [ -f "$API_DIR/mcp_client.py" ]; then
    echo "  MCP Client: mcp_client.py"
else
    echo "✗ MCP Client not found"
fi
echo ""

# Test imports
echo "✓ Testing Python imports..."
python3 << 'EOF'
import sys
modules = [
    ('litellm', 'LiteLLM'),
    ('mcp', 'Model Context Protocol'),
    ('sqlalchemy', 'SQLAlchemy'),
    ('fastapi', 'FastAPI'),
]

failed = []
for module, name in modules:
    try:
        __import__(module)
        print(f"  ✓ {name}")
    except ImportError:
        print(f"  ✗ {name}")
        failed.append(module)

if failed:
    print(f"\n⚠️  Some modules failed to import: {', '.join(failed)}")
    sys.exit(1)
EOF
echo ""

# Configuration summary
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Update API configuration:"
echo "   Edit $API_DIR/.env"
echo "   - Set NVIDIA_API_KEY from https://build.nvidia.com/"
echo "   - Verify NVIDIA_DEFAULT_MODEL"
echo "   - Optional: Add alternative LLM providers (OpenAI, Anthropic)"
echo ""
echo "2. Initialize/verify database:"
echo "   cd $API_DIR"
echo "   python create_startup_database.py  # If needed"
echo ""
echo "3. Start the API server:"
echo "   cd $API_DIR"
echo "   python main.py"
echo ""
echo "4. In another terminal, start the frontend:"
echo "   cd $PROJECT_ROOT/app/startup-swipe-schedu"
echo "   npm run dev"
echo ""
echo "5. Test the MCP integration:"
echo "   python test_llm.py"
echo ""
echo "Documentation:"
echo "   - Setup Guide: $API_DIR/MCP_INTEGRATION_GUIDE.md"
echo "   - Architecture: $API_DIR/ARCHITECTURE.md"
echo ""
echo "=================================================="
