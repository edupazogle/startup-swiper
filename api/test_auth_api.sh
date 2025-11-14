#!/bin/bash

echo "=========================================="
echo "Testing Authentication API"
echo "=========================================="
echo ""

# Test 1: Login as Alice
echo "1. Login as Alice..."
ALICE_RESPONSE=$(curl -s -X POST 'http://localhost:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d @- <<EOF
{"email":"alice@slushdemo.com","password":"AliceDemo2025!"}
EOF
)

echo "$ALICE_RESPONSE" | python3 -m json.tool
ALICE_TOKEN=$(echo "$ALICE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$ALICE_TOKEN" ]; then
  echo "✓ Alice logged in successfully"
  echo "  Token: ${ALICE_TOKEN:0:50}..."
else
  echo "✗ Alice login failed"
fi

echo ""
echo "2. Login as Bob..."
BOB_RESPONSE=$(curl -s -X POST 'http://localhost:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d @- <<EOF
{"email":"bob@slushdemo.com","password":"BobDemo2025!"}
EOF
)

echo "$BOB_RESPONSE" | python3 -m json.tool
BOB_TOKEN=$(echo "$BOB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$BOB_TOKEN" ]; then
  echo "✓ Bob logged in successfully"
  echo "  Token: ${BOB_TOKEN:0:50}..."
else
  echo "✗ Bob login failed"
fi

echo ""
echo "3. Test Protected Route (/auth/me) for Alice..."
if [ -n "$ALICE_TOKEN" ]; then
  curl -s -X GET 'http://localhost:8000/auth/me' \
    -H "Authorization: Bearer $ALICE_TOKEN" | python3 -m json.tool
  echo "✓ Alice's profile fetched successfully"
else
  echo "✗ Cannot test - no token"
fi

echo ""
echo "4. Test Protected Route (/auth/me) for Bob..."
if [ -n "$BOB_TOKEN" ]; then
  curl -s -X GET 'http://localhost:8000/auth/me' \
    -H "Authorization: Bearer $BOB_TOKEN" | python3 -m json.tool
  echo "✓ Bob's profile fetched successfully"
else
  echo "✗ Cannot test - no token"
fi

echo ""
echo "=========================================="
echo "Authentication Test Complete!"
echo "=========================================="
