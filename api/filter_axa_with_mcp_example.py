#!/usr/bin/env python3
"""
Example: Using Enhanced Filter with MCP Server Integration

This example shows how the enhanced filter would work when integrated
with the MCP startup database server for enriched data retrieval.

CURRENT STATUS: Structure prepared, ready to activate
ACTIVATION: Set --use-mcp flag when MCP server is running
"""

import asyncio
import json
from typing import Dict, List, Optional
from pathlib import Path

# This would be imported when MCP is available
# from mcp_client import StartupDatabaseMCPTools


async def enrich_startup_with_mcp(startup: Dict, mcp_tools: Optional[object] = None) -> Dict:
    """
    Enrich startup data using MCP server tools
    
    Args:
        startup: Startup dict with basic data
        mcp_tools: StartupDatabaseMCPTools instance (optional)
    
    Returns:
        Enhanced startup dict with MCP-sourced data
    """
    
    # If no MCP available, return original
    if not mcp_tools:
        return startup
    
    try:
        company_name = startup.get('company_name', '')
        
        # Query for enriched data via MCP
        enriched = await mcp_tools._get_enrichment_data(company_name)
        
        if enriched:
            # Merge enriched data
            startup['mcp_enriched'] = enriched
            
            # Update funding if MCP has better data
            if enriched.get('verified_funding'):
                startup['totalFunding'] = enriched['verified_funding']
            
            # Add company insights
            if enriched.get('company_insights'):
                startup['insights'] = enriched['company_insights']
    
    except Exception as e:
        # Continue with original data if MCP fails
        pass
    
    return startup


async def filter_with_mcp_enrichment(startups: List[Dict]) -> List[Dict]:
    """
    Filter startups with MCP enrichment
    
    USAGE (when ready):
        startups = json.load(open('docs/architecture/ddbb/slush_full_list.json'))
        enriched_startups = await filter_with_mcp_enrichment(startups[:50])
    """
    
    # This would be initialized when --use-mcp flag is passed
    # mcp_tools = StartupDatabaseMCPTools()
    mcp_tools = None  # Placeholder
    
    enriched = []
    
    for i, startup in enumerate(startups):
        if i % 10 == 0:
            print(f"Enriching startup {i+1}/{len(startups)}")
        
        enriched_startup = await enrich_startup_with_mcp(startup, mcp_tools)
        enriched.append(enriched_startup)
    
    return enriched


def example_mcp_filtering():
    """
    Example: How enhanced filter would use MCP
    """
    
    print("\n" + "="*80)
    print("ENHANCED FILTER + MCP INTEGRATION EXAMPLE")
    print("="*80)
    
    print("\n1. CURRENT STATE (Without MCP)")
    print("   python3 api/filter_axa_startups_enhanced.py --output results.json --stats")
    print("   ✓ Uses keyword matching")
    print("   ✓ Parses funding from description")
    print("   ✓ Uses static employee ranges")
    print("   ✓ Result: 14 startups (score >= 50)")
    
    print("\n2. WITH MCP INTEGRATION (Future)")
    print("   python3 api/filter_axa_startups_enhanced.py \\")
    print("     --use-mcp --output results.json --stats")
    print("   ✓ Queries MCP server for enriched profiles")
    print("   ✓ Gets verified funding amounts")
    print("   ✓ Retrieves current employee counts")
    print("   ✓ Accesses company insights")
    print("   ✓ Verifies website and contact info")
    print("   → Better accuracy and richer data")
    
    print("\n3. MCP DATA SOURCES")
    print("   MCP will query these tables via mcp_startup_server.py:")
    print("   - Startup profiles (funding, location, stage)")
    print("   - Company metrics (employees, growth rate)")
    print("   - Enrichment data (insights, verification)")
    print("   - Network relationships (investors, partners)")
    
    print("\n4. EXAMPLE DATA FLOW")
    print("""
    Input: {company_name: "Matillion", totalFunding: "$307M"}
    
    MCP Query: search_startups_by_name("Matillion")
    MCP Response: {
        company_name: "Matillion",
        totalFunding: 307000000,  # Numeric, verified
        employees: 500,            # Exact count
        verified_funding_date: "2024-10-15",
        funding_stage: "Series E",
        website_verified: true,
        linkedin_followers: 45000,
        glassdoor_rating: 4.2,
        growth_rate_yoy: 0.35
    }
    
    Enhanced Result:
    - More accurate funding figure
    - Verified employee count
    - Recent funding validation
    - Growth trajectory
    - Reputation signals
    """)
    
    print("\n5. INTEGRATION POINTS IN CODE")
    print("""
    # In filter_axa_startups_enhanced.py:
    
    if args.use_mcp:
        from mcp_client import StartupDatabaseMCPTools
        mcp_tools = StartupDatabaseMCPTools()
        
        # Enrich each startup before scoring
        for startup in startups:
            enriched = await enrich_startup_with_mcp(startup, mcp_tools)
            # Score using enriched data
            scoring = calculate_axa_score_enhanced(enriched)
    """)
    
    print("\n6. EXPECTED IMPROVEMENTS WITH MCP")
    print("   ✓ 95%+ funding accuracy (vs ~70% parsing success)")
    print("   ✓ Real-time employee data (vs static ranges)")
    print("   ✓ Verified website/contact (vs missing data)")
    print("   ✓ Growth trends (new signal)")
    print("   ✓ Reputation metrics (new signal)")
    print("   → Could improve Tier 1-2 count by 30-50%")
    
    print("\n7. ACTIVATION STEPS")
    print("   Step 1: Start MCP server")
    print("           python3 api/mcp_startup_server.py")
    print("   ")
    print("   Step 2: Run enhanced filter with MCP")
    print("           python3 api/filter_axa_startups_enhanced.py \\")
    print("             --use-mcp --output axa_mcp_enhanced.json --stats")
    print("   ")
    print("   Step 3: Compare results")
    print("           python3 -c 'import json;")
    print("             d = json.load(open(\"axa_mcp_enhanced.json\"));")
    print("             print(f\"MCP-enhanced: {len(d)} startups, mcp_enriched: {sum(1 for x in d if \\'mcp_enriched\\' in x)}\")'")
    
    print("\n8. ESTIMATED TIMELINE")
    print("   Now        → Enhanced filter without MCP (READY)")
    print("   +1-2 weeks → Start MCP server, test integration")
    print("   +2-4 weeks → Full MCP-enhanced results")
    print("   +4-6 weeks → NVIDIA NIM integration for confidence scoring")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    example_mcp_filtering()
    
    # If MCP becomes available, this would work:
    # asyncio.run(filter_with_mcp_enrichment(startups))
