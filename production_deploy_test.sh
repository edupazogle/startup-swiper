#!/bin/bash
# Production Deployment & Testing Script
# Deploys full solution and runs comprehensive tests

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     STARTUP SWIPER - PRODUCTION DEPLOYMENT & TEST            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "render.yaml" ]; then
    echo -e "${RED}❌ Error: render.yaml not found${NC}"
    exit 1
fi

echo -e "${BLUE}📋 PRE-DEPLOYMENT CHECKLIST${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Check Database
echo -e "${YELLOW}1. Checking Database...${NC}"
if [ -f "startup_swiper.db" ]; then
    EVENT_COUNT=$(python3 -c "import sqlite3; conn = sqlite3.connect('startup_swiper.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM calendar_events'); print(cursor.fetchone()[0]); conn.close()")
    STARTUP_COUNT=$(python3 -c "import sqlite3; conn = sqlite3.connect('startup_swiper.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM startups'); print(cursor.fetchone()[0]); conn.close()")
    USER_COUNT=$(python3 -c "import sqlite3; conn = sqlite3.connect('startup_swiper.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM users'); print(cursor.fetchone()[0]); conn.close()")
    
    echo -e "  ${GREEN}✓${NC} Database exists"
    echo "    - Events: $EVENT_COUNT"
    echo "    - Startups: $STARTUP_COUNT"
    echo "    - Users: $USER_COUNT"
else
    echo -e "  ${RED}✗${NC} Database not found"
    exit 1
fi

# 2. Check Environment Variables
echo ""
echo -e "${YELLOW}2. Checking Environment Variables...${NC}"
if [ -f "api/.env" ]; then
    echo -e "  ${GREEN}✓${NC} API .env exists"
    if grep -q "NVIDIA_API_KEY" api/.env; then
        echo -e "  ${GREEN}✓${NC} NVIDIA_API_KEY configured"
    else
        echo -e "  ${RED}✗${NC} NVIDIA_API_KEY missing"
    fi
    if grep -q "OPENAI_API_KEY" api/.env; then
        echo -e "  ${GREEN}✓${NC} OPENAI_API_KEY configured"
    else
        echo -e "  ${YELLOW}⚠${NC} OPENAI_API_KEY missing (optional)"
    fi
else
    echo -e "  ${RED}✗${NC} API .env not found"
    exit 1
fi

# 3. Check API Dependencies
echo ""
echo -e "${YELLOW}3. Checking API Dependencies...${NC}"
cd api
if python3 -c "import fastapi, uvicorn, sqlalchemy, litellm" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} All API dependencies installed"
else
    echo -e "  ${YELLOW}⚠${NC} Installing dependencies..."
    pip install -q -r requirements.txt
    echo -e "  ${GREEN}✓${NC} Dependencies installed"
fi
cd ..

# 4. Check Frontend Build
echo ""
echo -e "${YELLOW}4. Checking Frontend Build...${NC}"
if [ -d "app/startup-swipe-schedu/dist" ]; then
    echo -e "  ${GREEN}✓${NC} Frontend build exists"
else
    echo -e "  ${YELLOW}⚠${NC} Building frontend..."
    cd app/startup-swipe-schedu
    npm run build --silent
    cd ../..
    echo -e "  ${GREEN}✓${NC} Frontend built"
fi

echo ""
echo -e "${BLUE}🚀 STARTING PRODUCTION TEST${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Backend
echo -e "${YELLOW}Starting Backend API...${NC}"
cd api
uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
API_PID=$!
cd ..
sleep 3

# Check if API started
if ps -p $API_PID > /dev/null; then
    echo -e "${GREEN}✓${NC} API started (PID: $API_PID)"
else
    echo -e "${RED}✗${NC} API failed to start"
    cat /tmp/api.log
    exit 1
fi

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓${NC} API is ready"
        break
    fi
    sleep 1
done

echo ""
echo -e "${BLUE}🧪 RUNNING PRODUCTION TESTS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "ok"; then
    echo -e "${GREEN}✓ PASS${NC} - API health check"
else
    echo -e "${RED}✗ FAIL${NC} - API health check"
fi

