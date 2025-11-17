# Event Search Enhancement for AI Concierge

## Overview
Enhanced the AI Concierge database MCP tool to include comprehensive event search capabilities for Slush 2025 events. The system can now search, filter, and provide detailed information about the 381+ events scraped from the Slush platform.

## New Features

### 1. Event Search Tools
The following tools have been added to both the MCP client and AI Concierge agent:

#### `search_events`
Search for events by title or organizer name.
- **Parameters:**
  - `query`: Search query for event title or organizer
  - `limit`: Maximum results (default: 10)
- **Example:** "Find Google events" or "Show me events about AI"

#### `search_events_by_organizer`
Find all events organized by a specific company.
- **Parameters:**
  - `organizer`: Company/organization name
  - `limit`: Maximum results (default: 10)
- **Example:** "What events is AWS hosting?"

#### `search_events_by_date`
Find events happening on specific dates.
- **Parameters:**
  - `date_query`: Date string (e.g., "Nov 19", "Nov 20", "November 19")
  - `limit`: Maximum results (default: 10)
- **Example:** "What's happening on Nov 19?"

#### `search_events_by_category`
Search events by category or topic.
- **Parameters:**
  - `category`: Category/topic name (e.g., "AI", "Demo", "Networking")
  - `limit`: Maximum results (default: 10)
- **Example:** "Show me AI-related events"
- **Note:** Currently limited as most events lack category tags

#### `get_event_details`
Get comprehensive details about a specific event.
- **Parameters:**
  - `title`: Event title or partial title
- **Returns:** Full event information including organizer, time, location, categories, status, and user insights
- **Example:** "Tell me about the Y Science 2025 event"

#### `get_all_event_organizers`
Get list of all companies/organizations hosting events.
- **Parameters:**
  - `limit`: Maximum organizers to return (default: 20)
- **Returns:** List of organizers with event counts, sorted by number of events
- **Example:** "Which companies are organizing the most events?"

## Architecture

### MCP Client Layer (`mcp_client.py`)
- Added 6 new async methods for event search
- Tools integrated into `StartupDatabaseMCPTools` class
- Returns structured JSON responses with success/error handling
- Direct database access using SQLAlchemy

### AI Concierge Layer (`qwen_agentic_concierge.py`)
- Added 6 new tools to `ToolRegistry`
- Implements ReAct pattern for intelligent event search
- Returns formatted markdown strings for user-friendly output
- Includes LangSmith tracing for observability

### Database Layer (`models.py`)
- Uses existing `SlushEvent` model
- Fields: id, title, organizer, datetime, location, categories, status
- Optional user annotation fields: insight, tags, rating, followUp

## Data Coverage

### Event Statistics
- **Total Events:** 381
- **Date Range:** Nov 18-20, 2025
- **Top Organizers:**
  - Slush: 96 events
  - 27pilots - a Deloitte Business: 15 events
  - Google: 13 events
  - SusHi Tech Tokyo: 11 events
  - swisstech: 7 events

### Event Information
Each event includes:
- ✅ Title
- ✅ Organizer
- ✅ Date & Time (formatted string)
- ✅ Location (venue and room)
- ✅ Status (e.g., "Signature Side Event", "Closed", "Open")
- ⚠️ Categories (mostly empty - need enhancement)

## Usage Examples

### Direct Tool Usage (Python)
```python
from database import SessionLocal
from qwen_agentic_concierge import ToolRegistry

db = SessionLocal()
tools = ToolRegistry(db)

# Search for Google events
result = tools._search_events("Google", limit=5)
print(result)

# Get events on Nov 19
result = tools._search_events_by_date("Nov 19", limit=10)
print(result)

# Find who's organizing events
result = tools._get_all_event_organizers(limit=10)
print(result)

db.close()
```

### MCP Client Usage (Async)
```python
import asyncio
from mcp_client import StartupDatabaseMCPTools

async def search_events():
    mcp_tools = StartupDatabaseMCPTools()
    
    # Search by organizer
    result = await mcp_tools.call_tool(
        "search_events_by_organizer", 
        organizer="AWS", 
        limit=5
    )
    
    if result['success']:
        for event in result['results']:
            print(f"{event['title']} - {event['datetime']}")

asyncio.run(search_events())
```

### AI Concierge Usage (Natural Language)
Users can now ask natural language questions:
- "What events is Google hosting at Slush?"
- "Show me events happening on Nov 19"
- "Tell me about the Y Science 2025 event"
- "Which companies are organizing the most events?"
- "Find networking events"

