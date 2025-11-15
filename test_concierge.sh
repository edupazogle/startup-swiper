#!/bin/bash

echo "========================================"
echo "AI Concierge Test Script"
echo "========================================"
echo ""

BASE_URL="http://localhost:8000"

# Test 1: Basic question
echo "Test 1: Basic AI startups query"
echo "Question: What AI startups are there?"
curl -s -X POST $BASE_URL/concierge/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What AI startups are there?","user_context":{"user_id":"test1"}}' \
  | python3 -m json.tool | head -20
echo ""
echo "---"
echo ""

# Test 2: Location-based query
echo "Test 2: Location-based query"
echo "Question: Show me startups from Finland"
curl -s -X POST $BASE_URL/concierge/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Show me startups from Finland","user_context":{"user_id":"test2"}}' \
  | python3 -m json.tool | head -20
echo ""
echo "---"
echo ""

# Test 3: Industry query
echo "Test 3: Industry-specific query"
echo "Question: Tell me about healthtech startups"
curl -s -X POST $BASE_URL/concierge/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Tell me about healthtech startups","user_context":{"user_id":"test3"}}' \
  | python3 -m json.tool | head -20
echo ""
echo "---"
echo ""

echo "========================================"
echo "All tests completed!"
echo "========================================"
