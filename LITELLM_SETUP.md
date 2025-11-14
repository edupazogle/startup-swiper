# 🚀 LiteLLM Integration - Complete Setup

## ✅ What Was Implemented

A complete **LiteLLM integration** with **automatic logging** of all LLM requests and responses to `/logs/llm`.

### Key Features:
- 🤖 **Universal LLM Support**: OpenAI, Anthropic Claude, Google Gemini, Azure, and 100+ providers
- 📝 **Automatic Logging**: Every request/response saved to JSON files in `/logs/llm/`
- 🔍 **Debug Mode Enabled**: Full verbose logging for debugging
- ⚡ **FastAPI Endpoints**: REST API for LLM calls
- 🔄 **Async Support**: Non-blocking I/O operations
- 📊 **Token Tracking**: Cost tracking for each request
- 🛡️ **Error Logging**: Failed requests logged with full details

## 📁 What Was Created

```
/home/akyo/startup_swiper/
├── api/
│   ├── llm_config.py              # ⭐ Core LiteLLM + logging module
│   ├── main.py                     # ⭐ Updated with LLM endpoints
│   ├── requirements.txt            # ⭐ Added litellm dependencies
│   ├── .env.example                # ⭐ API key template
│   ├── start.sh                    # ⭐ Quick start script
│   ├── test_llm.py                 # ⭐ Test suite
│   ├── examples_llm.py             # ⭐ Usage examples
│   ├── verify_installation.sh      # ⭐ Installation checker
│   ├── README.md                   # ⭐ Updated docs
│   ├── LLM_INTEGRATION.md          # ⭐ Detailed LLM guide
│   ├── ARCHITECTURE.md             # ⭐ System architecture
│   └── IMPLEMENTATION_SUMMARY.md   # ⭐ This summary
│
└── logs/
    └── llm/                        # ⭐ Log storage directory
        ├── .gitkeep                # Keeps folder in git
        ├── .gitignore              # Ignores log files
        └── (logs created here)     # JSON log files
```

## 🚀 Quick Start (3 Steps)

### 1. Setup Environment
```bash
cd /home/akyo/startup_swiper/api

# Copy environment template
cp .env.example .env

# Edit and add your API keys
nano .env
```

Add your API keys to `.env`:
```bash
OPENAI_API_KEY=sk-your-openai-key-here
# or
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Server
```bash
./start.sh
```

That's it! The API is now running at http://localhost:8000

## 📚 API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### LLM Endpoints

#### Simple LLM Call
```bash
curl -X POST http://localhost:8000/llm/simple \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain product-market fit in one sentence",
    "model": "gpt-4o-mini",
    "temperature": 0.7
  }'
```

#### Chat with History
```bash
curl -X POST http://localhost:8000/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant"},
      {"role": "user", "content": "What is a startup accelerator?"}
    ],
    "model": "gpt-4o"
  }'
```

## 🧪 Testing

Run the test suite:
```bash
cd /home/akyo/startup_swiper/api
python test_llm.py
```

Run examples:
```bash
python examples_llm.py
```

Verify installation:
```bash
./verify_installation.sh
```

## 📊 Viewing Logs

All LLM requests and responses are automatically logged to `/logs/llm/`:

```bash
# View all logs
ls -lh /home/akyo/startup_swiper/logs/llm/

# View latest log
cat /home/akyo/startup_swiper/logs/llm/$(ls -t /home/akyo/startup_swiper/logs/llm/ | head -1) | jq

