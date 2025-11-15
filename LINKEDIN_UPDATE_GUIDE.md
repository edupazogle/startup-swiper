# LinkedIn Post Generator - Enhanced with Clarification Questions

## ✨ What's New

The LinkedIn Post Generator now includes an **intelligent clarification questions workflow** that ensures the agent gathers all necessary context before generating posts. This reduces revision cycles and creates more personalized, relevant content.

## 🎯 Key Feature: Adaptive Clarification Questions

When a user asks to write a LinkedIn post, the agent now:

1. **Detects** the request (recognizes 10+ LinkedIn post request phrases)
2. **Asks Smart Questions** about the topic, companies, tone, and goals
3. **Listens** to the user's responses
4. **Generates** a customized post based on gathered context

## 🚀 How It Works

### Basic Flow
```
User: "Write a LinkedIn post about AI in insurance"
  ↓
Agent: [Asks 3-4 clarifying questions]
  ↓
User: [Provides details]
  ↓
Agent: [Generates professional post]
  ↓
User: [Shares on LinkedIn]
```

### Example Conversation

**User:** 
```
"I want to write a LinkedIn post about AI in insurance"
```

**Agent Response:**
```
Here are 3 quick questions to shape your post:

1. Focus first - Are you highlighting a specific angle like 
   AI-driven claims processing, customer personalization, or 
   fraud detection? Or is this a broader thought leadership piece?

2. Names matter - Should we mention any insurance players 
   (e.g., Lemonade, Allstate) or AI tools? Any personal 
   experiences with AI in insurance?

3. Vibe check - Casual and curious or authoritative with stats?

Let me know and we'll craft something punchy! 🚀
```

**User Response:**
```
Focus: AI claims processing automation at AXA
Companies: Mention AXA and how we're innovating
Tone: Authoritative with statistics (40% cost reduction)
```

**Agent Generates:**
```
[Full professional LinkedIn post tailored to the user's specifics]
```

## 🔍 Request Detection

The agent recognizes all these phrases as LinkedIn post requests:

- "write a linkedin post"
- "write linkedin post"
- "create linkedin post"
- "generate linkedin post"
- "write a post"
- "create a post"
- "help me write a post"
- And 3+ more variations

## 📝 Implementation Details

### New Method: `_ask_linkedin_clarification_questions()`
- **Location:** `api/ai_concierge.py`
- **Purpose:** Generates context-gathering questions
- **Uses:** NVIDIA NIM DeepSeek-R1 LLM
- **Temperature:** 0.7 (balanced for conversational tone)
- **Max Tokens:** 800 (fits within single response)

### Updated Methods
1. **`answer_question()`** - Now checks for LinkedIn post requests first
2. **`answer_question_with_tools()`** - Routes LinkedIn requests to clarification flow
3. **`_classify_question()`** - Added "linkedin_post" classification

### Request Models
- **LinkedInPostRequest** - For direct generation with full details
- **ConciergeRequest** - For conversational requests with optional context

## 💡 Benefits

✅ **Comprehensive Context** - Gathers all details before generation
✅ **Personalized Posts** - Reflects user's specific perspective
✅ **Fewer Revisions** - Upfront details reduce edit cycles
✅ **Conversational** - Natural, engaging question flow
✅ **Intelligent** - LLM-powered adaptive questions
✅ **Flexible** - Works with or without initial topic
✅ **Professional** - Maintains VC partner persona throughout

## 🔄 Workflow Modes

### Mode 1: Conversational (Recommended for Interactive Use)
```
POST /concierge/ask
Request: {"question": "Help me write a LinkedIn post about Web3"}
Response: [Clarifying questions]
Follow-up: {"question": "About our new fund announcement..."}
Response: [Full post]
```

### Mode 2: Direct Generation (For API Automation)
```
POST /concierge/generate-linkedin-post
Request: {
  "topic": "...",
  "key_points": [...],
  "people_companies_to_tag": [...],
  "call_to_action": "...",
  "link": "..."
}
Response: [Full post generated directly]
```

### Mode 3: Tool-Enhanced (With MCP Integration)
```
POST /concierge/ask-with-tools
Request: {"question": "Write a post about Slush 2025"}
Response: [Clarifying questions with startup context]
```

## 📚 Documentation Files

1. **LINKEDIN_QUICKSTART.md** - Quick reference guide
2. **LINKEDIN_POST_GENERATOR.md** - Comprehensive feature guide
3. **LINKEDIN_WORKFLOW_GUIDE.md** - Workflow diagrams and flows
4. **LINKEDIN_FEATURE_SUMMARY.md** - Technical implementation details

## 🧪 Example Files

