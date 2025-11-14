# AI Concierge System Documentation

## Overview

The AI Concierge is a comprehensive intelligent assistant system designed for Slush 2025 that can answer questions about:

- **Startups** - From local database + CB Insights API
- **Events & Schedules** - Calendar events and sessions
- **Meetings & Participants** - Meeting information and attendees
- **Directions** - Navigation using Google Maps API
- **Attendees** - Information about event participants
- **Side Events** - Including location and navigation details

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Question                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              AI Concierge (ai_concierge.py)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Question Classification & Context Retrieval         │  │
│  └──────────────────────────────────────────────────────┘  │
└───────┬─────────────┬──────────────┬──────────────┬─────────┘
        │             │              │              │
        ▼             ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐
│   Database   │ │CB Insights│ │Google Maps│ │ LLM (GPT)  │
│   (SQLite)   │ │   API     │ │   API     │ │  Analysis  │
│              │ │           │ │           │ │            │
│ • Events     │ │• Research │ │• Directions│ │• Synthesis │
│ • Votes      │ │• Company  │ │• Travel    │ │• Response  │
│ • Attendees  │ │  Data     │ │  Times     │ │ Generation │
│ • Startups   │ │• News     │ │• Places    │ │            │
└──────────────┘ └──────────┘ └──────────┘ └─────────────┘
```

## Components

### 1. AI Concierge (`ai_concierge.py`)
Main orchestrator that:
- Classifies questions
- Retrieves relevant context
- Calls appropriate data sources
- Generates comprehensive answers using LLM

### 2. CB Insights Integration (`cb_insights_integration.py`)
- Company search and details
- Funding information
- News and developments
- Advanced research via CB Chat

### 3. Google Maps Integration (`google_maps_integration.py`)
- Directions (walking, driving, transit, cycling)
- Travel time estimates
- Place details and search
- Nearby places

### 4. Context Retriever
Intelligent system that fetches relevant data:
- Startup information from JSON database
- Event schedules from database
- Vote statistics
- Attendee information
- Meeting details

## API Endpoints

### Main Concierge Endpoint

#### `POST /concierge/ask`
Ask any question to the AI Concierge.

**Request:**
```json
{
  "question": "What AI startups are at the event?",
  "user_context": {
    "role": "investor",
    "interests": ["AI", "fintech"],
    "location": "Helsinki"
  }
}
```

**Response:**
```json
{
  "answer": "Based on the available information, here are the AI startups...",
  "question_type": "startup_info"
}
```

**Question Types:**
- `startup_info` - Questions about startups
- `event_info` - Questions about events
- `directions` - Navigation questions
- `attendee_info` - Questions about attendees
- `voting_info` - Questions about votes/interest
- `general` - Other questions

### Specialized Endpoints

#### `POST /concierge/startup-details`
Get detailed information about a specific startup.

**Request:**
```json
{
  "startup_name": "759 Studio"
}
```

**Response:**
```json
{
  "answer": "# 759 Studio\n**Description:** Provider of architectural...",
  "question_type": "startup_details"
}
```

#### `POST /concierge/event-details`
Get information about events.

**Request:**
```json
{
  "question": "keynote sessions"
}
```

#### `POST /concierge/directions`
Get directions between locations.

**Request:**
```json
{
  "origin": "Helsinki Central Station",
  "destination": "Messukeskus Helsinki",
  "mode": "walking"
}
```

**Modes:** `walking`, `driving`, `transit`, `bicycling`

**Response:**
```json
{
  "answer": "📍 From: Helsinki Central Station\n📍 To: Messukeskus...",
  "question_type": "directions"
}
```

#### `GET /concierge/search-startups`
Search for startups by keyword.

**Parameters:**
- `query` (string) - Search term
- `limit` (int) - Max results (default: 10)

**Response:**
```json
{
  "results": [
    {
      "id": 43732,
      "name": "759 Studio",
      "description": "...",
      "totalFunding": "0.08",
      "website": "https://..."
    }
  ],
  "count": 5
}
```

#### `GET /concierge/startup-categories`
Get startups by category.

**Parameters:**
- `category` (string) - Category name
- `limit` (int) - Max results (default: 10)

**Response:**
```json
{
  "results": [...],
  "count": 15,
  "category": "Artificial Intelligence"
}
```

## Usage Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Ask a question
response = requests.post(
    f"{BASE_URL}/concierge/ask",
    json={
        "question": "What fintech startups have raised over $5M?",
        "user_context": {"role": "investor"}
    }
)
answer = response.json()["answer"]
print(answer)

# Search startups
response = requests.get(
    f"{BASE_URL}/concierge/search-startups",
    params={"query": "AI", "limit": 10}
)
startups = response.json()["results"]

# Get directions
response = requests.post(
    f"{BASE_URL}/concierge/directions",
    json={
        "origin": "Hotel",
        "destination": "Messukeskus",
        "mode": "walking"
    }
)
directions = response.json()["answer"]
```

### JavaScript/TypeScript

```typescript
const BASE_URL = 'http://localhost:8000';

// Ask a question
async function askConcierge(question: string, context?: any) {
  const response = await fetch(`${BASE_URL}/concierge/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, user_context: context })
  });
  const data = await response.json();
  return data.answer;
}

