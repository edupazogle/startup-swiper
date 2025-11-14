"""
AI Concierge Testing Script

This script tests all the AI Concierge functionality including:
- Startup queries
- Event information
- Directions
- General Q&A
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_response(response):
    """Print formatted API response"""
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and "answer" in data:
            print(f"✓ Answer:\n{data['answer']}\n")
            if "question_type" in data:
                print(f"Question Type: {data['question_type']}")
        else:
            print(f"✓ Response:\n{json.dumps(data, indent=2)}\n")
    else:
        print(f"✗ Error {response.status_code}: {response.text}\n")

def test_startup_questions():
    """Test startup-related questions"""
    print_section("Testing Startup Questions")
    
    questions = [
        "Tell me about 759 Studio",
        "What startups are in the AI category?",
        "Which startups have raised the most funding?",
        "Find me fintech startups",
        "What is the average funding for startups at Slush?"
    ]
    
    for question in questions:
        print(f"Q: {question}")
        response = requests.post(
            f"{BASE_URL}/concierge/ask",
            json={"question": question}
        )
        print_response(response)
        time.sleep(1)

def test_event_questions():
    """Test event-related questions"""
    print_section("Testing Event Questions")
    
    questions = [
        "What events are happening today?",
        "Tell me about the keynote sessions",
        "When is the networking event?",
        "Show me all the workshops",
        "What's on the main stage?"
    ]
    
    for question in questions:
        print(f"Q: {question}")
        response = requests.post(
            f"{BASE_URL}/concierge/ask",
            json={"question": question}
        )
        print_response(response)
        time.sleep(1)

def test_directions():
    """Test directions functionality"""
    print_section("Testing Directions")
    
    # Test with specific locations
    directions_request = {
        "origin": "Helsinki Central Station",
        "destination": "Messukeskus Helsinki",
        "mode": "walking"
    }
    
    print(f"Getting directions from {directions_request['origin']} to {directions_request['destination']}")
    response = requests.post(
        f"{BASE_URL}/concierge/directions",
        json=directions_request
    )
    print_response(response)
    
    # Test with question format
    print("\nQ: How do I get to the main venue from downtown Helsinki?")
    response = requests.post(
        f"{BASE_URL}/concierge/ask",
        json={"question": "How do I get to Messukeskus Helsinki from Helsinki Central Station?"}
    )
    print_response(response)

def test_startup_search():
    """Test startup search functionality"""
    print_section("Testing Startup Search")
    
    queries = [
        ("AI", 5),
        ("sustainable", 3),
        ("fintech", 5)
    ]
    
    for query, limit in queries:
        print(f"Searching for: '{query}' (limit: {limit})")
        response = requests.get(
            f"{BASE_URL}/concierge/search-startups",
            params={"query": query, "limit": limit}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data['count']} startups")
            for startup in data['results'][:3]:
                print(f"  - {startup.get('name')}: {startup.get('shortDescription', 'N/A')[:80]}...")
        else:
            print(f"✗ Error: {response.status_code}")
        print()
        time.sleep(0.5)

def test_startup_details():
    """Test detailed startup information"""
    print_section("Testing Detailed Startup Information")
    
    startup_names = [
        "759 Studio",
        # Add more startup names from your data
    ]
    
    for name in startup_names:
        print(f"Getting details for: {name}")
        response = requests.post(
            f"{BASE_URL}/concierge/startup-details",
            json={"startup_name": name}
        )
        print_response(response)
        time.sleep(1)

def test_attendee_questions():
    """Test attendee-related questions"""
    print_section("Testing Attendee Questions")
    
    questions = [
        "Who is attending the event?",
        "How many people are registered?",
        "Are there any VIPs attending?",
        "Who should I network with?"
    ]
    
    for question in questions:
        print(f"Q: {question}")
        response = requests.post(
            f"{BASE_URL}/concierge/ask",
            json={"question": question}
        )
        print_response(response)
        time.sleep(1)

def test_meeting_questions():
    """Test meeting-related questions"""
    print_section("Testing Meeting Questions")
    
    questions = [
        "What meetings do I have scheduled?",
        "Who am I meeting with today?",
        "When is my next meeting?",
        "Show me all scheduled meetings"
    ]
    
    for question in questions:
        print(f"Q: {question}")
        response = requests.post(
            f"{BASE_URL}/concierge/ask",
            json={"question": question}
        )
        print_response(response)
        time.sleep(1)

def test_complex_questions():
    """Test complex multi-part questions"""
    print_section("Testing Complex Questions")
    
    questions = [
        "I'm interested in sustainable tech startups. Which ones should I meet and when are they presenting?",
        "Compare the top 3 AI startups at the event",
        "What are the best networking opportunities for fintech founders?",
        "I need to get from my hotel to the morning keynote. How long will it take and what route should I use?",
        "Which startups have raised over $5M and are in the B2B SaaS space?"
    ]
    
    for question in questions:
        print(f"Q: {question}")
        response = requests.post(
            f"{BASE_URL}/concierge/ask",
            json={
                "question": question,
                "user_context": {
                    "interests": ["AI", "fintech", "sustainability"],
                    "role": "investor"
                }
            }
        )
        print_response(response)
        time.sleep(2)

def test_category_search():
    """Test startup category search"""
    print_section("Testing Category Search")
    
    categories = ["AI", "Fintech", "Healthcare", "Sustainability"]
    
    for category in categories:
        print(f"Category: {category}")
        response = requests.get(
            f"{BASE_URL}/concierge/startup-categories",
            params={"category": category, "limit": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data['count']} startups in {data['category']}")
            for startup in data['results'][:3]:
                print(f"  - {startup.get('name')}")
        else:
            print(f"✗ Error: {response.status_code}")
        print()
        time.sleep(0.5)

def check_api_health():
    """Check if API is running"""
    print_section("Checking API Health")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print("✓ API is running")
            print(f"  Message: {data.get('message')}")
            print(f"  Version: {data.get('version')}")
            if 'features' in data:
                print("  Features:")
                for feature in data['features']:
                    print(f"    - {feature}")
            return True
        else:
            print(f"✗ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to API at {BASE_URL}")
        print("Please start the API with: uvicorn main:app --reload")
        return False

def main():
    """Run all tests"""
    print("="*70)
    print("  AI CONCIERGE TEST SUITE")
    print("="*70)
    print(f"Testing API at: {BASE_URL}")
    print()
    
    # Check API health first
    if not check_api_health():
        return
    
    print("\n⏳ Starting tests in 2 seconds...\n")
    time.sleep(2)
    
    # Run all test suites
    test_suites = [
        ("Startup Questions", test_startup_questions),
        ("Event Questions", test_event_questions),
        ("Startup Search", test_startup_search),
        ("Startup Details", test_startup_details),
        ("Directions", test_directions),
        ("Attendee Questions", test_attendee_questions),
        ("Meeting Questions", test_meeting_questions),
        ("Category Search", test_category_search),
        ("Complex Questions", test_complex_questions),
    ]
    
    results = []
    
    for suite_name, suite_func in test_suites:
        try:
            suite_func()
            results.append((suite_name, "✓ PASS"))
        except Exception as e:
            print(f"\n✗ Error in {suite_name}: {e}\n")
            results.append((suite_name, f"✗ FAIL: {e}"))
    
    # Print summary
    print_section("TEST SUMMARY")
    for suite_name, result in results:
        print(f"{result}: {suite_name}")
    
    passed = sum(1 for _, r in results if "PASS" in r)
    total = len(results)
    
    print(f"\n{'='*70}")
    print(f"  Total: {passed}/{total} test suites passed")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
