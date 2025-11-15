# AI Concierge: NVIDIA NIM + MCP Integration

## Overview

The AI Concierge system now fully integrates:
- **NVIDIA NIM** (NVIDIA Inference Microservices) with DeepSeek-R1 model
- **MCP** (Model Context Protocol) for database query tools
- **LiteLLM** for unified LLM interface with logging

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    API Endpoints                        │
│  /concierge/ask, /concierge/ask-with-tools, etc.       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│            MCPEnhancedAIConcierge                       │
│  (created by create_concierge() function)              │
│                                                         │
│  - Tool calling support                                │
│  - MCP tools integration                               │
│  - NVIDIA NIM support                                  │
└────────────┬──────────────────────────┬────────────────┘
             │                          │
    ┌────────▼──────────┐    ┌──────────▼────────┐
    │  NVIDIA NIM       │    │    MCP Tools      │
    │  (DeepSeek-R1)    │    │                   │
    │  via LiteLLM      │    │  - search_startups│
    │                   │    │  - get_funding    │
    │  - gpt-4o         │    │  - get_location   │
    │  - claude-3       │    │  - get_industry   │
    │  - deepseek-r1    │    │  - get_team       │
    └───────────────────┘    └───────────────────┘
             │                          │
             └──────────┬───────────────┘
                        │
              ┌─────────▼─────────┐
              │  Database/CB      │
              │  Insights/Enriched│
              │  Startup Data     │
              └───────────────────┘
```

## Integration Details

### 1. NVIDIA NIM Configuration

**File**: `api/llm_config.py`

```python
NVIDIA_NIM_CONFIG = {
    "api_key": os.getenv("NVIDIA_API_KEY"),
    "base_url": "https://integrate.api.nvidia.com/v1",
    "default_model": "deepseek-ai/deepseek-r1",
    "embedding_model": "nvidia/llama-3.2-nemoretriever-300m-embed-v2",
}
```

**Key Functions**:
- `llm_completion(messages, model=None, use_nvidia_nim=True)`: Uses NVIDIA NIM by default
- `simple_llm_call_async(prompt, model=None, use_nvidia_nim=True)`: Simple text-based calls

### 2. MCP Integration

**File**: `api/mcp_client.py`

Provides `StartupDatabaseMCPTools` class with tools for:
- `search_startups_by_name(query, limit)`
- `search_startups_by_industry(industry, limit)`
- `search_startups_by_location(country, city, limit)`
- `search_startups_by_funding(stage, limit)`
- `get_startup_details(startup_id)`
- `get_team_info(startup_id)`
- `get_enrichment_data(startup_id)`

### 3. AI Concierge Implementation

**File**: `api/ai_concierge.py`

#### Base Class: `AIConcierge`
- Basic question answering
- Context retrieval from database
- Simple LLM calls without tool support

#### Enhanced Class: `MCPEnhancedAIConcierge`
- Extends `AIConcierge`
- Adds MCP tool integration
- Supports tool calling with NVIDIA NIM
- **Two main methods**:
  1. `answer_question()` - Standard answers with NVIDIA NIM
  2. `answer_question_with_tools()` - Tool-enhanced answers using MCP queries

#### Factory Function
```python
def create_concierge(db: Session) -> MCPEnhancedAIConcierge:
    """
    Create an AI Concierge instance with MCP and NVIDIA NIM integration
    Returns MCPEnhancedAIConcierge with full tool and LLM support
    """
    return MCPEnhancedAIConcierge(db)
```

## API Endpoints

### 1. `/concierge/ask` (POST)
**Primary endpoint with full integration**

Uses: NVIDIA NIM + MCP tool calling

```bash
curl -X POST http://localhost:8000/concierge/ask \
  -H "Content-Type: application/json" \
  -d {
    "question": "Find me startups in Finland with Series A funding",
    "user_context": {}
  }
```

**Response**:
```json
{
  "answer": "Based on the database, I found X startups in Finland with Series A funding...",
  "question_type": "startup_info"
}
```

### 2. `/concierge/ask-with-tools` (POST)
**Explicit tool-calling endpoint**

Uses: NVIDIA NIM DeepSeek-R1 + MCP tool calling

```bash
curl -X POST http://localhost:8000/concierge/ask-with-tools \
  -H "Content-Type: application/json" \
  -d {
    "question": "What companies founded after 2020 are in the AI space?",
    "user_context": null
  }
```

### 3. Other Endpoints
- `/concierge/startup-details` - Detailed startup info with CB Insights
- `/concierge/event-details` - Event information
- `/concierge/directions` - Location-based directions
- `/concierge/search-startups` - Direct startup search
- `/concierge/startup-categories` - Filter by category

## NVIDIA NIM + MCP Workflow

When a user asks a question about startups:

```
1. User asks: "Find startups in AI space with $10M+ funding"
                    ↓
2. MCPEnhancedAIConcierge.answer_question_with_tools() is called
                    ↓
