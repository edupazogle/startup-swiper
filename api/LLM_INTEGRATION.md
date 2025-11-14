# LiteLLM Integration with Logging

This FastAPI application includes full LiteLLM integration with automatic logging of all LLM requests and responses.

## 🎯 Features

- **Universal LLM Support**: Works with OpenAI, Anthropic Claude, Google AI, Azure, Cohere, and 100+ LLM providers via LiteLLM
- **Automatic Logging**: All requests and responses are logged to `/logs/llm` folder
- **Debug Mode**: Full verbose logging enabled for debugging
- **Structured Logs**: JSON format with timestamps, request IDs, duration, tokens used
- **Error Tracking**: Failed requests are also logged with error details
- **Async Support**: Both sync and async LLM calls supported

## 📁 Log Structure

Each LLM call creates a JSON file in `/logs/llm/` with this structure:

```json
{
  "timestamp": "2025-11-14T10:30:45.123456",
  "request_id": "abc123-def456-ghi789",
  "model": "gpt-4o",
  "duration_ms": 1234.56,
  "request": {
    "messages": [
      {"role": "user", "content": "Your prompt here"}
    ],
    "metadata": {}
  },
  "response": {
    "content": "The LLM response...",
    "role": "assistant",
    "finish_reason": "stop",
    "usage": {
      "prompt_tokens": 45,
      "completion_tokens": 123,
      "total_tokens": 168
    },
    "model": "gpt-4o",
    "id": "chatcmpl-xyz"
  },
  "error": null,
  "success": true
}
```

Filename format: `YYYYMMDD_HHMMSS_microseconds_model_requestid.json`

Example: `20251114_103045_123456_gpt-4o_abc12345.json`

## 🚀 Setup

### 1. Install Dependencies

```bash
cd /home/akyo/startup_swiper/api
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# For OpenAI models (GPT-4, GPT-3.5, etc.)
OPENAI_API_KEY=sk-your-openai-key-here

# For Anthropic models (Claude)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional: Other providers
GOOGLE_API_KEY=your-google-key
COHERE_API_KEY=your-cohere-key
```

### 3. Start the API

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Simple LLM Call

```bash
POST /llm/simple
```

Basic LLM call with a single prompt.

**Request:**
```json
{
  "prompt": "Explain what a startup accelerator is",
  "model": "gpt-4o",
  "system_message": "You are a helpful assistant",
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response:**
```json
{
  "content": "A startup accelerator is...",
  "model": "gpt-4o"
}
```

**Example with cURL:**
```bash
curl -X POST http://localhost:8000/llm/simple \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are the key metrics for a SaaS startup?",
    "model": "gpt-4o-mini",
    "temperature": 0.7
  }'
```

### Chat LLM Call

```bash
POST /llm/chat
```

Full conversation with message history.

**Request:**
```json
{
  "messages": [
    {"role": "system", "content": "You are a startup advisor"},
    {"role": "user", "content": "How do I find product-market fit?"},
    {"role": "assistant", "content": "Product-market fit means..."},
    {"role": "user", "content": "What metrics should I track?"}
  ],
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "content": "For tracking product-market fit...",
  "model": "gpt-4o"
}
```

**Example with cURL:**
```bash
curl -X POST http://localhost:8000/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant"},
      {"role": "user", "content": "Tell me about Y Combinator"}
    ],
    "model": "gpt-4o-mini"
  }'
