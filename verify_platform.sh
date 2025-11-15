#!/bin/bash

###############################################################################
# Platform Verification Script
# Tests all key functionality of the Startup Swiper platform
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:5000"

passed=0
failed=0

test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Testing $name... "
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        ((passed++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code, expected $expected_code)"
        ((failed++))
        return 1
    fi
}

test_json_response() {
    local name=$1
    local url=$2
    local jq_query=${3:-'.'}
    
    echo -n "Testing $name... "
    response=$(curl -s "$url")
    
    if echo "$response" | jq -e "$jq_query" > /dev/null 2>&1; then
        result=$(echo "$response" | jq -r "$jq_query")
        echo -e "${GREEN}✓ PASS${NC} - Result: $result"
        ((passed++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} - Invalid JSON or query failed"
        ((failed++))
        return 1
    fi
}

echo ""
echo "=========================================="
echo "   Platform Verification Tests"
echo "=========================================="
echo ""

# API Health Tests
echo -e "${BLUE}=== API Health Tests ===${NC}"
test_endpoint "API Health" "$API_URL/health"
test_json_response "API Status" "$API_URL/health" '.status == "healthy"'
test_json_response "API Version" "$API_URL/health" '.version'
echo ""

# Database Tests
echo -e "${BLUE}=== Database Tests ===${NC}"
test_json_response "Startup Count" "$API_URL/startups/all?limit=1" '.total'
test_json_response "Enrichment Stats" "$API_URL/startups/enrichment/stats" '.total_startups'
test_json_response "Enrichment Percentage" "$API_URL/startups/enrichment/stats" '.enrichment_percentage'
echo ""

# Data Endpoints
echo -e "${BLUE}=== Data Endpoints ===${NC}"
test_endpoint "Get Startups" "$API_URL/startups/all?limit=5"
test_endpoint "Get Prioritized Startups" "$API_URL/startups/prioritized?limit=5"
test_endpoint "Calendar Events" "$API_URL/calendar-events/"
test_endpoint "Ideas" "$API_URL/ideas/"
test_endpoint "Auroral Themes" "$API_URL/api/auroral-themes"
echo ""

# Metadata Endpoints
echo -e "${BLUE}=== Metadata Endpoints ===${NC}"
test_endpoint "Current User" "$API_URL/api/current-user"
test_endpoint "Data Version" "$API_URL/api/data-version"
test_endpoint "Finished Users" "$API_URL/api/finished-users"
echo ""

# Frontend Tests
echo -e "${BLUE}=== Frontend Tests ===${NC}"
test_endpoint "Frontend Root" "$FRONTEND_URL"
echo -n "Testing Frontend Content... "
if curl -s "$FRONTEND_URL" | grep -q "Startup Rise"; then
    echo -e "${GREEN}✓ PASS${NC} - Frontend serving correctly"
    ((passed++))
else
    echo -e "${RED}✗ FAIL${NC} - Frontend content issue"
    ((failed++))
fi
echo ""

# Database Integration Tests
echo -e "${BLUE}=== Database Integration Tests ===${NC}"
echo -n "Testing Startup Retrieval... "
startup_data=$(curl -s "$API_URL/startups/all?limit=1")
if echo "$startup_data" | jq -e '.startups[0].id' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC} - Startups retrieved from DB"
    ((passed++))
else
    echo -e "${RED}✗ FAIL${NC} - Failed to retrieve startup data"
    ((failed++))
fi

echo -n "Testing Calendar Events... "
events_count=$(curl -s "$API_URL/calendar-events/" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
if [ "$events_count" -gt 0 ]; then
    echo -e "${GREEN}✓ PASS${NC} - $events_count events loaded"
    ((passed++))
else
    echo -e "${YELLOW}⚠ WARN${NC} - No events found"
    ((failed++))
fi

echo -n "Testing Ratings System... "
if curl -s "$API_URL/api/ratings/average" | jq -e '.ratings' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC} - Ratings endpoint working"
    ((passed++))
else
    echo -e "${RED}✗ FAIL${NC} - Ratings endpoint issue"
    ((failed++))
fi
echo ""

# Summary
echo "=========================================="
echo "           Test Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$passed${NC}"
echo -e "Failed: ${RED}$failed${NC}"
echo "Total:  $((passed + failed))"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Platform is ready for use:"
    echo "  - Frontend: $FRONTEND_URL"
    echo "  - API: $API_URL"
    echo "  - API Docs: $API_URL/docs"
    exit 0
else
    echo -e "${YELLOW}⚠ Some tests failed${NC}"
    echo "Check logs for details:"
    echo "  - API: logs/api.log"
    echo "  - Frontend: logs/frontend.log"
    exit 1
fi