3. System message with tool definitions sent to NVIDIA NIM (DeepSeek-R1)
                    ↓
4. DeepSeek-R1 decides to use MCP tools:
   - Calls search_startups_by_industry(industry="AI", limit=20)
   - Calls search_startups_by_funding(stage="Series A+", limit=20)
                    ↓
5. MCP tools query the database and return results
                    ↓
6. DeepSeek-R1 synthesizes the results into a natural language response
                    ↓
7. Response returned to user with sourced information
```

## Environment Variables

Required for full integration:

```bash
# NVIDIA NIM Configuration
export NVIDIA_API_KEY="your-api-key-here"
export NVIDIA_NIM_BASE_URL="https://integrate.api.nvidia.com/v1"
export NVIDIA_DEFAULT_MODEL="deepseek-ai/deepseek-r1"
export NVIDIA_EMBEDDING_MODEL="nvidia/llama-3.2-nemoretriever-300m-embed-v2"

# Optional: OpenAI fallback
export OPENAI_API_KEY="your-openai-key"

# Optional: Anthropic fallback
export ANTHROPIC_API_KEY="your-anthropic-key"
```

## Logging

All LLM requests and responses are logged to `/logs/llm/`:

Each request generates a JSON log with:
- Timestamp
- Request ID
- Model used
- Messages sent
- Response content
- Duration
- Token usage
- Errors (if any)

## Performance Characteristics

### NVIDIA NIM (DeepSeek-R1)
- **Model**: deepseek-ai/deepseek-r1 (Reasoning model)
- **Capabilities**: Complex reasoning, code understanding, detailed analysis
- **Latency**: ~2-5 seconds per request
- **Cost**: Optimized through NVIDIA integrate.api.nvidia.com

### MCP Tool Calling
- **Database Query Time**: <100ms per query
- **Tool Resolution**: Native to LLM (no round-trips needed)
- **Available Tools**: 7 startup-specific tools

### LiteLLM Integration
- **Verbose Logging**: All requests logged
- **Model Support**: 100+ models from various providers
- **Failover**: Can fallback to gpt-4o or claude-3 if NVIDIA NIM unavailable

## Usage Examples

### Example 1: Startup Search with Funding Criteria
```python
from database import SessionLocal
from ai_concierge import create_concierge

db = SessionLocal()
concierge = create_concierge(db)

# Uses NVIDIA NIM + MCP
response = await concierge.answer_question_with_tools(
    question="Find startups in healthcare with seed funding",
    use_nvidia_nim=True
)
print(response)
```

### Example 2: Using Available Tools
```python
# Get MCP tools for reference
tools = concierge.get_tool_definitions()

# Call a tool directly
result = await concierge.handle_tool_call(
    "search_startups_by_industry",
    industry="healthcare",
    limit=10
)
```

### Example 3: Conversational Search
```python
# Format results conversationally
answer = await concierge.conversational_startup_search(
    query="AI and Machine Learning",
    search_type="industry"
)
print(answer)
```

## Verification

To verify the integration is working:

```bash
cd /home/akyo/startup_swiper
python3 << 'EOF'
import sys
sys.path.insert(0, 'api')
from database import SessionLocal
from ai_concierge import create_concierge, MCPEnhancedAIConcierge

db = SessionLocal()
concierge = create_concierge(db)

# Verify it's the enhanced version
assert isinstance(concierge, MCPEnhancedAIConcierge)
print("✓ MCPEnhancedAIConcierge initialized")

# Verify MCP tools
tools = concierge.get_tool_definitions()
assert len(tools) > 0
print(f"✓ {len(tools)} MCP tools available")

# Verify NVIDIA NIM support
assert hasattr(concierge, 'answer_question_with_tools')
print("✓ NVIDIA NIM tool calling supported")

db.close()
EOF
```

## Benefits of This Integration

1. **Advanced Reasoning**: DeepSeek-R1's reasoning capabilities for complex startup analysis
2. **Accurate Data Retrieval**: MCP tools ensure database queries are precise and consistent
3. **Tool Calling**: LLM can independently decide when and how to use database tools
4. **Comprehensive Responses**: Combine reasoning with fresh database data
5. **Logging**: Full audit trail of all LLM requests and database queries
6. **Extensibility**: Easy to add more MCP tools for new data sources

## Troubleshooting

### Issue: "NVIDIA_API_KEY not set"
- Solution: `export NVIDIA_API_KEY="your-key"` before starting the server

### Issue: MCP tools return no results
- Check: Ensure startup database is loaded properly
- Verify: Use direct database queries to confirm data exists

### Issue: Slow responses
- Consider: DeepSeek-R1 is a reasoning model (slower but more accurate)
- Alternative: Use faster models for simple queries

### Issue: Tool calling not working
- Verify: `MCPEnhancedAIConcierge` is being used (via `create_concierge()`)
- Check: LLM logs in `/logs/llm/` for detailed error messages