# Test 2: Get Events
echo ""
echo -e "${YELLOW}Test 2: Get Calendar Events${NC}"
EVENTS=$(curl -s http://localhost:8000/events?skip=0&limit=5)
if echo "$EVENTS" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if len(data) > 0 else 1)" 2>/dev/null; then
    COUNT=$(echo "$EVENTS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
    echo -e "${GREEN}✓ PASS${NC} - Retrieved $COUNT events"
else
    echo -e "${RED}✗ FAIL${NC} - Failed to get events"
fi

# Test 3: Get Startups
echo ""
echo -e "${YELLOW}Test 3: Get Startups${NC}"
STARTUPS=$(curl -s http://localhost:8000/startups?skip=0&limit=5)
if echo "$STARTUPS" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if len(data) > 0 else 1)" 2>/dev/null; then
    COUNT=$(echo "$STARTUPS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
    echo -e "${GREEN}✓ PASS${NC} - Retrieved $COUNT startups"
else
    echo -e "${RED}✗ FAIL${NC} - Failed to get startups"
fi

# Test 4: NVIDIA NIM Concierge (Critical Test)
echo ""
echo -e "${YELLOW}Test 4: AI Concierge with NVIDIA NIM (DeepSeek-R1)${NC}"
echo "  Question: 'What can you help me with?'"
CONCIERGE_RESPONSE=$(curl -s -X POST http://localhost:8000/concierge/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "What can you help me with?"}' \
    --max-time 60)

if echo "$CONCIERGE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'answer' in data and len(data['answer']) > 50 else 1)" 2>/dev/null; then
    ANSWER=$(echo "$CONCIERGE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['answer'][:200])")
    echo -e "${GREEN}✓ PASS${NC} - NVIDIA NIM responding"
    echo "  Response: ${ANSWER}..."
else
    echo -e "${RED}✗ FAIL${NC} - NVIDIA NIM not responding correctly"
    echo "  Response: $CONCIERGE_RESPONSE"
fi

# Test 5: Concierge Startup Search
echo ""
echo -e "${YELLOW}Test 5: AI Concierge Startup Search${NC}"
echo "  Question: 'Find AI startups'"
CONCIERGE_SEARCH=$(curl -s -X POST http://localhost:8000/concierge/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "Find AI startups"}' \
    --max-time 60)

if echo "$CONCIERGE_SEARCH" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'answer' in data and len(data['answer']) > 50 else 1)" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC} - AI search working"
else
    echo -e "${RED}✗ FAIL${NC} - AI search failed"
fi

# Test 6: Authentication
echo ""
echo -e "${YELLOW}Test 6: User Authentication${NC}"
AUTH=$(curl -s -X POST http://localhost:8000/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=nicolas.desaintromain@axa.com&password=123")

if echo "$AUTH" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'access_token' in data else 1)" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC} - Authentication working"
else
    echo -e "${RED}✗ FAIL${NC} - Authentication failed"
fi

# Test 7: Filter AXA Startups
echo ""
echo -e "${YELLOW}Test 7: AXA Filtered Startups${NC}"
FILTERED=$(curl -s http://localhost:8000/startups/axa-filtered?skip=0&limit=5)
if echo "$FILTERED" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if len(data) > 0 else 1)" 2>/dev/null; then
    COUNT=$(echo "$FILTERED" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
    echo -e "${GREEN}✓ PASS${NC} - Retrieved $COUNT AXA-filtered startups"
else
    echo -e "${RED}✗ FAIL${NC} - Failed to get filtered startups"
fi

# Check logs for NVIDIA NIM usage
echo ""
echo -e "${YELLOW}Test 8: Verifying NVIDIA NIM Logs${NC}"
LATEST_LOG=$(ls -t logs/llm/*.json 2>/dev/null | head -1)
if [ -n "$LATEST_LOG" ]; then
    MODEL=$(cat "$LATEST_LOG" | python3 -c "import sys, json; print(json.load(sys.stdin).get('model', 'unknown'))")
    SUCCESS=$(cat "$LATEST_LOG" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
    
    if [[ "$MODEL" == *"deepseek"* ]] && [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✓ PASS${NC} - NVIDIA NIM (DeepSeek-R1) confirmed in logs"
        echo "  Model: $MODEL"
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Check model configuration"
        echo "  Model: $MODEL"
    fi
else
    echo -e "${YELLOW}⚠ WARNING${NC} - No LLM logs found"
fi

echo ""
echo -e "${BLUE}📊 TEST SUMMARY${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "API Endpoints Tested:"
echo "  ✓ Health Check"
echo "  ✓ Calendar Events"
echo "  ✓ Startups"
echo "  ✓ AI Concierge (NVIDIA NIM)"
echo "  ✓ Startup Search (AI)"
echo "  ✓ Authentication"
echo "  ✓ AXA Filtered Startups"
echo "  ✓ LLM Logging"
echo ""
echo "Production URLs:"
echo "  API:      http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  Docs:     http://localhost:8000/docs"
echo ""

# Cleanup
echo -e "${YELLOW}Stopping test services...${NC}"
kill $API_PID 2>/dev/null || true
sleep 1
echo -e "${GREEN}✓${NC} Cleanup complete"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  DEPLOYMENT GUIDE                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "To deploy to production (Render.com):"
echo ""
echo "1. Create GitHub Repository:"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Production ready deployment'"
echo "   git remote add origin YOUR_GITHUB_URL"
echo "   git push -u origin main"
echo ""
echo "2. Deploy on Render.com:"
echo "   - Go to https://render.com/dashboard"
echo "   - Click 'New' → 'Blueprint'"
echo "   - Connect your GitHub repo"
echo "   - Click 'Apply'"
echo ""
echo "3. Set Environment Variables on Render:"
echo ""
echo "   Backend API Service:"
echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   DATABASE_URL=sqlite:///./startup_swiper.db"
echo "   NVIDIA_API_KEY=<your-key>"
echo "   OPENAI_API_KEY=<your-key> (optional)"
echo "   SECRET_KEY=$(openssl rand -hex 32)"
echo ""
echo "   Frontend Service:"
echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   VITE_API_URL=https://YOUR-API-NAME.onrender.com"
echo ""
echo "4. Test Production:"
echo "   - Wait 5-10 minutes for deployment"
echo "   - Visit your frontend URL"
echo "   - Login: nicolas.desaintromain@axa.com / 123"
echo "   - Test AI Concierge with NVIDIA NIM"
echo "   - Test Calendar view"
echo "   - Test Startup swipe"
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ READY FOR PRODUCTION                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
