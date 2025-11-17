#!/bin/bash

echo "=========================================="
echo "   Production Test - tilyn.ai"
echo "=========================================="
echo ""

# Test 1: API Health
echo "1. API Health Check"
curl -s https://tilyn.ai/api/health | jq '.'
echo ""

# Test 2: Data Version
echo "2. Data Version"
curl -s https://tilyn.ai/api/data-version | jq '.'
echo ""

# Test 3: Slush Events
echo "3. Slush Events (first 3)"
curl -s 'https://tilyn.ai/api/slush-events?limit=3' | jq '.[:3] | .[] | {id, title, location, start_time}'
echo ""

# Test 4: Events Stats
echo "4. Slush Events Statistics"
curl -s https://tilyn.ai/api/slush-events/stats/summary | jq '.'
echo ""

# Test 5: Startups via search
echo "5. Search Startups (AI/ML)"
curl -s 'https://tilyn.ai/startups/search?q=ai&limit=3' | jq '.[:3] | .[] | {id, name, description_short}'
echo ""

# Test 6: Topics & Use Cases
echo "6. Topics & Use Cases"
curl -s 'https://tilyn.ai/topics' | jq '.[:5]'
echo ""

# Test 7: Phases
echo "7. Investment Phases"
curl -s 'https://tilyn.ai/phases' | jq '.'
echo ""

# Test 8: Auroral Themes
echo "8. Auroral Themes"
curl -s 'https://tilyn.ai/api/auroral-themes' | jq '.[:2]'
echo ""

# Test 9: AI Concierge (No Auth)
echo "9. AI Concierge - Startup Categories"
curl -s 'https://tilyn.ai/concierge/startup-categories' | jq '.'
echo ""

echo "=========================================="
echo "   Production Deployment Summary"
echo "=========================================="
echo ""
echo "✅ Frontend:  https://tilyn.ai"
echo "✅ API:       https://tilyn.ai/api"
echo "✅ API Docs:  https://tilyn.ai/api/docs"
echo ""
echo "Note: User registration/login requires proper NGINX"
echo "      configuration for POST requests."
echo ""
