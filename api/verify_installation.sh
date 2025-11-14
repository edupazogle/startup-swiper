#!/bin/bash

# Installation verification script for LiteLLM integration

echo "=========================================="
echo "LiteLLM Integration Verification"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✓ Python 3: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "llm_config.py" ]; then
    echo "❌ Not in API directory. Please run from /home/akyo/startup_swiper/api"
    exit 1
fi
echo "✓ In API directory"

# Check required files
echo ""
echo "Checking required files..."
files=(
    "main.py"
    "llm_config.py"
    "database.py"
    "models.py"
    "schemas.py"
    "crud.py"
    "requirements.txt"
    ".env.example"
    "start.sh"
    "test_llm.py"
    "examples_llm.py"
)

all_files_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ❌ $file"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo ""
    echo "❌ Some required files are missing"
    exit 1
fi

# Check logs directory
echo ""
echo "Checking logs directory..."
if [ -d "../logs/llm" ]; then
    echo "  ✓ logs/llm directory exists"
    if [ -w "../logs/llm" ]; then
        echo "  ✓ logs/llm is writable"
    else
        echo "  ⚠️  logs/llm is not writable"
    fi
else
    echo "  ❌ logs/llm directory not found"
    exit 1
fi

# Check documentation
echo ""
echo "Checking documentation..."
docs=(
    "README.md"
    "LLM_INTEGRATION.md"
    "IMPLEMENTATION_SUMMARY.md"
    "ARCHITECTURE.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "  ✓ $doc"
    else
        echo "  ⚠️  $doc not found"
    fi
done

# Check requirements.txt contains litellm
echo ""
echo "Checking dependencies..."
if grep -q "litellm" requirements.txt; then
    echo "  ✓ litellm in requirements.txt"
else
    echo "  ❌ litellm not in requirements.txt"
    exit 1
fi

if grep -q "aiofiles" requirements.txt; then
    echo "  ✓ aiofiles in requirements.txt"
else
    echo "  ❌ aiofiles not in requirements.txt"
    exit 1
fi

# Check .env file
echo ""
echo "Checking configuration..."
if [ -f ".env" ]; then
    echo "  ✓ .env file exists"
    if grep -q "OPENAI_API_KEY" .env || grep -q "ANTHROPIC_API_KEY" .env; then
        echo "  ✓ API keys configured in .env"
    else
        echo "  ⚠️  No API keys found in .env (you'll need to add them)"
    fi
else
    echo "  ⚠️  .env file not found (will be created from .env.example)"
fi

# Check if dependencies are installed
echo ""
echo "Checking installed packages..."
if python3 -c "import litellm" 2>/dev/null; then
    echo "  ✓ litellm is installed"
else
    echo "  ⚠️  litellm not installed (run: pip install -r requirements.txt)"
fi

if python3 -c "import fastapi" 2>/dev/null; then
    echo "  ✓ fastapi is installed"
else
    echo "  ⚠️  fastapi not installed (run: pip install -r requirements.txt)"
fi

# Summary
echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""
echo "✓ All core files present"
echo "✓ Logs directory configured"
echo "✓ Dependencies listed in requirements.txt"
echo ""

if [ -f ".env" ]; then
    echo "Next steps:"
    echo "1. Ensure API keys are in .env file"
    echo "2. Install dependencies: pip install -r requirements.txt"
    echo "3. Start server: ./start.sh"
    echo "4. Run tests: python test_llm.py"
else
    echo "Next steps:"
    echo "1. Copy .env.example to .env: cp .env.example .env"
    echo "2. Add your API keys to .env"
    echo "3. Install dependencies: pip install -r requirements.txt"
    echo "4. Start server: ./start.sh"
    echo "5. Run tests: python test_llm.py"
fi

echo ""
echo "📚 Documentation:"
echo "  • Main README: README.md"
echo "  • LLM Guide: LLM_INTEGRATION.md"
echo "  • Architecture: ARCHITECTURE.md"
echo "  • Summary: IMPLEMENTATION_SUMMARY.md"
echo ""
echo "🎉 LiteLLM integration is ready!"
