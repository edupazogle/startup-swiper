#!/bin/bash
# Quick test script for Slush Events Scraper

echo "========================================"
echo "Slush Events Scraper - Test Run"
echo "========================================"
echo ""

# Check if Selenium is running
echo "1. Checking Selenium container..."
if sudo docker ps | grep -q selenium; then
    echo "   ✅ Selenium container is running"
else
    echo "   ❌ Selenium container not running"
    echo "   Starting Selenium container..."
    sudo docker run -d \
        --name selenium-chrome \
        -p 4444:4444 \
        -p 7900:7900 \
        --shm-size="2g" \
        selenium/standalone-chrome:latest
    
    echo "   ⏳ Waiting 10 seconds for Selenium to start..."
    sleep 10
fi

echo ""
echo "2. Checking credentials..."
if grep -q "SLUSH_EMAIL" .env && grep -q "SLUSH_PASSWORD" .env; then
    echo "   ✅ Credentials found in .env"
else
    echo "   ❌ Credentials not found in .env"
    exit 1
fi

echo ""
echo "3. Running events scraper (limiting to 5 events for testing)..."
echo ""
python3 scrape_slush_events.py --limit 5 --screenshots

echo ""
echo "========================================"
echo "Test Complete!"
echo "========================================"
echo ""
echo "Check outputs:"
echo "  - slush_events.json"
echo "  - slush_events.db"
echo "  - slush_events_screenshots/ (if any)"
echo ""
echo "To scrape all events, run:"
echo "  python3 scrape_slush_events.py"
echo ""
