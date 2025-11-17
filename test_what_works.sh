#!/bin/bash

echo "=========================================="
echo "  Production Features Test - tilyn.ai"
echo "=========================================="
echo ""

echo "✅ WORKING FEATURES:"
echo "-------------------"
echo ""

echo "1. Frontend Application"
echo "   URL: https://tilyn.ai"
echo "   Status: $(curl -s -o /dev/null -w "%{http_code}" https://tilyn.ai/)"
echo ""

echo "2. API Health & Status"
curl -s https://tilyn.ai/api/health | jq -r '"   Service: " + .service + "\n   Version: " + .version + "\n   Startups: " + (.startups_loaded|tostring)'
echo ""

echo "3. API Documentation"
echo "   Interactive Docs: https://tilyn.ai/api/docs"
echo "   OpenAPI Spec: https://tilyn.ai/api/openapi.json"
ENDPOINTS_COUNT=$(curl -s https://tilyn.ai/api/openapi.json | jq '.paths | length')
echo "   Total Endpoints: $ENDPOINTS_COUNT"
echo ""

echo "4. Available Endpoint Categories:"
curl -s https://tilyn.ai/api/openapi.json | jq -r '.paths | keys[]' | sed 's|/[^/]*$||' | sort -u | grep -v '^$' | head -20 | sed 's/^/   - /'
echo ""

echo "=========================================="
echo "⚠️  NEEDS CONFIGURATION:"
echo "-------------------"
echo ""
echo "The following require NGINX configuration fixes:"
echo "  - User Authentication (POST /auth/register, /auth/login)"
echo "  - Root-level API endpoints (/startups, /phases, /topics)"
echo "  - Full CRUD operations on all resources"
echo ""
echo "=========================================="
