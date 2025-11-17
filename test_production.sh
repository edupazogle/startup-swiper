#!/bin/bash

echo "=========================================="
echo "Production Deployment Test - tilyn.ai"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test API Health
echo "1. Testing API Health..."
HEALTH=$(curl -s https://tilyn.ai/api/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ API is healthy${NC}"
    echo "$HEALTH" | jq '.'
else
    echo -e "${RED}✗ API health check failed${NC}"
    echo "$HEALTH"
fi
echo ""

# Test Frontend
echo "2. Testing Frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://tilyn.ai/)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Frontend is accessible (HTTP $FRONTEND_STATUS)${NC}"
else
    echo -e "${RED}✗ Frontend check failed (HTTP $FRONTEND_STATUS)${NC}"
fi
echo ""

# Test API Endpoints
echo "3. Testing API Endpoints..."

# Test startups endpoint
echo "   - Startups endpoint..."
STARTUPS=$(curl -s 'https://tilyn.ai/api/startups?limit=1')
if echo "$STARTUPS" | jq -e '.[0].id' > /dev/null 2>&1; then
    echo -e "     ${GREEN}✓ Startups endpoint working${NC}"
    echo "     Sample: $(echo "$STARTUPS" | jq -r '.[0].name' 2>/dev/null || echo 'N/A')"
else
    echo -e "     ${RED}✗ Startups endpoint failed${NC}"
fi

# Test phases endpoint
echo "   - Phases endpoint..."
PHASES=$(curl -s 'https://tilyn.ai/api/phases')
if echo "$PHASES" | jq -e 'length' > /dev/null 2>&1; then
    COUNT=$(echo "$PHASES" | jq 'length')
    echo -e "     ${GREEN}✓ Phases endpoint working ($COUNT phases)${NC}"
else
    echo -e "     ${RED}✗ Phases endpoint failed${NC}"
fi

# Test events endpoint
echo "   - Events endpoint..."
EVENTS=$(curl -s 'https://tilyn.ai/api/events?limit=1')
if echo "$EVENTS" | jq -e '.[0].id' > /dev/null 2>&1; then
    echo -e "     ${GREEN}✓ Events endpoint working${NC}"
    echo "     Sample: $(echo "$EVENTS" | jq -r '.[0].title' 2>/dev/null || echo 'N/A')"
else
    echo -e "     ${YELLOW}⚠ Events endpoint may be empty${NC}"
fi

echo ""

# Test Registration (create test user)
echo "4. Testing User Registration..."
TEST_EMAIL="test_$(date +%s)@example.com"
REGISTER_RESULT=$(curl -s -X POST 'https://tilyn.ai/api/register' \
    -H 'Content-Type: application/json' \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"TestPassword123!\",
        \"username\": \"test_user_$(date +%s)\"
    }")

if echo "$REGISTER_RESULT" | jq -e '.id' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ User registration working${NC}"
    USER_ID=$(echo "$REGISTER_RESULT" | jq -r '.id')
    USER_EMAIL=$(echo "$REGISTER_RESULT" | jq -r '.email')
    echo "   Created user: $USER_EMAIL (ID: $USER_ID)"
    
    # Test Login
    echo ""
    echo "5. Testing User Login..."
    LOGIN_RESULT=$(curl -s -X POST 'https://tilyn.ai/api/login' \
        -H 'Content-Type: application/json' \
        -d "{
            \"email\": \"$USER_EMAIL\",
            \"password\": \"TestPassword123!\"
        }")
    
    if echo "$LOGIN_RESULT" | jq -e '.access_token' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ User login working${NC}"
        ACCESS_TOKEN=$(echo "$LOGIN_RESULT" | jq -r '.access_token')
        echo "   Token obtained successfully"
        
        # Test authenticated endpoint
        echo ""
        echo "6. Testing Authenticated Endpoint..."
        ME_RESULT=$(curl -s 'https://tilyn.ai/api/auth/me' \
            -H "Authorization: Bearer $ACCESS_TOKEN")
        
        if echo "$ME_RESULT" | jq -e '.email' > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Authentication working${NC}"
            echo "   Logged in as: $(echo "$ME_RESULT" | jq -r '.email')"
        else
            echo -e "${RED}✗ Authentication failed${NC}"
        fi
    else
        echo -e "${RED}✗ User login failed${NC}"
        echo "$LOGIN_RESULT" | jq '.'
    fi
else
    echo -e "${YELLOW}⚠ User registration response:${NC}"
    echo "$REGISTER_RESULT" | jq '.'
fi

echo ""
echo "=========================================="
echo "✅ Production Deployment Tests Complete"
echo "=========================================="
echo ""
echo "Production URLs:"
echo "  Frontend: https://tilyn.ai"
echo "  API:      https://tilyn.ai/api"
echo "  API Docs: https://tilyn.ai/api/docs"
echo ""
