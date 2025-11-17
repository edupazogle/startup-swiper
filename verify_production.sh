#!/bin/bash

###############################################################################
# Production Readiness Verification Script
# Tests all critical functionality on production
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

test_warning() {
    echo -e "${YELLOW}⚠ WARNING${NC}"
    ((WARNINGS++))
}

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        Production Readiness Verification - tilyn.ai         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Frontend Accessibility
echo -n "1. Frontend Accessible (HTTPS)........................ "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://tilyn.ai/ 2>/dev/null || echo "000")
if [ "$STATUS" = "200" ]; then
    test_result 0
else
    test_result 1
    echo "   Status code: $STATUS"
fi

# Test 2: API Health
echo -n "2. API Health Check................................... "
HEALTH=$(curl -s https://tilyn.ai/api/health 2>/dev/null)
if echo "$HEALTH" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    test_result 0
    STARTUP_COUNT=$(echo "$HEALTH" | jq -r '.startups_loaded')
    echo "   Startups loaded: $STARTUP_COUNT"
else
    test_result 1
fi

# Test 3: API Documentation
echo -n "3. API Documentation Accessible....................... "
DOC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://tilyn.ai/api/docs 2>/dev/null || echo "000")
if [ "$DOC_STATUS" = "200" ]; then
    test_result 0
else
    test_result 1
fi

# Test 4: User Registration
echo -n "4. User Registration (POST)........................... "
TEST_EMAIL="verify_$(date +%s)@test.com"
REGISTER=$(curl -s -X POST https://tilyn.ai/auth/register \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"Test123!Pass\",\"username\":\"test_$(date +%s)\"}" 2>/dev/null)

if echo "$REGISTER" | jq -e '.id' > /dev/null 2>&1; then
    test_result 0
    USER_ID=$(echo "$REGISTER" | jq -r '.id')
    echo "   Created user ID: $USER_ID"
    
    # Test 5: User Login
    echo -n "5. User Login (JWT)................................... "
    LOGIN=$(curl -s -X POST https://tilyn.ai/auth/login \
        -H 'Content-Type: application/json' \
        -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"Test123!Pass\"}" 2>/dev/null)
    
    if echo "$LOGIN" | jq -e '.access_token' > /dev/null 2>&1; then
        test_result 0
        TOKEN=$(echo "$LOGIN" | jq -r '.access_token')
        
        # Test 6: Authenticated Endpoint
        echo -n "6. Authenticated Endpoint (/auth/me).................. "
        ME=$(curl -s https://tilyn.ai/auth/me \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$ME" | jq -e '.email' > /dev/null 2>&1; then
            test_result 0
        else
            test_result 1
        fi
    else
        test_result 1
        echo -n "6. Authenticated Endpoint (/auth/me).................. "
        echo -e "${YELLOW}SKIPPED${NC}"
        ((WARNINGS++))
    fi
else
    test_result 1
    echo "   Response: $REGISTER"
    echo -n "5. User Login (JWT)................................... "
    echo -e "${YELLOW}SKIPPED${NC}"
    echo -n "6. Authenticated Endpoint (/auth/me).................. "
    echo -e "${YELLOW}SKIPPED${NC}"
    ((WARNINGS+=2))
fi

# Test 7: Slush Events
echo -n "7. Slush Events API................................... "
EVENTS=$(curl -s 'https://tilyn.ai/api/slush-events?limit=1' 2>/dev/null)
if echo "$EVENTS" | jq -e '.[0].id' > /dev/null 2>&1; then
    test_result 0
    EVENT_TITLE=$(echo "$EVENTS" | jq -r '.[0].title')
    echo "   Sample: $EVENT_TITLE"
else
    test_warning
    echo "   No events found (not critical)"
fi

# Test 8: Concierge AI
echo -n "8. AI Concierge (Startup Categories).................. "
CATEGORIES=$(curl -s https://tilyn.ai/concierge/startup-categories 2>/dev/null)
if echo "$CATEGORIES" | jq -e 'length > 0' > /dev/null 2>&1; then
    test_result 0
else
    test_result 1
fi

# Test 9: SSL Certificate
echo -n "9. SSL Certificate Valid.............................. "
SSL_EXPIRY=$(echo | openssl s_client -servername tilyn.ai -connect tilyn.ai:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep "notAfter" | cut -d= -f2)
if [ -n "$SSL_EXPIRY" ]; then
    test_result 0
    echo "   Expires: $SSL_EXPIRY"
else
    test_result 1
fi

# Test 10: Response Time
echo -n "10. API Response Time (<2s)........................... "
START_TIME=$(date +%s%N)
curl -s https://tilyn.ai/api/health > /dev/null 2>&1
END_TIME=$(date +%s%N)
DURATION=$(( (END_TIME - START_TIME) / 1000000 ))
if [ $DURATION -lt 2000 ]; then
    test_result 0
    echo "   Response time: ${DURATION}ms"
else
    test_warning
    echo "   Response time: ${DURATION}ms (slow)"
fi

# Test 11: CORS Headers
echo -n "11. CORS Headers Present.............................. "
CORS=$(curl -s -I https://tilyn.ai/api/health 2>/dev/null | grep -i "access-control-allow-origin")
if [ -n "$CORS" ]; then
    test_result 0
else
    test_result 1
fi

# Test 12: Compression Enabled
echo -n "12. GZIP Compression Enabled.......................... "
GZIP=$(curl -s -I -H "Accept-Encoding: gzip" https://tilyn.ai/ 2>/dev/null | grep -i "content-encoding: gzip")
if [ -n "$GZIP" ]; then
    test_result 0
else
    test_warning
fi

# Test 13: PWA Manifest
echo -n "13. PWA Manifest Available............................ "
MANIFEST_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://tilyn.ai/manifest.json 2>/dev/null || echo "000")
if [ "$MANIFEST_STATUS" = "200" ]; then
    test_result 0
else
    test_warning
fi

# Test 14: Service Worker
echo -n "14. Service Worker Available.......................... "
SW_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://tilyn.ai/sw.js 2>/dev/null || echo "000")
if [ "$SW_STATUS" = "200" ]; then
    test_result 0
else
    test_warning
fi

# Test 15: API Error Handling
echo -n "15. API Error Handling (404).......................... "
ERROR_404=$(curl -s https://tilyn.ai/api/nonexistent 2>/dev/null)
if echo "$ERROR_404" | jq -e '.detail' > /dev/null 2>&1; then
    test_result 0
else
    test_result 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                      Test Summary                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "  ${GREEN}Passed:${NC}   $PASSED"
echo -e "  ${RED}Failed:${NC}   $FAILED"
echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ PRODUCTION READY - All tests passed!           ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
    exit 0
elif [ $PERCENTAGE -ge 80 ]; then
    echo -e "${YELLOW}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠ MOSTLY READY - Some issues need attention      ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════╝${NC}"
    exit 1
else
    echo -e "${RED}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ NOT READY - Critical issues must be fixed      ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════╝${NC}"
    exit 2
fi
