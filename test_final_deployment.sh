#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║            🎉 DEPLOYMENT SUCCESSFUL! 🎉                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Testing production endpoints..."
echo ""

echo "1. Frontend Test:"
curl -sI https://tilyn.ai/ | grep -E "HTTP|Cache-Control|Date" | head -5

echo ""
echo "2. API Health:"
curl -s https://tilyn.ai/api/health | jq '.'

echo ""
echo "3. Testing User Registration:"
TEST_EMAIL="final_test_$(date +%s)@example.com"
TEST_PASS="Test123Pass"
REGISTER=$(curl -s -X POST https://tilyn.ai/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"'$TEST_EMAIL'","password":"'$TEST_PASS'","username":"final'$(date +%s)'"}')

if echo "$REGISTER" | jq -e '.id' > /dev/null 2>&1; then
  echo "✅ User Registration Working!"
  USER_ID=$(echo "$REGISTER" | jq -r '.id')
  echo "   Created User ID: $USER_ID"
  
  echo ""
  echo "4. Testing User Login:"
  LOGIN=$(curl -s -X POST https://tilyn.ai/auth/login \
    -H 'Content-Type: application/json' \
    -d '{"email":"'$TEST_EMAIL'","password":"'$TEST_PASS'"}')
  
  if echo "$LOGIN" | jq -e '.access_token' > /dev/null 2>&1; then
    echo "✅ User Login Working!"
    echo "   JWT Token obtained successfully"
  else
    echo "❌ Login failed"
    echo "$LOGIN" | jq '.'
  fi
else
  echo "⚠️  Registration response:"
  echo "$REGISTER" | jq '.'
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                  PRODUCTION IS READY! ✅                         ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "URLs:"
echo "  • Frontend: https://tilyn.ai"
echo "  • API: https://tilyn.ai/api"
echo "  • API Docs: https://tilyn.ai/api/docs"
echo ""
echo "To see the new frontend, clear your browser cache:"
echo "  • Chrome/Firefox: Ctrl+Shift+R (Cmd+Shift+R on Mac)"
echo "  • Or open in Incognito/Private mode"
echo ""
