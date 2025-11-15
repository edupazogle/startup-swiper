"""
AI Concierge MCP Integration Guide

Complete guide for setting up and using the MCP (Model Context Protocol) integrated
AI Concierge with NVIDIA NIM support for startup information extraction.
"""

# AI Concierge with MCP and NVIDIA NIM Setup Guide

## Overview

The AI Concierge system is now enhanced with:
- **LiteLLM Integration**: Unified LLM interface supporting multiple providers
- **NVIDIA NIM Support**: Optimized inference using DeepSeek and other models via NVIDIA's infrastructure
- **MCP Server**: Model Context Protocol server for database-backed startup queries
- **Tool Calling**: LLM function calling to dynamically extract startup information

## Architecture

```
┌─────────────────────────────────────┐
│     Frontend (React/TypeScript)     │
│        AI Assistant Chat UI         │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│       API Server (FastAPI)          │
│    - /api/concierge/ask             │
│    - /api/concierge/tools           │
└────────────────┬────────────────────┘
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
┌─────────────────┐  ┌──────────────────┐
│  LiteLLM        │  │  MCP Client      │
│  (with NVIDIA   │  │                  │
│   NIM support)  │  │  - search_by_name
│                 │  │  - search_by_industry
│  - Async calls  │  │  - get_details
│  - Logging      │  │  - search_by_funding
│  - Model select │  │  - search_by_location
└─────────────────┘  └────────┬─────────┘
       │                      │
       │                      ▼
       │            ┌──────────────────────┐
       │            │ SQLite/PostgreSQL DB │
       │            │ (Startup Data)       │
       │            └──────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  NVIDIA NIM (inference.nvidia.com)  │
│  - deepseek-ai/deepseek-r1         │
│  - Other available models           │
└─────────────────────────────────────┘
```

## Installation

### 1. Install Dependencies

```bash
cd /home/akyo/startup_swiper
pip install -r api/requirements.txt
```

Key new packages:
- `mcp>=1.1.4` - Model Context Protocol SDK
- `litellm>=1.44.28` - Already included, but now with full NVIDIA NIM support

### 2. Configure Environment Variables

Update `/home/akyo/startup_swiper/api/.env`:

```env
# NVIDIA NIM Configuration (required)
NVIDIA_API_KEY=nvapi-...
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_DEFAULT_MODEL=deepseek-ai/deepseek-r1
NVIDIA_EMBEDDING_MODEL=nvidia/llama-3.2-nemoretriever-300m-embed-v2

# Optional: Alternative LLM providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Or update `/home/akyo/startup_swiper/app/startup-swipe-schedu/.env` if running frontend:

```env
NVIDIA_API_KEY=nvapi-...
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_DEFAULT_MODEL=deepseek-ai/deepseek-r1
```

## Usage

### Using the MCP-Enhanced AI Concierge

```python
from sqlalchemy.orm import Session
from ai_concierge import create_mcp_concierge

# Create MCP-enhanced concierge
db: Session = get_db()
concierge = create_mcp_concierge(db)

# Get available tools
tools = concierge.get_tool_definitions()

# Answer questions with tool support
response = await concierge.answer_question_with_tools(
    question="Tell me about AI startups in Finland with Series A funding",
    use_nvidia_nim=True
)

# Or use specific search
result = await concierge.conversational_startup_search(
    query="AI",
    search_type="industry"
)
```

### API Endpoints (FastAPI)

The main API server should expose:

```python
@app.post("/api/concierge/ask")
async def ask_concierge(
    question: str,
    use_mcp: bool = True,
    use_nvidia_nim: bool = True
):
    """Answer a question using AI Concierge with optional MCP/NVIDIA NIM"""
    db = SessionLocal()
    
    if use_mcp:
        concierge = create_mcp_concierge(db)
        response = await concierge.answer_question_with_tools(
            question=question,
            use_nvidia_nim=use_nvidia_nim
        )
    else:
        concierge = create_concierge(db)
        response = await concierge.answer_question(question)
    
    return {"response": response}


@app.get("/api/concierge/tools")
async def get_concierge_tools():
    """Get available MCP tools for the LLM"""
    db = SessionLocal()
    concierge = create_mcp_concierge(db)
    tools = concierge.get_tool_definitions()
    
    return {"tools": tools}
```

## Available MCP Tools

The AI Concierge can use these tools to query the startup database:

### 1. Search Startups by Name
```python
{
    "name": "search_startups_by_name",
    "description": "Search for startups by company name",
    "parameters": {
        "query": "string (company name)",
        "limit": "integer (default: 10)"
    }
}
```

### 2. Search Startups by Industry
```python
{
    "name": "search_startups_by_industry",
    "description": "Search for startups in a specific industry",
    "parameters": {
        "industry": "string (e.g., AI, Fintech, Biotech)",
        "limit": "integer (default: 10)"
    }
}
```

### 3. Get Startup Details
```python
{
    "name": "get_startup_details",
    "description": "Get detailed information about a specific startup",
    "parameters": {
        "startup_id": "integer (optional)",
        "company_name": "string (optional)"
    }
}
```

### 4. Search by Funding Stage
```python
{
    "name": "search_startups_by_funding",
    "description": "Search for startups by funding stage",
    "parameters": {
        "stage": "string (e.g., Seed, Series A, Series B)",
        "min_funding": "number (optional, in millions)",
        "limit": "integer (default: 10)"
    }
}
```

### 5. Search by Location
```python
{
    "name": "search_startups_by_location",
    "description": "Search for startups by country or city",
    "parameters": {
        "country": "string (required)",
        "city": "string (optional)",
        "limit": "integer (default: 10)"
    }
}
```

### 6. Get Startup Enrichment Data
```python
{
    "name": "get_startup_enrichment_data",
    "description": "Get enriched data (team, tech stack, social media)",
    "parameters": {
        "startup_id": "integer (optional)",
        "company_name": "string (optional)"
    }
}
```

### 7. Get Top Funded Startups
```python
{
    "name": "get_top_startups_by_funding",
    "description": "Get the top funded startups",
    "parameters": {
        "limit": "integer (default: 10)"
    }
}
```

## LiteLLM Configuration

### Supported Models via NVIDIA NIM

The system is configured to use NVIDIA NIM models, particularly:

- **deepseek-ai/deepseek-r1** (Default reasoning model)
- **nvidia/llama-3.2-nemoretriever-300m-embed-v2** (Embeddings)

Other available models can be used by changing `NVIDIA_DEFAULT_MODEL`.

### Model Format

LiteLLM supports these formats for NVIDIA NIM:
```python
# Direct NIM model (auto-routes to NVIDIA endpoint)
model = "deepseek-ai/deepseek-r1"

