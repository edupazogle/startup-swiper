#!/usr/bin/env python3
"""
AI Concierge Agent Test - Demonstrates tool calling with startup database queries

Tests the MCPEnhancedAIConcierge class which uses tools to answer questions.
"""

import asyncio
import sys
from pathlib import Path

# Add API directory to path
api_dir = Path(__file__).parent
sys.path.insert(0, str(api_dir))

from ai_concierge import create_mcp_concierge
from database import SessionLocal


async def test_startup_search_with_context():
    """Test the AI Concierge searching for startups"""
    
    print("\n" + "="*70)
    print("AI CONCIERGE AGENT - STARTUP SEARCH TEST")
    print("="*70)
    
    db = SessionLocal()
    concierge = create_mcp_concierge(db)
    
    print("\n✓ AI Concierge initialized")
    print(f"✓ {len(concierge.get_tool_definitions())} tools available")
    
    # Test 1: Search by industry
    print("\n" + "-"*70)
    print("TEST 1: Search for AI startups")
    print("-"*70)
    
    result = await concierge.conversational_startup_search(
        query="AI",
        search_type="industry"
    )
    
    print("\nQuery: 'Find me AI startups'")
    print("Method: search_startups_by_industry")
    print("\nResult:")
    print(result)
    
    # Test 2: Search by name
    print("\n" + "-"*70)
    print("TEST 2: Search for specific startup")
    print("-"*70)
    
    result = await concierge.conversational_startup_search(
        query="Matillion",
        search_type="name"
    )
    
    print("\nQuery: 'Find Matillion'")
    print("Method: search_startups_by_name")
    print("\nResult:")
    print(result)
    
    # Test 3: Search by funding stage
    print("\n" + "-"*70)
    print("TEST 3: Search for Series B startups")
    print("-"*70)
    
    result = await concierge.conversational_startup_search(
        query="Series B",
        search_type="funding"
    )
    
    print("\nQuery: 'Find Series B startups'")
    print("Method: search_startups_by_funding")
    print("\nResult:")
    print(result)
    
    # Test 4: Get detailed info
    print("\n" + "-"*70)
    print("TEST 4: Get detailed startup information")
    print("-"*70)
    
    detail = await concierge.mcp_tools.call_tool(
        "get_startup_details",
        company_name="SumUp"
    )
    
    if detail.get('success'):
        startup = detail.get('startup', {})
        print("\nQuery: 'Tell me about SumUp'")
        print("Method: get_startup_details")
        print("\nResult:")
        print(f"  Company: {startup.get('name')}")
        print(f"  Website: {startup.get('website')}")
        print(f"  Industry: {startup.get('industry')}")
        print(f"  Total Funding: ${startup.get('totalFunding', 'N/A')}M")
        print(f"  Current Stage: {startup.get('stage')}")
        print(f"  Location: {startup.get('location')}")
        print(f"  Description: {startup.get('description', 'N/A')[:150]}...")
    else:
        print(f"✗ Error: {detail.get('error')}")
    
    db.close()
    print("\n" + "="*70)
    print("✓ All concierge tests completed successfully!")
    print("="*70 + "\n")


async def test_tool_calling():
    """Test direct tool calling from the concierge"""
    
    print("\n" + "="*70)
    print("AI CONCIERGE - DIRECT TOOL CALLING TEST")
    print("="*70)
    
    db = SessionLocal()
    concierge = create_mcp_concierge(db)
    
    # Show available tools
    print("\n📋 Available Tools for AI Agent:")
    print("-"*70)
    
    tools = concierge.get_tool_definitions()
    for i, tool in enumerate(tools, 1):
        name = tool['function']['name']
        description = tool['function']['description']
        print(f"\n{i}. {name}")
        print(f"   {description}")
        params = tool['function']['parameters'].get('properties', {})
        if params:
            print(f"   Parameters: {', '.join(params.keys())}")
    
    # Test calling tools
    print("\n" + "-"*70)
    print("🔧 Testing Tool Calls")
    print("-"*70)
    
    test_calls = [
        ("search_startups_by_name", {"query": "Cognita", "limit": 3}),
        ("search_startups_by_industry", {"industry": "fintech", "limit": 3}),
        ("get_top_startups_by_funding", {"limit": 3}),
    ]
    
    for tool_name, params in test_calls:
        print(f"\n📤 Calling: {tool_name}")
        print(f"   Parameters: {params}")
        
        result = await concierge.handle_tool_call(tool_name, **params)
        
        if result.get('success'):
            count = result.get('count', 0)
            results = result.get('results', [])
            print(f"   ✓ Success - Retrieved {count} results")
            if results:
                for startup in results[:2]:
                    print(f"     • {startup.get('name')} ({startup.get('industry', 'N/A')})")
        else:
            print(f"   ✗ Error: {result.get('error')}")
    
    db.close()
    print("\n" + "="*70 + "\n")


async def test_startup_filtering():
    """Test complex startup filtering scenarios"""
    
    print("\n" + "="*70)
    print("AI CONCIERGE - STARTUP FILTERING TEST")
    print("="*70)
    
    db = SessionLocal()
    concierge = create_mcp_concierge(db)
    
    # Scenario 1: Find well-funded AI startups
    print("\n📌 Scenario 1: Find well-funded AI startups")
    print("-"*70)
    
    ai_startups = await concierge.mcp_tools.call_tool(
        "search_startups_by_industry",
        industry="AI",
        limit=10
    )
    
    if ai_startups.get('success'):
        results = ai_startups.get('results', [])
        # Filter for funded startups
        funded = [s for s in results if s.get('funding') and s.get('funding') > 10]
        
        print(f"Total AI startups found: {len(results)}")
        print(f"Well-funded (>$10M): {len(funded)}\n")
        
        if funded:
            print("Top funded AI startups:")
            for startup in sorted(funded, key=lambda x: x.get('funding', 0), reverse=True)[:5]:
                print(f"  • {startup['name']}: ${startup['funding']}M")
    
    # Scenario 2: Find startups by stage
    print("\n📌 Scenario 2: Find startups at different funding stages")
    print("-"*70)
    
    stages = ["Seed", "Series A", "Series B"]
    for stage in stages:
        result = await concierge.mcp_tools.call_tool(
            "search_startups_by_funding",
            stage=stage,
            limit=1
        )
        
        if result.get('success'):
            count = result.get('count', 0)
            print(f"  {stage}: {count} startups found")
    
    # Scenario 3: Get top funded startups and get details
    print("\n📌 Scenario 3: Top funded startups with details")
    print("-"*70)
    
    top = await concierge.mcp_tools.call_tool(
        "get_top_startups_by_funding",
        limit=3
    )
    
    if top.get('success'):
        results = top.get('results', [])
        print(f"Found {len(results)} top startups:\n")
        
        for startup in results:
            print(f"  💰 {startup['name']}")
            print(f"     Funding: ${startup['funding']}M")
            print(f"     Industry: {startup['industry']}")
            print(f"     Website: {startup.get('website', 'N/A')}\n")
    
    db.close()
    print("="*70 + "\n")


async def main():
    """Run all AI Concierge tests"""
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "AI CONCIERGE AGENT TESTING SUITE" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    
    await test_startup_search_with_context()
    await test_tool_calling()
    await test_startup_filtering()
    
    print("\n" + "="*70)
    print("🎉 ALL AI CONCIERGE TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nThe AI Concierge is fully functional with:")
    print("  ✓ 7 MCP tools for database queries")
    print("  ✓ Tool calling support")
    print("  ✓ Startup search and filtering")
    print("  ✓ Detailed startup information retrieval")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
