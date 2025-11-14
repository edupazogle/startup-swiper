#!/usr/bin/env python3
"""
Test Enriched Data API Endpoints
Verify all new endpoints work correctly
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_enrichment_stats():
    """Test 1: Get enrichment statistics"""
    print_section("Test 1: Enrichment Statistics")
    
    try:
        response = requests.get(f"{BASE_URL}/startups/enrichment/stats")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"\nDatabase Stats:")
        print(f"  Total Startups:   {data['total_startups']}")
        print(f"  Enriched:         {data['enriched_count']}")
        print(f"  Completion:       {data['enrichment_percentage']:.1f}%")
        print(f"\nField Coverage:")
        for field, count in data['fields_available'].items():
            print(f"  {field.replace('_', ' ').title()}: {count}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_search_enriched():
    """Test 2: Search enriched startups"""
    print_section("Test 2: Search Enriched Startups")
    
    try:
        # Search with enrichment filter
        response = requests.get(
            f"{BASE_URL}/startups/enriched/search",
            params={
                "enrichment_type": "tech_stack",
                "limit": 5
            }
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"Found {data['count']} startups with tech stack enrichment\n")
        
        for i, startup in enumerate(data['results'][:3], 1):
            print(f"{i}. {startup['name']}")
            print(f"   Website: {startup['website']}")
            if startup['enrichment'].get('tech_stack'):
                print(f"   Tech: {', '.join(startup['enrichment']['tech_stack'][:3])}")
            print()
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_get_startup_enrichment():
    """Test 3: Get specific startup enrichment"""
    print_section("Test 3: Get Specific Startup Enrichment")
    
    try:
        # First, find an enriched startup
        response = requests.get(
            f"{BASE_URL}/startups/enriched/search",
            params={"limit": 1}
        )
        response.raise_for_status()
        
        results = response.json()['results']
        if not results:
            print("✗ No enriched startups found")
            return False
        
        startup_id = results[0]['id']
        
        # Get full enrichment
        response = requests.get(f"{BASE_URL}/startups/{startup_id}/enrichment")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"\nStartup: {data['startup_name']}")
        print(f"Website: {data['website']}")
        
        enrichment = data['enrichment']
        
        if enrichment.get('emails'):
            print(f"\n📧 Emails ({len(enrichment['emails'])}):")
            for email in enrichment['emails'][:3]:
                print(f"   {email}")
        
        if enrichment.get('social_media'):
            print(f"\n🌐 Social Media:")
            for platform, url in list(enrichment['social_media'].items())[:3]:
                print(f"   {platform}: {url[:50]}...")
        
        if enrichment.get('tech_stack'):
            print(f"\n💻 Tech Stack ({len(enrichment['tech_stack'])}):")
            print(f"   {', '.join(enrichment['tech_stack'][:5])}")
        
        if enrichment.get('team_members'):
            print(f"\n👥 Team ({len(enrichment['team_members'])}):")
            for member in enrichment['team_members'][:3]:
                print(f"   {member}")
        
        print(f"\n⏰ Last Enriched: {data['last_enriched']}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_search_by_field():
    """Test 4: Search by enriched field"""
    print_section("Test 4: Search by Enriched Field")
    
    try:
        # Search by technology
        response = requests.post(
            f"{BASE_URL}/startups/enrichment/by-name",
            json={
                "field_name": "tech",
                "field_value": "React",
                "limit": 5
            }
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"Found {data['count']} startups using: {data['search_value']}\n")
        
        for i, startup in enumerate(data['results'][:5], 1):
            print(f"{i}. {startup['name']}")
            print(f"   {startup['website']}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_search_by_email():
    """Test 5: Search by email domain"""
    print_section("Test 5: Search by Email Domain")
    
    try:
        response = requests.post(
            f"{BASE_URL}/startups/enrichment/by-name",
            json={
                "field_name": "email",
                "field_value": "@",  # Any email
                "limit": 5
            }
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"Found {data['count']} startups with emails\n")
        
        for i, startup in enumerate(data['results'][:5], 1):
            print(f"{i}. {startup['name']}")
            print(f"   {startup['website']}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_full_workflow():
    """Test 6: Complete workflow"""
    print_section("Test 6: Complete Workflow")
    
    try:
        # Step 1: Get stats
        print("1️⃣ Getting enrichment statistics...")
        response = requests.get(f"{BASE_URL}/startups/enrichment/stats")
        stats = response.json()
        enriched_count = stats['enriched_count']
        print(f"   ✓ {enriched_count} enriched startups found")
        
        # Step 2: Search by tech
        print("\n2️⃣ Searching for startups using Python...")
        response = requests.post(
            f"{BASE_URL}/startups/enrichment/by-name",
            json={"field_name": "tech", "field_value": "Python", "limit": 1}
        )
        results = response.json()['results']
        if results:
            startup_id = results[0]['id']
            startup_name = results[0]['name']
            print(f"   ✓ Found: {startup_name}")
            
            # Step 3: Get full enrichment
            print("\n3️⃣ Getting full enrichment data...")
            response = requests.get(f"{BASE_URL}/startups/{startup_id}/enrichment")
            enrichment_data = response.json()
            print(f"   ✓ Retrieved enrichment for {enrichment_data['startup_name']}")
            
            # Step 4: Display results
            print("\n4️⃣ Enrichment Summary:")
            enrichment = enrichment_data['enrichment']
            print(f"   📧 Emails: {len(enrichment.get('emails', []))} found")
            print(f"   🌐 Social: {len(enrichment.get('social_media', {}))} platforms")
            print(f"   💻 Tech: {len(enrichment.get('tech_stack', []))} technologies")
            print(f"   👥 Team: {len(enrichment.get('team_members', []))} members")
            
            print("\n✓ Complete workflow successful!")
            return True
        else:
            print("   ✗ No results found")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  ENRICHED DATA API TEST SUITE")
    print("="*60)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("\n✗ API returned unexpected status code")
            print("Make sure the API is running: uvicorn api/main:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to API at", BASE_URL)
        print("Start the API with: source .venv/bin/activate && uvicorn api/main:app --reload")
        return
    
    print("✓ API is running\n")
    
    # Run tests
    tests = [
        ("Enrichment Stats", test_enrichment_stats),
        ("Search Enriched", test_search_enriched),
        ("Get Enrichment", test_get_startup_enrichment),
        ("Search by Field", test_search_by_field),
        ("Search by Email", test_search_by_email),
        ("Full Workflow", test_full_workflow),
    ]
    
    results = []
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! API is ready for production.")
        print("\nNext steps:")
        print("  1. Integrate with React frontend")
        print("  2. Add enriched data display to startup cards")
        print("  3. Create search/filter by enriched fields")
        print("  4. Continue enriching remaining startups")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")

if __name__ == "__main__":
    main()
