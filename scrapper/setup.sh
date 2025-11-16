#!/bin/bash
# Scraper Setup and Execution Script

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🚀 SLUSH STARTUP SCRAPER - Docker + Selenium"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
   echo "⚠️  Some commands require sudo"
   SUDO="echo 8246 | sudo -S"
else
   SUDO=""
fi

# Step 1: Install Docker if needed
echo "1️⃣  Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "   Installing Docker..."
    $SUDO apt-get update -qq
    $SUDO apt-get install -y docker.io 2>&1 | tail -3
    $SUDO usermod -aG docker $USER
    echo "   ✅ Docker installed"
else
    echo "   ✅ Docker already installed: $(docker --version)"
fi

# Step 2: Start Docker service
echo ""
echo "2️⃣  Starting Docker..."
$SUDO service docker start 2>&1 | tail -1
sleep 2
echo "   ✅ Docker service started"

# Step 3: Pull Selenium image
echo ""
echo "3️⃣  Pulling Selenium Chrome image..."
$SUDO docker pull selenium/standalone-chrome:latest 2>&1 | tail -1
echo "   ✅ Selenium image ready"

# Step 4: Start Selenium container
echo ""
echo "4️⃣  Starting Selenium container..."
CONTAINER_ID=$($SUDO docker ps -a | grep selenium-chrome | awk '{print $1}')

if [ ! -z "$CONTAINER_ID" ]; then
    echo "   Stopping existing container..."
    $SUDO docker stop $CONTAINER_ID 2>&1 || true
    $SUDO docker rm $CONTAINER_ID 2>&1 || true
fi

$SUDO docker run -d \
  --name selenium-chrome \
  -p 4444:4444 \
  -p 7900:7900 \
  --shm-size="2g" \
  selenium/standalone-chrome:latest > /dev/null

echo "   ✅ Selenium container started (port 4444)"

# Step 5: Wait for Selenium to be ready
echo ""
echo "5️⃣  Waiting for Selenium to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:4444/status > /dev/null 2>&1; then
        echo "   ✅ Selenium ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  Selenium timeout - proceeding anyway"
    fi
    sleep 1
done

# Step 6: Setup Python environment
echo ""
echo "6️⃣  Checking Python environment..."
if [ ! -d ".venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "   ✅ Virtual environment ready"

# Step 7: Install dependencies
echo ""
echo "7️⃣  Installing dependencies..."
pip install -q selenium beautifulsoup4 requests python-dotenv 2>&1 | tail -1
echo "   ✅ Dependencies installed"

# Step 8: Ready to scrape
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Run scraping commands:"
echo ""
echo "1. Browse page scraper:"
echo "   python3 scrape_slush_browse_remote.py"
echo ""
echo "2. Profile detail scraper:"
echo "   python3 scrape_slush_profiles_remote.py --limit 100"
echo ""
echo "3. Extract data:"
echo "   python3 extract_product_market_data.py --limit 3665"
echo ""
echo "4. Watch in browser:"
echo "   http://localhost:7900 (password: secret)"
echo ""
echo "Useful commands:"
echo "   tail -f *.log              - Monitor logs"
echo "   docker ps                  - Check container status"
echo "   docker logs selenium-chrome - View Selenium logs"
echo ""