// Search startups
async function searchStartups(query: string, limit = 10) {
  const response = await fetch(
    `${BASE_URL}/concierge/search-startups?query=${query}&limit=${limit}`
  );
  const data = await response.json();
  return data.results;
}

// Get directions
async function getDirections(origin: string, destination: string, mode = 'walking') {
  const response = await fetch(`${BASE_URL}/concierge/directions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ origin, destination, mode })
  });
  const data = await response.json();
  return data.answer;
}

// Usage
const answer = await askConcierge("What's happening at 2pm?");
const startups = await searchStartups("sustainable tech");
const route = await getDirections("Central Station", "Venue", "transit");
```

### cURL

```bash
# Ask a question
curl -X POST http://localhost:8000/concierge/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me about AI startups",
    "user_context": {"interests": ["AI", "ML"]}
  }'

# Search startups
curl "http://localhost:8000/concierge/search-startups?query=fintech&limit=5"

# Get directions
curl -X POST http://localhost:8000/concierge/directions \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Helsinki Central Station",
    "destination": "Messukeskus Helsinki",
    "mode": "walking"
  }'
```

## Question Examples

The AI Concierge can answer various types of questions:

### Startup Questions
- "What AI startups are at the event?"
- "Tell me about [company name]"
- "Which startups have raised the most funding?"
- "Show me sustainable tech companies"
- "Compare [company A] and [company B]"
- "What's the average funding stage?"

### Event Questions
- "What events are happening today?"
- "When is the keynote session?"
- "Show me all networking events"
- "What's on the main stage at 2pm?"
- "Tell me about side events"

### Direction Questions
- "How do I get to Messukeskus from downtown?"
- "Directions from [A] to [B]"
- "How long does it take to walk to the venue?"
- "What's the best route by public transit?"

### Meeting Questions
- "Who am I meeting with today?"
- "What's my schedule?"
- "Show me all meetings with [person]"
- "When is my next meeting?"

### Attendee Questions
- "Who is attending the event?"
- "How many people are registered?"
- "Are there investors from [country]?"
- "Who should I network with?"

### Complex Questions
- "I'm interested in fintech. Which startups should I meet and when are they presenting?"
- "What are the best networking opportunities for AI founders?"
- "Which startups in the sustainability space have raised Series A?"

## Configuration

### Required Environment Variables

Add to `.env` file:

```bash
# Required for core functionality
OPENAI_API_KEY=sk-your-openai-key

# Optional enhancements
CB_INSIGHTS_API_KEY=your-cb-insights-key
GOOGLE_MAPS_API_KEY=your-google-maps-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### Startup Data

The system loads startup data from JSON files located at:
```
app/startup-swipe-schedu/startups/
├── slush2_extracted.json  (Primary source)
├── slush2.json            (Fallback)
└── slush_full.json        (Fallback)
```

## Features

### Context-Aware Responses
The concierge uses multiple data sources to provide comprehensive answers:
- **Local Database**: Events, votes, attendees, ratings
- **Startup Data**: 180K+ entries with detailed information
- **CB Insights**: Additional research and market data
- **Google Maps**: Real-time directions and location info
- **LLM Analysis**: Intelligent synthesis and natural language responses

### Intelligent Question Classification
Automatically determines question type and retrieves relevant context:
- Startup-related queries → Database + CB Insights
- Event queries → Calendar events
- Navigation queries → Google Maps
- Attendee queries → Attendee database
- Complex queries → Multiple sources combined

### Rich Responses
- **Structured Information**: Clear, organized answers
- **Multiple Sources**: Combines data from various APIs
- **Context Preservation**: Remembers conversation context
- **Actionable Information**: Provides next steps and recommendations

## Testing

### Run Full Test Suite
```bash
cd /home/akyo/startup_swiper/api
python test_concierge.py
```

Tests cover:
- Startup queries
- Event information
- Directions
- Search functionality
- Complex multi-part questions
- Category searches
- Meeting and attendee info

### Run Examples
```bash
python examples_concierge.py
```

Shows practical usage examples for all features.

## Performance

- **Response Time**: 1-3 seconds for simple queries
- **Complex Queries**: 3-5 seconds (multiple API calls)
- **Caching**: Startup data cached in memory
- **Concurrent Requests**: Async support for multiple simultaneous queries

## Logging

All LLM interactions are automatically logged to `/logs/llm/` including:
- User questions
- Retrieved context
- LLM responses
- Processing time
- Question classification

## Error Handling

The system gracefully handles:
- Missing API keys (falls back to available sources)
- API failures (provides partial information)
- Invalid queries (asks for clarification)
- No data found (suggests alternatives)

## Limitations

- CB Insights API requires valid API key
- Google Maps API requires valid API key and may have usage limits
- Startup data accuracy depends on source JSON files
- LLM responses may vary based on model and context

## Future Enhancements

Potential improvements:
- [ ] Real-time event updates via webhooks
- [ ] User preference learning
- [ ] Multi-language support
- [ ] Voice interface integration
- [ ] Personalized recommendations
- [ ] Meeting scheduling automation
- [ ] Calendar integration
- [ ] Push notifications for relevant events

## Support

For issues or questions:
1. Check API logs in `/logs/llm/`
2. Verify environment variables in `.env`
3. Test individual components (CB Insights, Google Maps, LLM)
4. Review startup data files

## License

See main project LICENSE file.
