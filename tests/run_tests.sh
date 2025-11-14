#!/bin/bash
# Quick test runner for Selenium tests

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Startup Swiper - Selenium Test Runner                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
BASE_URL="http://localhost:5173"
HEADLESS=false
TEST_TYPE="full"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --headless)
            HEADLESS=true
            shift
            ;;
        --url)
            BASE_URL="$2"
            shift 2
            ;;
        --basic)
            TEST_TYPE="basic"
            shift
            ;;
        --full)
            TEST_TYPE="full"
            shift
            ;;
        --help)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --headless        Run in headless mode (no GUI)"
            echo "  --url URL         Set base URL (default: http://localhost:5173)"
            echo "  --basic           Run basic navigation test"
            echo "  --full            Run full exploration test (default)"
            echo "  --help            Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check if app is running
echo "🔍 Checking if application is running..."
if curl -s "$BASE_URL" > /dev/null; then
    echo -e "${GREEN}✓${NC} Application is running at $BASE_URL"
else
    echo -e "${YELLOW}⚠${NC} Application not reachable at $BASE_URL"
    echo ""
    read -p "Do you want to start the application? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting application..."
        cd ..
        ./launch.sh &
        sleep 10
        cd tests
        echo -e "${GREEN}✓${NC} Application started"
    else
        echo -e "${RED}✗${NC} Tests require the application to be running"
        exit 1
    fi
fi

# Check dependencies
echo ""
echo "🔍 Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC} Python 3 not found"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3 found"

if ! python3 -c "import selenium" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Selenium not installed"
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi
echo -e "${GREEN}✓${NC} Selenium installed"

if ! command -v chromedriver &> /dev/null && ! command -v chromium-chromedriver &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} ChromeDriver not found"
    echo "Please run: ./setup_selenium.sh"
    exit 1
fi
echo -e "${GREEN}✓${NC} ChromeDriver found"

# Run tests
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Starting Tests"
echo "═══════════════════════════════════════════════════════════════"
echo "  Type: $TEST_TYPE"
echo "  URL: $BASE_URL"
echo "  Headless: $HEADLESS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Build command
if [ "$TEST_TYPE" == "basic" ]; then
    CMD="python3 selenium_navigation_test.py --url $BASE_URL"
else
    CMD="python3 selenium_full_exploration.py --url $BASE_URL"
fi

if [ "$HEADLESS" == "true" ]; then
    CMD="$CMD --headless"
fi

# Run the test
echo "Running: $CMD"
echo ""

if $CMD; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${GREEN}✓ TESTS COMPLETED SUCCESSFULLY${NC}"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "📸 Screenshots: selenium_screenshots/"
    echo "📝 Log files: selenium_test_*.log"
    echo ""
    
    # Count screenshots
    SCREENSHOT_COUNT=$(ls -1 selenium_screenshots/*.png 2>/dev/null | wc -l)
    echo "Generated $SCREENSHOT_COUNT screenshots"
    
    # Show latest log
    LATEST_LOG=$(ls -t selenium_test_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo ""
        echo "Latest log file: $LATEST_LOG"
        echo ""
        echo "Last 10 lines of log:"
        echo "---"
        tail -10 "$LATEST_LOG"
    fi
    
    exit 0
else
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${RED}✗ TESTS FAILED${NC}"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Check the log files and screenshots for details."
    exit 1
fi