# Or specific endpoints
model = "nvidia_nim/deepseek-ai/deepseek-r1"
```

### Async vs Sync

```python
# Async (recommended for FastAPI)
response = await llm_completion(
    messages=[{"role": "user", "content": "..."}],
    model=None,  # Uses NVIDIA default
    use_nvidia_nim=True
)

# Sync
response = llm_completion_sync(
    messages=[{"role": "user", "content": "..."}],
    model=None,  # Uses NVIDIA default
    use_nvidia_nim=True
)
```

## Logging

All LLM requests and responses are logged to `/home/akyo/startup_swiper/logs/llm/`:

```
logs/llm/
├── 20240115_120530_deepseek-ai_deepseek-r1_abc12345.json
├── 20240115_120645_deepseek-ai_deepseek-r1_def67890.json
└── ...
```

Each log file contains:
- Request messages
- Response content
- Token usage
- Latency
- Any errors

## MCP Server

The MCP Startup Server (`mcp_startup_server.py`) can be run standalone:

```bash
python api/mcp_startup_server.py
```

This exposes the startup database tools via the MCP protocol, allowing other clients to interact with the database.

## Testing

### Test Basic Concierge

```bash
python -m pytest api/test_concierge.py -v
```

### Test LLM Integration

```bash
python api/test_llm.py
```

### Test with MCP

```python
import asyncio
from api.ai_concierge import create_mcp_concierge
from api.database import SessionLocal

async def test_mcp():
    db = SessionLocal()
    concierge = create_mcp_concierge(db)
    
    # Get tools
    tools = concierge.get_tool_definitions()
    print(f"Available tools: {len(tools)}")
    
    # Answer question
    answer = await concierge.answer_question_with_tools(
        "What AI startups are in Finland?"
    )
    print(answer)
    
    db.close()

asyncio.run(test_mcp())
```

## Troubleshooting

### NVIDIA API Key Issues
```
Error: NVIDIA_API_KEY not set
Solution: 
1. Get API key from https://build.nvidia.com/
2. Set NVIDIA_API_KEY in .env
3. Restart the application
```

### LLM Call Timeouts
```
Error: Request timeout connecting to NVIDIA NIM
Solution:
1. Check internet connection
2. Verify NVIDIA API key is valid
3. Check NVIDIA_NIM_BASE_URL is correct
4. Try alternative LLM provider (OpenAI, Anthropic)
```

### MCP Tool Not Found
```
Error: Tool 'search_startups_by_name' not available
Solution:
1. Ensure ai_concierge.py is using MCPEnhancedAIConcierge
2. Verify database has startup data
3. Check database connection
```

### Database Connection
```
Error: Could not connect to database
Solution:
1. Verify database file exists: startup_swiper.db
2. Check DATABASE_URL in .env
3. Ensure database permissions are correct
4. Run migrations: alembic upgrade head
```

## Performance Optimization

### Caching Tool Results
```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_startup_by_name(name: str):
    """Cached startup lookup"""
    # ... database query ...
```

### Batch Tool Calls
```python
# Multiple searches at once
results = await asyncio.gather(
    concierge.mcp_tools.call_tool("search_startups_by_name", query="AI"),
    concierge.mcp_tools.call_tool("search_startups_by_industry", industry="Fintech"),
)
```

### Model Selection for Speed
For faster responses, use lighter models:
```python
# Fast + accurate
model = "mistral-7b"  # If available on NVIDIA NIM

# Or fallback to OpenAI mini model
model = "gpt-4o-mini"
```

## Production Deployment

### Docker Setup
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY api/requirements.txt .
RUN pip install -r requirements.txt

COPY api/ .

ENV NVIDIA_API_KEY=your-key-here
ENV NVIDIA_DEFAULT_MODEL=deepseek-ai/deepseek-r1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
# Production .env
NVIDIA_API_KEY=nvapi-...
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_DEFAULT_MODEL=deepseek-ai/deepseek-r1

DATABASE_URL=postgresql://user:pass@prod-db:5432/startup_swiper
LOG_LEVEL=INFO
LITELLM_DEBUG=false
```

## Further Reading

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [NVIDIA NIM Docs](https://docs.nvidia.com/nim/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [DeepSeek R1 Model Card](https://huggingface.co/deepseek-ai/deepseek-r1)

## Support

For issues or questions:
1. Check logs in `/logs/llm/`
2. Review error messages in console
3. Verify API keys and configuration
4. Check database connectivity
5. Review documentation above

---
Last Updated: 2025-01-15
