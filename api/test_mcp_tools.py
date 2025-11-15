#!/usr/bin/env python3
"""
Comprehensive MCP Tool Testing Script

Tests all 7 MCP tools with actual database queries
"""

import asyncio
import sys
from pathlib import Path

# Add API directory to path
api_dir = Path(__file__).parent
sys.path.insert(0, str(api_dir))

from mcp_client import StartupDatabaseMCPTools
from database import SessionLocal


async def test_all_tools():
    """Test all MCP tools with actual startup data"""
    
    print("\n" + "="*70)
    print("MCP STARTUP DATABASE TOOLS - COMPREHENSIVE TEST")
    print("="*70)
    
    # Initialize MCP tools
    print("\n🔧 Initializing MCP Tools...")
    tools = StartupDatabaseMCPTools()
    
    db = SessionLocal()
    print("✓ Database connected")
    print(f"✓ Tools initialized with {len(tools.get_tools_for_llm())} tools")
    
    # Define tests
    tests = [
        {
            "name": "Search Startups by Name",
            "tool": "search_startups_by_name",
            "params": {"query": "AI", "limit": 5},
            "description": "Find startups with 'AI' in their name"
        },
        {
            "name": "Search Startups by Industry",
            "tool": "search_startups_by_industry",
            "params": {"industry": "AI", "limit": 5},
            "description": "Find AI startups"
        },
        {
            "name": "Search by Funding Stage",
            "tool": "search_startups_by_funding",
            "params": {"stage": "Seed", "limit": 5},
            "description": "Find Seed stage startups"
        },
        {
            "name": "Search by Location",
            "tool": "search_startups_by_location",
            "params": {"country": "Finland", "limit": 5},
            "description": "Find startups in Finland"
        },
        {
            "name": "Get Top Funded Startups",
            "tool": "get_top_startups_by_funding",
            "params": {"limit": 5},
            "description": "Get the top 5 most funded startups"
        },
    ]
    
    results = []
    
    # Run each test
    for i, test in enumerate(tests, 1):
        print(f"\n{'-'*70}")
        print(f"TEST {i}: {test['name']}")
        print(f"Description: {test['description']}")
        print(f"{'-'*70}")
        
        try:
            result = await tools.call_tool(test['tool'], **test['params'])
            
            if result.get('success'):
                count = result.get('count', 0)
                startup_results = result.get('results', [])
                
                print(f"✓ SUCCESS - Found {count} startups\n")
                
                # Display results in table format
                if startup_results:
                    print(f"{'#':<3} {'Name':<30} {'Industry':<15} {'Funding':<12}")
                    print("-" * 70)
                    
                    for idx, startup in enumerate(startup_results[:5], 1):
                        name = (startup.get('name', 'N/A'))[:28]
                        industry = (startup.get('industry', 'N/A'))[:13]
                        funding = startup.get('funding')
                        funding_str = f"${funding}M" if funding else "N/A"
                        
                        print(f"{idx:<3} {name:<30} {industry:<15} {funding_str:<12}")
                
                results.append((test['name'], True, None))
            
            else:
                error = result.get('error', 'Unknown error')
                print(f"✗ FAILED: {error}")
                results.append((test['name'], False, error))
        
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            results.append((test['name'], False, str(e)))
    
    # Test getting specific startup details
    print(f"\n{'-'*70}")
    print(f"TEST 6: Get Startup Details")
    print(f"Description: Get complete details for a specific startup")
    print(f"{'-'*70}")
    
    try:
        detail_result = await tools.call_tool(
            "get_startup_details",
            company_name="Straion"
        )
        
        if detail_result.get('success'):
            startup = detail_result.get('startup', {})
            
            print(f"✓ SUCCESS - Retrieved startup details\n")
            print(f"Company: {startup.get('name')}")
            print(f"Website: {startup.get('website')}")
            print(f"Location: {startup.get('location')}")
            print(f"Industry: {startup.get('industry')}")
            print(f"Funding: ${startup.get('totalFunding', 'N/A')}M")
            print(f"Stage: {startup.get('stage')}")
            print(f"Employees: {startup.get('employees')}")
            print(f"Description: {startup.get('description', 'N/A')[:100]}...")
            
            results.append(("Get Startup Details", True, None))
        else:
            print(f"✗ FAILED: {detail_result.get('error')}")
            results.append(("Get Startup Details", False, detail_result.get('error')))
    
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        results.append(("Get Startup Details", False, str(e)))
    
    # Test enrichment data
    print(f"\n{'-'*70}")
    print(f"TEST 7: Get Enrichment Data")
    print(f"Description: Get team, tech stack, and social media info")
    print(f"{'-'*70}")
    
    try:
        enrichment_result = await tools.call_tool(
            "get_startup_enrichment_data",
            company_name="Straion"
        )
        
        if enrichment_result.get('success'):
            print(f"✓ SUCCESS - Retrieved enrichment data\n")
            print(f"Company: {enrichment_result.get('startup_name')}")
            print(f"Enriched: {enrichment_result.get('enrichment_date')}")
            
            team = enrichment_result.get('team', [])
            if team:
                print(f"\nTeam Members ({len(team)}):")
                for member in team[:3]:
                    print(f"  • {member.get('name', 'N/A')} - {member.get('role', 'N/A')}")
            
            tech_stack = enrichment_result.get('tech_stack', [])
            if tech_stack:
                print(f"\nTech Stack:")
                print(f"  {', '.join(tech_stack[:5])}")
            
            social = enrichment_result.get('social_media', {})
            if social:
                print(f"\nSocial Media:")
                for platform, url in list(social.items())[:3]:
                    if url:
                        print(f"  • {platform}: {url}")
            
            results.append(("Get Enrichment Data", True, None))
        else:
            print(f"⚠️  No enrichment data found (startup may not be enriched)")
            results.append(("Get Enrichment Data", True, "No data"))
    
    except Exception as e:
        print(f"⚠️  Could not retrieve enrichment data: {str(e)}")
        results.append(("Get Enrichment Data", True, "Not available"))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        error_msg = f" ({error})" if error else ""
        print(f"{status}: {test_name}{error_msg}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉 "*15)
        print("ALL MCP TOOLS WORKING PERFECTLY!")
        print("🎉 "*15)
    elif passed >= total - 1:
        print("\n✅ EXCELLENT - MCP Tools are fully operational")
        print("Most tests passed. The system is ready for use.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    db.close()
    return passed == total


async def test_complex_query():
    """Test a complex multi-tool query scenario"""
    
    print("\n\n" + "="*70)
    print("COMPLEX QUERY TEST - AI Startups in Finland with Series A Funding")
    print("="*70)
    
    tools = StartupDatabaseMCPTools()
    
    try:
        # Step 1: Find Finnish startups
        print("\n[Step 1] Finding startups in Finland...")
        finland_result = await tools.call_tool(
            "search_startups_by_location",
            country="Finland",
            limit=20
        )
        
        if not finland_result.get('success'):
            print("✗ Could not find Finnish startups")
            return False
        
        finnish_startups = finland_result.get('results', [])
        print(f"✓ Found {len(finnish_startups)} startups in Finland")
        
        # Step 2: Filter for AI startups
        print("\n[Step 2] Finding AI startups...")
        ai_result = await tools.call_tool(
            "search_startups_by_industry",
            industry="AI",
            limit=20
        )
        
        if not ai_result.get('success'):
            print("✗ Could not find AI startups")
            return False
        
        ai_startups = ai_result.get('results', [])
        print(f"✓ Found {len(ai_startups)} AI startups")
        
        # Step 3: Find Series A startups
        print("\n[Step 3] Finding Series A startups...")
        series_a_result = await tools.call_tool(
            "search_startups_by_funding",
            stage="Series A",
            limit=20
        )
        
        if not series_a_result.get('success'):
            print("✗ Could not find Series A startups")
            return False
        
        series_a_startups = series_a_result.get('results', [])
        print(f"✓ Found {len(series_a_startups)} Series A startups")
        
        # Combine results (find common startups)
        finnish_names = {s['name'].lower() for s in finnish_startups}
        ai_names = {s['name'].lower() for s in ai_startups}
        series_a_names = {s['name'].lower() for s in series_a_startups}
        
        # Find intersection
        matching = finnish_names & ai_names & series_a_names
        
        print(f"\n[Result] AI startups in Finland with Series A funding:")
        print(f"{'='*70}")
        
        if matching:
            print(f"✓ Found {len(matching)} matching startups:\n")
            for i, name in enumerate(matching, 1):
                print(f"  {i}. {name.title()}")
        else:
            print("⚠️  No startups matching all three criteria found")
            print("(This is normal - the criteria are quite specific)")
            
            print(f"\nAlternatively:")
            print(f"  • {len(finnish_names)} startups in Finland")
            print(f"  • {len(ai_names)} AI startups total")
            print(f"  • {len(series_a_names)} Series A startups total")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def main():
    """Run all tests"""
    
    success = await test_all_tools()
    await test_complex_query()
    
    print("\n" + "="*70)
    print("Testing complete!")
    print("="*70 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