# Count total requests
ls /home/akyo/startup_swiper/logs/llm/*.json 2>/dev/null | wc -l

# Find errors
grep -l '"success": false' /home/akyo/startup_swiper/logs/llm/*.json 2>/dev/null

# Calculate total tokens used
jq -s '[.[].response.usage.total_tokens] | add' /home/akyo/startup_swiper/logs/llm/*.json 2>/dev/null
```

### Log File Format

Each log is a JSON file named: `YYYYMMDD_HHMMSS_microseconds_model_requestid.json`

Example content:
```json
{
  "timestamp": "2025-11-14T10:30:45.123456",
  "request_id": "abc-123-def-456",
  "model": "gpt-4o-mini",
  "duration_ms": 1234.56,
  "request": {
    "messages": [{"role": "user", "content": "Your prompt"}],
    "metadata": {}
  },
  "response": {
    "content": "The response...",
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

## 🔧 Using in Your Code

### Python (Async)
```python
from llm_config import simple_llm_call_async

response = await simple_llm_call_async(
    prompt="Your prompt here",
    model="gpt-4o-mini"
)
print(response)
```

### Python (Sync)
```python
from llm_config import simple_llm_call

response = simple_llm_call(
    prompt="Your prompt here",
    model="gpt-4o-mini"
)
print(response)
```

### JavaScript/TypeScript
```typescript
async function callLLM(prompt: string, model: string = 'gpt-4o-mini') {
  const response = await fetch('http://localhost:8000/llm/simple', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, model })
  });
  const data = await response.json();
  return data.content;
}
```

## 🎯 Supported Models

### OpenAI
- `gpt-4o` - Latest GPT-4 Omni
- `gpt-4o-mini` - Fast and cost-effective
- `gpt-4` - Standard GPT-4
- `gpt-3.5-turbo` - GPT-3.5

### Anthropic
- `claude-3-5-sonnet-20241022` - Claude 3.5 Sonnet
- `claude-3-opus-20240229` - Claude 3 Opus
- `claude-3-sonnet-20240229` - Claude 3 Sonnet

### Google
- `gemini-1.5-pro` - Gemini Pro
- `gemini-1.5-flash` - Gemini Flash

### And 100+ more providers via LiteLLM!

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [README.md](api/README.md) | Main API documentation |
| [LLM_INTEGRATION.md](api/LLM_INTEGRATION.md) | Complete LLM usage guide |
| [ARCHITECTURE.md](api/ARCHITECTURE.md) | System architecture & diagrams |
| [IMPLEMENTATION_SUMMARY.md](api/IMPLEMENTATION_SUMMARY.md) | Implementation details |

## 🔐 Security Notes

- ✅ `.env` file is git-ignored (API keys safe)
- ✅ `logs/` directory is git-ignored (logs not committed)
- ⚠️  Add authentication for production use
- ⚠️  Logs may contain sensitive conversation data
- ⚠️  Never commit API keys to git

## 🎓 Advanced Features

### Custom Metadata
```python
response = await llm_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-4o",
    metadata={
        "user_id": 123,
        "feature": "chat",
        "session_id": "abc-123"
    }
)
```

### Streaming Responses
```python
async for chunk in llm_completion(
    messages=[{"role": "user", "content": "Write a story"}],
    model="gpt-4o",
    stream=True
):
    print(chunk.choices[0].delta.content, end="")
```

### Error Handling
```python
try:
    response = await simple_llm_call_async(prompt="test", model="gpt-4o")
except Exception as e:
    print(f"Error: {e}")
    # Error is automatically logged to /logs/llm/
```

## 💰 Cost Tracking

Each log includes token usage for cost calculation:
- `prompt_tokens`: Input tokens
- `completion_tokens`: Output tokens  
- `total_tokens`: Total (for cost calculation)

Use logs to track spending across different models and features.

## 🐛 Troubleshooting

### API Key Not Found
```bash
# Check .env file exists
ls -la api/.env

# Check if key is set
grep OPENAI_API_KEY api/.env
```

### Dependencies Not Installed
```bash
cd api
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Change port in start command
uvicorn main:app --reload --port 8001
```

### Logs Not Created
```bash
# Check directory permissions
ls -ld logs/llm/

# Create manually if needed
mkdir -p logs/llm
chmod 755 logs/llm
```

## 📞 Support

For issues or questions:
1. Check the documentation in `api/LLM_INTEGRATION.md`
2. Review architecture in `api/ARCHITECTURE.md`
3. Run verification: `./api/verify_installation.sh`
4. Check API logs for errors

## 🎉 What's Next?

Your LiteLLM integration is ready to use! 

**Next Steps:**
1. ✅ Add your API keys to `.env`
2. ✅ Start the server: `./api/start.sh`
3. ✅ Run tests: `python api/test_llm.py`
4. ✅ Try examples: `python api/examples_llm.py`
5. ✅ Check logs: `ls -lh logs/llm/`
6. ✅ Read docs: `api/LLM_INTEGRATION.md`

**Integration with Frontend:**
Update your React TypeScript code to call the new API endpoints instead of `window.spark.llm()`.

---

**All LLM requests and responses will be automatically logged to `/logs/llm/` with complete debugging information!** 🎊
