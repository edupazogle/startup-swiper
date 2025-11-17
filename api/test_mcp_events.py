"""
Test MCP client event search tools
"""
import asyncio
from mcp_client import StartupDatabaseMCPTools

async def test_mcp_event_tools():
    """Test MCP event search tools"""
    mcp_tools = StartupDatabaseMCPTools()
    
    print("=" * 80)
    print("TESTING MCP EVENT SEARCH TOOLS")
    print("=" * 80)
    
    # Test 1: Search events
    print("\n1. Testing search_events with 'Google'...")
    result = await mcp_tools.call_tool("search_events", query="Google", limit=3)
    print(f"Success: {result['success']}")
    print(f"Count: {result.get('count', 0)}")
    if result['success'] and result.get('results'):
        for event in result['results']:
            print(f"  - {event['title']} by {event['organizer']}")
    
    # Test 2: Search by organizer
    print("\n2. Testing search_events_by_organizer with 'AWS'...")
    result = await mcp_tools.call_tool("search_events_by_organizer", organizer="AWS", limit=3)
    print(f"Success: {result['success']}")
    print(f"Count: {result.get('count', 0)}")
    if result['success'] and result.get('results'):
        for event in result['results']:
            print(f"  - {event['title']} - {event['datetime']}")
    
    # Test 3: Search by date
    print("\n3. Testing search_events_by_date with 'Nov 20'...")
    result = await mcp_tools.call_tool("search_events_by_date", date_query="Nov 20", limit=3)
    print(f"Success: {result['success']}")
    print(f"Count: {result.get('count', 0)}")
    if result['success'] and result.get('results'):
        for event in result['results']:
            print(f"  - {event['title']} at {event['location']}")
    
    # Test 4: Get event details
    print("\n4. Testing get_event_details by title...")
    result = await mcp_tools.call_tool("get_event_details", title="Y Science 2025")
    print(f"Success: {result['success']}")
    if result['success'] and result.get('event'):
        event = result['event']
        print(f"  Title: {event['title']}")
        print(f"  Organizer: {event['organizer']}")
        print(f"  DateTime: {event['datetime']}")
        print(f"  Location: {event['location']}")
    
    # Test 5: Get all organizers
    print("\n5. Testing get_all_event_organizers...")
    result = await mcp_tools.call_tool("get_all_event_organizers", limit=5)
    print(f"Success: {result['success']}")
    print(f"Count: {result.get('count', 0)}")
    if result['success'] and result.get('results'):
        for org in result['results']:
            print(f"  - {org['organizer']}: {org['event_count']} events")
    
    print("\n" + "=" * 80)
    print("MCP TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_mcp_event_tools())
