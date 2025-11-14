# LiteLLM Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend / Client                        │
│  (React TypeScript, cURL, Python, etc.)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Request
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Server (main.py)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  POST /llm/simple  │  POST /llm/chat                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Function Call
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Config Module (llm_config.py)             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • simple_llm_call_async()                               │  │
│  │  • llm_completion()                                      │  │
│  │  • LLMLogger class                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬───────────────────────┬────────────────────┘
                     │                       │
                     │ API Call              │ Log to Disk
                     │                       │
                     ▼                       ▼
┌─────────────────────────────────┐  ┌──────────────────────────┐
│         LiteLLM Library         │  │   /logs/llm/*.json       │
│  ┌──────────────────────────┐  │  │  ┌────────────────────┐ │
│  │  litellm.acompletion()   │  │  │  │ Request details    │ │
│  │  litellm.completion()    │  │  │  │ Response content   │ │
│  └──────────────────────────┘  │  │  │ Token usage        │ │
└────────────┬────────────────────┘  │  │ Duration           │ │
             │                       │  │ Metadata           │ │
             │ Route to Provider     │  │ Errors (if any)    │ │
             │                       │  └────────────────────┘ │
             ▼                       └──────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Providers (via Internet)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  OpenAI  │  │Anthropic │  │ Google   │  │  Azure   │ etc.. │
│  │  GPT-4   │  │ Claude 3 │  │ Gemini   │  │ OpenAI   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Request Flow:
```
1. Client sends request to FastAPI endpoint
   ↓
2. FastAPI validates request with Pydantic schemas
   ↓
3. Calls llm_config module functions
   ↓
4. LiteLLM routes to appropriate provider (OpenAI, Anthropic, etc.)
   ↓
5. Provider returns response
   ↓
6. Response logged to /logs/llm/
   ↓
7. Response returned to client
```

## Component Details

### 1. FastAPI Server (`main.py`)
- **Purpose**: HTTP API endpoints
- **Endpoints**: 
  - `/llm/simple` - Simple prompt-response
  - `/llm/chat` - Full conversation with history
- **Features**: CORS, validation, error handling

### 2. LLM Config Module (`llm_config.py`)
- **Purpose**: LiteLLM configuration and logging
- **Components**:
  - `LLMLogger` class - Handles all logging
  - `llm_completion()` - Async completion calls
  - `simple_llm_call()` - Simplified interface
- **Features**: 
  - Request ID generation
  - Duration tracking
  - Token counting
  - Error logging

### 3. LiteLLM Library
- **Purpose**: Universal LLM API
- **Supports**: 100+ providers
- **Features**:
  - Unified interface
  - Automatic routing
  - Retry logic
  - Streaming support

### 4. Log Storage (`/logs/llm/`)
- **Format**: JSON files
- **Naming**: `timestamp_model_requestid.json`
- **Contents**: Complete request/response data
- **Purpose**: 
  - Debugging
  - Cost tracking
  - Audit trail
  - Performance analysis

## Request/Response Logging

### What Gets Logged:

```json
{
  "timestamp": "2025-11-14T10:30:45.123456",
  "request_id": "unique-uuid",
  "model": "gpt-4o",
  "duration_ms": 1234.56,
  
  "request": {
    "messages": [...],
    "metadata": {...}
  },
  
  "response": {
    "content": "...",
    "usage": {
      "prompt_tokens": 45,
      "completion_tokens": 123,
      "total_tokens": 168
    }
  },
  
  "error": null,
  "success": true
}
```

## Environment Configuration

```
.env file
├── OPENAI_API_KEY        → OpenAI models
├── ANTHROPIC_API_KEY     → Claude models
├── GOOGLE_API_KEY        → Gemini models
├── AZURE_API_KEY         → Azure OpenAI
└── DATABASE_URL          → Database connection
```

## File Organization

```
/home/akyo/startup_swiper/
├── api/
│   ├── main.py              # FastAPI application
│   ├── llm_config.py        # LiteLLM + logging
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # API keys (not in git)
│   ├── .env.example         # Template
│   ├── start.sh             # Quick start script
│   ├── test_llm.py          # Test suite
│   ├── examples_llm.py      # Usage examples
│   ├── README.md            # Main docs
│   ├── LLM_INTEGRATION.md   # LLM-specific docs
│   └── IMPLEMENTATION_SUMMARY.md
│
└── logs/
    └── llm/                 # Log storage
        ├── .gitkeep         # Keep directory in git
        ├── .gitignore       # Ignore log files
        └── *.json           # Actual log files
```

## Integration Points

### Frontend Integration:
```typescript
// Replace existing window.spark.llm() calls with:
async function callLLM(prompt: string, model: string = 'gpt-4o') {
  const response = await fetch('http://localhost:8000/llm/simple', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, model })
  });
  return (await response.json()).content;
}
```

### Python Integration:
```python
from llm_config import simple_llm_call_async

# In your async functions:
response = await simple_llm_call_async(
    prompt="Your prompt",
    model="gpt-4o-mini"
)
```

## Monitoring & Debugging

### View Logs:
```bash
# Latest log
cat logs/llm/$(ls -t logs/llm/ | head -1) | jq

# All logs
ls -lh logs/llm/

# Find errors
grep -l '"success": false' logs/llm/*.json

# Token usage
jq -s '[.[].response.usage.total_tokens] | add' logs/llm/*.json
```

### Debug Output:
- Console shows detailed LiteLLM operations
- Each request/response is logged
- Errors include full stack traces
- Token usage is tracked

## Security Considerations

1. **API Keys**: Stored in `.env`, not in git
2. **Logs**: May contain sensitive data, in `.gitignore`
3. **CORS**: Enabled for development, restrict in production
4. **Authentication**: Add API authentication for production use
5. **Rate Limiting**: Consider adding rate limits

## Performance

- **Async Operations**: Non-blocking I/O
- **Streaming Support**: Available for long responses
- **Connection Pooling**: Handled by LiteLLM
- **Caching**: Can be added via LiteLLM cache

## Scalability

- **Horizontal**: Multiple API server instances
- **Vertical**: Async handles concurrent requests
- **Database**: SQLite → PostgreSQL for production
- **Logs**: Rotate/archive old logs regularly

## Cost Tracking

Each log includes token usage:
- `prompt_tokens`: Input cost
- `completion_tokens`: Output cost
- `total_tokens`: Total cost

Use logs to calculate monthly spend per model.
