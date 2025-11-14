"""
Test script for LiteLLM integration with logging

This script tests the LLM endpoints and verifies that logs are being created.
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
LOGS_DIR = Path(__file__).parent / "logs" / "llm"

def test_simple_llm_call():
    """Test the simple LLM endpoint"""
    print("\n" + "="*60)
    print("Testing Simple LLM Call")
    print("="*60)
    
    payload = {
        "prompt": "Explain what a startup accelerator is in one sentence.",
        "model": "gpt-4o-mini",
        "temperature": 0.7
    }
    
    print(f"\nRequest: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/llm/simple", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Success!")
        print(f"Response: {result['content'][:200]}...")
        print(f"Model: {result['model']}")
    else:
        print(f"\n✗ Error {response.status_code}: {response.text}")
    
    return response.status_code == 200

def test_chat_llm_call():
    """Test the chat LLM endpoint"""
    print("\n" + "="*60)
    print("Testing Chat LLM Call")
    print("="*60)
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful startup advisor."},
            {"role": "user", "content": "What are the key metrics for a SaaS startup?"}
        ],
        "model": "gpt-4o-mini",
        "temperature": 0.7
    }
    
    print(f"\nRequest: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/llm/chat", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Success!")
        print(f"Response: {result['content'][:200]}...")
        print(f"Model: {result['model']}")
    else:
        print(f"\n✗ Error {response.status_code}: {response.text}")
    
    return response.status_code == 200

def test_with_system_message():
    """Test LLM call with system message"""
    print("\n" + "="*60)
    print("Testing LLM with System Message")
    print("="*60)
    
    payload = {
        "prompt": "Recommend 3 tools for a startup founder.",
        "model": "gpt-4o-mini",
        "system_message": "You are a concise startup advisor. Keep responses brief.",
        "temperature": 0.5
    }
    
    print(f"\nRequest: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/llm/simple", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Success!")
        print(f"Response: {result['content']}")
        print(f"Model: {result['model']}")
    else:
        print(f"\n✗ Error {response.status_code}: {response.text}")
    
    return response.status_code == 200

def check_logs():
    """Check if log files were created"""
    print("\n" + "="*60)
    print("Checking Log Files")
    print("="*60)
    
    if not LOGS_DIR.exists():
        print(f"\n✗ Logs directory not found: {LOGS_DIR}")
        return False
    
    log_files = list(LOGS_DIR.glob("*.json"))
    
    print(f"\n✓ Found {len(log_files)} log files in {LOGS_DIR}")
    
    if log_files:
        # Show the most recent log file
        latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
        print(f"\nMost recent log: {latest_log.name}")
        
        with open(latest_log, 'r') as f:
            log_data = json.load(f)
        
        print("\nLog contents:")
        print(json.dumps(log_data, indent=2)[:500] + "...")
        
        return True
    else:
        print("\n⚠ No log files found yet")
        return False

def main():
    print("="*60)
    print("LiteLLM Integration Test Suite")
    print("="*60)
    print(f"API URL: {BASE_URL}")
    print(f"Logs Directory: {LOGS_DIR}")
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"\n✓ API is running: {response.json()}")
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Cannot connect to API at {BASE_URL}")
        print("Please start the API with: uvicorn main:app --reload")
        return
    
    # Run tests
    results = []
    
    results.append(("Simple LLM Call", test_simple_llm_call()))
    time.sleep(1)
    
    results.append(("Chat LLM Call", test_chat_llm_call()))
    time.sleep(1)
    
    results.append(("LLM with System Message", test_with_system_message()))
    time.sleep(2)  # Give time for logs to be written
    
    results.append(("Log Files Created", check_logs()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