```

## 🔧 Using Different Models

LiteLLM supports many providers. Just change the `model` parameter:

### OpenAI Models
- `gpt-4o` - Latest GPT-4 Omni
- `gpt-4o-mini` - Faster, cheaper GPT-4
- `gpt-4` - GPT-4
- `gpt-3.5-turbo` - GPT-3.5

### Anthropic Claude
- `claude-3-5-sonnet-20241022` - Claude 3.5 Sonnet
- `claude-3-opus-20240229` - Claude 3 Opus
- `claude-3-sonnet-20240229` - Claude 3 Sonnet

### Google AI
- `gemini-1.5-pro` - Gemini Pro
- `gemini-1.5-flash` - Gemini Flash

### Azure OpenAI
- `azure/gpt-4` - Azure-hosted GPT-4

## 🧪 Testing

Run the test suite:

```bash
python test_llm.py
```

This will:
1. Test the simple LLM endpoint
2. Test the chat endpoint
3. Test with system messages
4. Verify log files are created
5. Show a sample log file

## 📊 Monitoring Logs

### View all logs:
```bash
ls -lh logs/llm/
```

### View latest log:
```bash
cat logs/llm/$(ls -t logs/llm/ | head -1) | jq
```

### Count total requests:
```bash
ls logs/llm/*.json | wc -l
```

### Find errors:
```bash
grep -l '"success": false' logs/llm/*.json
```

### Calculate total tokens used:
```bash
jq -s '[.[].response.usage.total_tokens] | add' logs/llm/*.json
```

## 🔐 Security

- Never commit `.env` file (it's in `.gitignore`)
- Logs may contain sensitive data - keep `/logs` in `.gitignore`
- API keys are read from environment variables
- Use proper authentication in production

## 🛠️ Integration with Frontend

### JavaScript/TypeScript Example:

```typescript
// Simple call
async function callLLM(prompt: string) {
  const response = await fetch('http://localhost:8000/llm/simple', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: prompt,
      model: 'gpt-4o-mini',
      temperature: 0.7
    })
  });
  
  const data = await response.json();
  return data.content;
}

// Chat call
async function chatLLM(messages: Array<{role: string, content: string}>) {
  const response = await fetch('http://localhost:8000/llm/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: messages,
      model: 'gpt-4o',
      temperature: 0.7
    })
  });
  
  const data = await response.json();
  return data.content;
}
```

### Python Example:

```python
import requests

def call_llm(prompt: str, model: str = "gpt-4o-mini"):
    response = requests.post(
        "http://localhost:8000/llm/simple",
        json={
            "prompt": prompt,
            "model": model,
            "temperature": 0.7
        }
    )
    return response.json()["content"]
```

## 📈 Cost Tracking

Each log file includes token usage:
- `prompt_tokens`: Tokens in your request
- `completion_tokens`: Tokens in the response
- `total_tokens`: Sum of both

Use this data to track API costs across different models.

## 🐛 Debugging

LiteLLM verbose mode is enabled by default. Check terminal output for detailed logs.

To increase logging:
```python
import litellm
litellm.set_verbose = True
```

Common issues:
1. **API Key not found**: Check `.env` file and environment variables
2. **Model not found**: Verify model name is correct for your provider
3. **Rate limits**: Logs will show 429 errors - implement retry logic
4. **No logs created**: Check write permissions on `/logs/llm` folder

## 📝 Project Structure

```
api/
├── main.py              # FastAPI app with LLM endpoints
├── llm_config.py        # LiteLLM configuration and logging
├── database.py          # Database connection
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── crud.py              # CRUD operations
├── requirements.txt     # Dependencies
├── test_llm.py          # Test suite
├── .env.example         # Example environment file
├── .env                 # Your API keys (not in git)
└── logs/
    └── llm/             # LLM request/response logs
        ├── 20251114_103045_123456_gpt-4o_abc12345.json
        ├── 20251114_103050_654321_claude-3_def67890.json
        └── ...
```

## 🎓 Advanced Usage

### Custom Metadata

Add custom metadata to logs:

```python
from llm_config import llm_completion

response = await llm_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-4o",
    metadata={
        "user_id": 123,
        "session_id": "abc123",
        "feature": "startup_recommendations"
    }
)
```

### Streaming Responses

```python
from llm_config import llm_completion

async for chunk in llm_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-4o",
    stream=True
):
    print(chunk.choices[0].delta.content, end="")
```

### Error Handling

```python
from llm_config import simple_llm_call_async

try:
    response = await simple_llm_call_async(
        prompt="Your prompt",
        model="gpt-4o"
    )
    print(response)
except Exception as e:
    print(f"LLM call failed: {e}")
    # Error is automatically logged to /logs/llm
```

## 📄 License

See main project LICENSE file.