The AI Concierge will automatically:
1. **Think:** Analyze the question
2. **Act:** Choose appropriate event search tool(s)
3. **Observe:** Review database results
4. **Answer:** Provide formatted, comprehensive response

## System Prompt Enhancement

The AI Concierge system prompt has been updated with event search strategy:
```
## Tool Usage Strategy
...
- **Event search**: 
  - Use `search_events` to find events by title or organizer
  - Use `search_events_by_organizer` to see all events hosted by a company
  - Use `search_events_by_date` to find events on specific dates
  - Use `search_events_by_category` to find events by topic
  - Use `get_event_details` for comprehensive information about a specific event
  - Use `get_all_event_organizers` to see which companies are hosting events
```

## Testing

### Unit Tests
Three test scripts have been created:

1. **`test_event_tools_direct.py`** - Direct tool function tests
   - Tests all 6 event search tools
   - Verifies database queries and response formatting
   - No AI/LLM involved

2. **`test_mcp_events.py`** - MCP client integration tests
   - Tests async MCP tool calls
   - Verifies JSON response structure
   - Tests error handling

3. **`test_event_search.py`** - End-to-end AI Concierge tests
   - Tests natural language queries
   - Verifies ReAct pattern execution
   - Tests with real LLM (Qwen)

### Running Tests
```bash
cd /home/akyo/startup_swiper/api
source ../.venv/bin/activate

# Direct tool tests (fastest)
python test_event_tools_direct.py

# MCP client tests
python test_mcp_events.py

# Full AI Concierge tests (requires API keys)
python test_event_search.py
```

## Files Modified

### `/home/akyo/startup_swiper/api/mcp_client.py`
- Added 6 event search tools to `_get_tools_definition()`
- Implemented 6 async methods: `_search_events`, `_search_events_by_organizer`, etc.
- Added event tool routing in `call_tool()` method
- **Lines added:** ~340 lines

### `/home/akyo/startup_swiper/api/qwen_agentic_concierge.py`
- Added 6 event search tools to `ToolRegistry._register_tools()`
- Implemented 6 methods with LangSmith tracing decorators
- Updated system prompt with event search strategy
- **Lines added:** ~230 lines

## Integration Points

### Database
- Queries `slush_events` table
- Uses SQLAlchemy ORM
- Supports LIKE queries for flexible text search
- JSON field casting for category searches

### AI Agent
- Integrated into ReAct reasoning loop
- Works alongside existing startup and people search
- Maintains conversation context
- Provides structured markdown responses

### API Endpoints
- Event search tools accessible via:
  - Direct function calls (Python)
  - MCP client (async)
  - AI Concierge (natural language)
- Future: Could expose as REST API endpoints

## Future Enhancements

### Short Term
1. **Enhance Category Data:** Re-scrape or manually tag events with proper categories
2. **Add Time Filters:** "Events in the morning", "Evening events"
3. **Location Filters:** "Events in Venue 5", "Side events only"
4. **Status Filters:** "Show only open events", "Hide closed events"

### Medium Term
1. **Event Recommendations:** "Suggest events for me based on my interests"
2. **Conflict Detection:** "Are there any schedule conflicts?"
3. **Personalization:** User preferences and saved events
4. **Calendar Export:** ICS file generation

### Long Term
1. **Real-time Updates:** Sync with live Slush platform
2. **Attendee Matching:** "Who else is attending this event?"
3. **Smart Scheduling:** "Build an optimal schedule for me"
4. **Event Analytics:** "Trending topics", "Most popular organizers"

## Performance Notes

- Database queries are fast (<50ms for most searches)
- Limit parameters prevent overwhelming responses
- Indexes on `title` and `organizer` columns improve search speed
- JSON field searches slightly slower (no index on categories)

## Known Limitations

1. **Empty Categories:** Most events lack category tags (scraped data limitation)
2. **Date Format:** Dates stored as strings, not datetime objects (could improve filtering)
3. **No Event IDs:** Events don't have external IDs, only database IDs
4. **Static Data:** Events scraped once, not real-time
5. **No Attendee Data:** Events not linked to attendee records yet

## Related Documentation

- `SLUSH_EVENTS_SCRAPING.md` - Event scraping process
- `api/README.md` - API documentation
- `AI_CONCIERGE_ARCHITECTURE.md` - Concierge design patterns

## Support

For issues or questions:
1. Check test scripts for usage examples
2. Review LangSmith traces for debugging
3. Verify database has event data: `SELECT COUNT(*) FROM slush_events`
4. Check logs: `/home/akyo/startup_swiper/logs/`