1. **examples_linkedin_posts.py** - 5 standalone examples
2. **examples_linkedin_workflow.py** - Interactive workflow demonstration
3. **LINKEDIN_WORKFLOW_GUIDE.md** - Complete workflow scenarios

## 🚀 Usage Examples

### Example 1: Generic Post Request
```python
from ai_concierge import create_concierge
from database import SessionLocal
import asyncio

async def example():
    db = SessionLocal()
    concierge = create_concierge(db)
    
    # User asks for a post
    response = await concierge.answer_question("Write a LinkedIn post")
    print(response)  # Agent asks clarifying questions
    
    # User provides details via follow-up question
    response2 = await concierge.answer_question(
        "I want to write about AI in finance, "
        "mention Fintech Inc and focus on automation"
    )
    print(response2)  # Agent generates full post

asyncio.run(example())
```

### Example 2: Direct Generation
```python
post = await concierge.generate_linkedin_post(
    topic="Series A Announcement",
    key_points=[
        "$25M funding raised",
        "AI infrastructure focus",
        "Global expansion plans"
    ],
    people_companies_to_tag=["@OurVC", "@TechLeader"],
    call_to_action="Join us in building the future",
    link="https://press-release.com"
)
print(post)  # Full post ready to share
```

### Example 3: API Call
```bash
# Conversational approach
curl -X POST http://localhost:8000/concierge/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "help me write a linkedin post about our new product"}'

# Direct generation
curl -X POST http://localhost:8000/concierge/generate-linkedin-post \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Product launch announcement",
    "key_points": ["New AI features", "Enterprise ready", "Launch date Q1"],
    "people_companies_to_tag": ["@Company"],
    "call_to_action": "Be first in line!",
    "link": "https://product.com"
  }'
```

## 🔧 Technical Specifications

| Aspect | Details |
|--------|---------|
| **LLM Model** | NVIDIA NIM - DeepSeek-R1 |
| **Question Temperature** | 0.7 (conversational) |
| **Generation Temperature** | 0.8 (creative) |
| **Max Tokens (Questions)** | 800 |
| **Max Tokens (Posts)** | 2500 |
| **Response Time** | 10-15 seconds |
| **Async** | ✅ Fully async |
| **Caching** | Supported via LiteLLM |

## 📊 Git Commits

1. **feat: add LinkedIn post clarification questions workflow**
   - Core implementation of clarification questions
   - Updated answer_question() and answer_question_with_tools()
   - Added _ask_linkedin_clarification_questions() method

2. **docs: add LinkedIn workflow guide**
   - Comprehensive workflow diagrams
   - Request detection keywords
   - Clarification question examples
   - Two-way interaction patterns

## ✅ What's Tested

- ✅ Request detection with 10+ phrase variations
- ✅ Clarification questions generation via NVIDIA NIM
- ✅ Python syntax validation
- ✅ Frontend build successful (no errors)
- ✅ Both answer_question() and answer_question_with_tools() paths
- ✅ Direct post generation with full details
- ✅ API endpoint responses

## 🎯 Next Steps

Users can now:

1. **Ask naturally** - "Help me write a post about..."
2. **Get guidance** - Agent asks smart clarifying questions
3. **Provide context** - Answer questions with details
4. **Generate posts** - Agent creates professional content
5. **Share directly** - Copy-paste ready LinkedIn posts

## 💬 Example Interactions

### Startup Announcement
```
User: "Write a post about our Series B"
Agent: [Clarifying questions about funding amount, investors, focus]
User: [Provides: $50M, led by top VC, AI infrastructure]
Agent: [Generates compelling announcement post]
```

### Thought Leadership
```
User: "Help write a LinkedIn post about blockchain"
Agent: [Questions about specific angle, tone, audience]
User: [Provides: Enterprise adoption, data-driven, industry focus]
Agent: [Generates authoritative insights post]
```

### Event Recap
```
User: "Create a post about Slush 2025"
Agent: [Questions about key takeaways, companies met, main learning]
User: [Provides: AI startups dominating, team recommendations, future trends]
Agent: [Generates conference recap post]
```

---

## 🎉 Summary

The LinkedIn Post Generator now features:

✨ **Intelligent Clarification Questions** - Gathers context before generation
✨ **Conversational Flow** - Natural interaction pattern
✨ **Adaptive Questions** - Different questions for different requests
✨ **Professional Output** - VC-grade posts every time
✨ **Flexible Usage** - Works as Q&A or direct generation
✨ **Well-Documented** - Multiple guides and examples
✨ **Production-Ready** - Tested and validated

**Get started today:** Just ask the agent *"Help me write a LinkedIn post"* and let the conversation flow! 🚀

Version 2.0 • November 16, 2025 • AI Concierge System
