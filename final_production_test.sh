#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║        FINAL PRODUCTION VERIFICATION - tilyn.ai                 ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0

# Test 1: Frontend
echo -n "1. Frontend Accessible........................... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://tilyn.ai/)
if [ "$STATUS" = "200" ]; then
    echo "✅ PASS"
    ((PASS++))
else
    echo "❌ FAIL (HTTP $STATUS)"
    ((FAIL++))
fi

# Test 2: API Health
echo -n "2. API Health Endpoint........................... "
HEALTH=$(curl -s https://tilyn.ai/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ PASS"
    ((PASS++))
else
    echo "❌ FAIL"
    ((FAIL++))
fi

# Test 3: API Docs
echo -n "3. API Documentation............................. "
DOCS=$(curl -s -o /dev/null -w "%{http_code}" https://tilyn.ai/docs)
if [ "$DOCS" = "200" ]; then
    echo "✅ PASS"
    ((PASS++))
else
    echo "❌ FAIL (HTTP $DOCS)"
    ((FAIL++))
fi

# Test 4: User Registration
echo -n "4. User Registration............................. "
REG=$(curl -s -X POST https://tilyn.ai/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email":"test'$(date +%s)'@test.com","password":"Test123Pass","username":"test'$(date +%s)'"}')
if echo "$REG" | grep -q '"id"'; then
    echo "✅ PASS"
    ((PASS++))
    USER_EMAIL=$(echo "$REG" | grep -o '"email":"[^"]*"' | cut -d'"' -f4)
    
    # Test 5: User Login
    echo -n "5. User Login.................................... "
    LOGIN=$(curl -s -X POST https://tilyn.ai/auth/login \
        -H 'Content-Type: application/json' \
        -d '{"email":"'$USER_EMAIL'","password":"Test123Pass"}')
    if echo "$LOGIN" | grep -q "access_token"; then
        echo "✅ PASS"
        ((PASS++))
    else
        echo "❌ FAIL"
        ((FAIL++))
    fi
else
    echo "❌ FAIL"
    ((FAIL++))
    echo -n "5. User Login.................................... "
    echo "⏭  SKIPPED"
fi

# Test 6: SSL Certificate
echo -n "6. SSL Certificate............................... "
if echo | openssl s_client -connect tilyn.ai:443 -servername tilyn.ai 2>/dev/null | grep -q "Verify return code: 0"; then
    echo "✅ PASS"
    ((PASS++))
else
    echo "❌ FAIL"
    ((FAIL++))
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                      TEST SUMMARY                                ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "  ✅ Passed: $PASS"
echo "  ❌ Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  🎉 PRODUCTION IS FULLY READY! 🎉                               ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "✅ All systems operational"
    echo "✅ Frontend deployed and accessible"
    echo "✅ API running and healthy"
    echo "✅ Authentication working"
    echo "✅ SSL/HTTPS enabled"
    echo ""
    echo "🌐 Production URLs:"
    echo "   • Frontend: https://tilyn.ai"
    echo "   • API Health: https://tilyn.ai/health"
    echo "   • API Docs: https://tilyn.ai/api/docs"
    echo ""
    echo "📝 Clear browser cache to see latest frontend:"
    echo "   • Press Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
    echo "   • Or open in Incognito/Private mode"
    echo ""
    exit 0
else
    echo "⚠️  Some tests failed. Check the output above."
    exit 1
fi
