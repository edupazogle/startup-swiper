#!/bin/bash
# Setup script for Selenium tests

echo "=========================================="
echo "Selenium Test Environment Setup"
echo "=========================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Install Selenium and dependencies
echo ""
echo "Installing Selenium and dependencies..."
pip3 install -r requirements.txt

# Check if Chrome is installed
if command -v google-chrome &> /dev/null; then
    echo "✓ Google Chrome found: $(google-chrome --version)"
elif command -v chromium-browser &> /dev/null; then
    echo "✓ Chromium found: $(chromium-browser --version)"
else
    echo "⚠️  Chrome/Chromium not found. Installing chromium-browser..."
    sudo apt-get update
    sudo apt-get install -y chromium-browser chromium-chromedriver
fi

# Check if ChromeDriver is available
if command -v chromedriver &> /dev/null; then
    echo "✓ ChromeDriver found: $(chromedriver --version)"
else
    echo "⚠️  ChromeDriver not found. Installing..."
    sudo apt-get install -y chromium-chromedriver
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To run the tests:"
echo "  python3 selenium_navigation_test.py"
echo ""
echo "Options:"
echo "  --url http://localhost:5173  (default)"
echo "  --headless                   (run without GUI)"
echo ""
echo "Example:"
echo "  python3 selenium_navigation_test.py --headless"
echo ""
