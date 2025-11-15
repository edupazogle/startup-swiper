#!/usr/bin/env python3
"""
Platform Verification Script
Tests all key endpoints and functionality
"""

import requests
import sys

API_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5000"

GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m'

passed = 0
failed = 0

def test(name, url, check_fn=None):
    global passed, failed
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            if check_fn:
                data = response.json() if 'json' in response.headers.get('content-type', '') else response.text
                result = check_fn(data)
                if result:
                    print(f"{GREEN}✓{NC} {name}: {result}")
                    passed += 1
                else:
                    print(f"{RED}✗{NC} {name}: Check failed")
                    failed += 1
            else:
                print(f"{GREEN}✓{NC} {name}")
                passed += 1
        else:
            print(f"{RED}✗{NC} {name}: HTTP {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"{RED}✗{NC} {name}: {e}")
        failed += 1

print("\n" + "="*50)
print("   Platform Verification")
print("="*50 + "\n")

# API Tests
print("API Tests:")
test("Health", f"{API_URL}/health", lambda d: d.get('status'))
test("Startups Count", f"{API_URL}/startups/all?limit=1", lambda d: f"{d.get('total')} startups")
test("Enrichment Stats", f"{API_URL}/startups/enrichment/stats", 
     lambda d: f"{d.get('enriched_count')} enriched ({d.get('enrichment_percentage')}%)")
test("Calendar Events", f"{API_URL}/calendar-events/", lambda d: f"{len(d)} events")
test("Current User", f"{API_URL}/api/current-user", lambda d: d.get('user_id'))
test("Data Version", f"{API_URL}/api/data-version", lambda d: d.get('version'))
test("Auroral Themes", f"{API_URL}/api/auroral-themes", lambda d: f"{len(d.get('themes', []))} themes")

# Frontend Test
print("\nFrontend Test:")
test("Frontend", FRONTEND_URL, lambda d: "Startup Rise" in d)

print("\n" + "="*50)
print(f"Results: {GREEN}{passed} passed{NC}, {RED}{failed} failed{NC}")
print("="*50)

if failed == 0:
    print(f"\n{GREEN}✓ All tests passed!{NC}\n")
    print("Platform is ready:")
    print(f"  Frontend: {FRONTEND_URL}")
    print(f"  API: {API_URL}")
    print(f"  API Docs: {API_URL}/docs")
    print()
    sys.exit(0)
else:
    print(f"\n{RED}✗ Some tests failed{NC}\n")
    sys.exit(1)
