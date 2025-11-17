"""
Direct unit tests for event search tools
"""
from database import SessionLocal
from qwen_agentic_concierge import ToolRegistry

def test_event_tools():
    """Test event search tools directly"""
    db = SessionLocal()
    tools = ToolRegistry(db)
    
    print("=" * 80)
    print("TESTING EVENT SEARCH TOOLS (Direct)")
    print("=" * 80)
    
    # Test 1: Search events by keyword
    print("\n1. Testing search_events with 'Google'...")
    result = tools._search_events("Google", limit=3)
    print(result)
    
    # Test 2: Search events by organizer
    print("\n2. Testing search_events_by_organizer with 'Slush'...")
    result = tools._search_events_by_organizer("Slush", limit=3)
    print(result)
    
    # Test 3: Search events by date
    print("\n3. Testing search_events_by_date with 'Nov 19'...")
    result = tools._search_events_by_date("Nov 19", limit=3)
    print(result)
    
    # Test 4: Get all organizers
    print("\n4. Testing get_all_event_organizers (top 10)...")
    result = tools._get_all_event_organizers(limit=10)
    print(result)
    
    # Test 5: Get event details
    print("\n5. Testing get_event_details for 'Y Science 2025'...")
    result = tools._get_event_details("Y Science 2025")
    print(result)
    
    # Test 6: Search by category (if any events have categories)
    print("\n6. Testing search_events_by_category with 'AI'...")
    result = tools._search_events_by_category("AI", limit=3)
    print(result)
    
    db.close()
    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_event_tools()
