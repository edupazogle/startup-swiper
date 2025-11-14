# FastAPI Startup Swiper Database API

A FastAPI application that provides REST API endpoints for the Startup Swiper application database, with integrated LiteLLM support for universal LLM access.

## Features

- Full CRUD operations for all database tables
- **🤖 LiteLLM Integration**: Universal LLM API supporting OpenAI, Anthropic, Google AI, and 100+ providers
- **📝 Automatic Logging**: All LLM requests/responses saved to `/logs/llm` folder
- **🔍 Debug Mode**: Full verbose logging for debugging LLM calls
- SQLAlchemy ORM for database management
- Pydantic schemas for request/response validation
- CORS enabled for frontend integration
- SQLite database (easily configurable for PostgreSQL/MySQL)

## Quick Start

### Option 1: Using the start script
```bash
cd /home/akyo/startup_swiper/api
./start.sh
```

### Option 2: Manual setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys (copy and edit .env)
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY or ANTHROPIC_API_KEY

# Start the server
uvicorn main:app --reload
```

Visit:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs

## 🤖 LLM Integration

This API includes full LiteLLM integration with automatic request/response logging.

### LLM Endpoints

**Simple LLM Call:**
```bash
POST /llm/simple
{
  "prompt": "Your prompt here",
  "model": "gpt-4o-mini",
  "temperature": 0.7
}
```

**Chat with Message History:**
```bash
POST /llm/chat
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello!"}
  ],
  "model": "gpt-4o"
}
```

### Supported Models
- OpenAI: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- Anthropic: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`
- Google: `gemini-1.5-pro`, `gemini-1.5-flash`
- And 100+ more via LiteLLM

### LLM Logging
All LLM requests and responses are automatically logged to `/logs/llm/` as JSON files:
- Request content and parameters
- Response content and metadata
- Token usage statistics
- Duration and timestamps
- Error details (if any)

📚 **Full LLM Documentation**: See [LLM_INTEGRATION.md](./LLM_INTEGRATION.md)

## Database Tables

The API provides endpoints for the following tables:
- **calendar-events**: Store meeting and event data
- **linkedin-chat-messages**: LinkedIn conversation history
- **admin-user**: Admin authentication
- **votes**: User voting history on startups
- **auroral-info**: Aurora background configuration
- **ideas**: User submitted ideas
- **startup-ratings**: Startup rating and feedback
- **finished-users**: Users who completed the flow
- **ai-chat-messages**: AI chat conversation history
- **user-events**: User activity tracking
- **ai-assistant-messages**: AI assistant interactions
- **current-user-id**: Current active user
- **data-version**: Data versioning

## Installation

### 1. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure API keys:
```bash
cp .env.example .env
# Edit .env and add:
# OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. (Optional) Configure database:
   - Default: SQLite (`startup_swiper.db`)
   - For PostgreSQL/MySQL: Set `DATABASE_URL` environment variable

## Running the API

```bash
# Quick start with script
./start.sh

# Or manually:
# Development mode
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or run directly:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Endpoints

### Calendar Events
- `POST /calendar-events/` - Create event
- `GET /calendar-events/` - List all events
- `GET /calendar-events/{event_id}` - Get specific event
- `PUT /calendar-events/{event_id}` - Update event
- `DELETE /calendar-events/{event_id}` - Delete event

### Votes
- `POST /votes/` - Create vote
- `GET /votes/` - List all votes
- `GET /votes/startup/{startup_id}` - Get votes for startup

### Ideas
- `POST /ideas/` - Create idea
- `GET /ideas/` - List all ideas
- `GET /ideas/{idea_id}` - Get specific idea

### Startup Ratings
- `POST /startup-ratings/` - Create/update rating
- `GET /startup-ratings/` - List all ratings
- `GET /startup-ratings/{startup_id}` - Get rating for startup

## Example Request

```bash
# Create a calendar event
curl -X POST "http://localhost:8000/calendar-events/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Startup Meeting",
    "startTime": "2025-11-15T10:00:00",
    "endTime": "2025-11-15T11:00:00",
    "type": "meeting",
    "attendees": ["user1", "user2"],
    "isSaved": false
  }'

# Create a vote
curl -X POST "http://localhost:8000/votes/" \
  -H "Content-Type: application/json" \
  -d '{
    "startupId": "startup-123",
    "userId": 1,
    "userName": "John Doe",
    "interested": true,
    "meetingScheduled": false
  }'
```

## Environment Variables

- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)

Example for PostgreSQL:
```bash
export DATABASE_URL="postgresql://user:password@localhost/startup_swiper"
```

## Project Structure

```
api/
├── main.py           # FastAPI application and routes
├── models.py         # SQLAlchemy database models
├── schemas.py        # Pydantic schemas
├── crud.py           # CRUD operations
├── database.py       # Database connection setup
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Development

The database tables are automatically created on first run. The API uses SQLAlchemy migrations through `Base.metadata.create_all()`.

## License

See parent project LICENSE file.
