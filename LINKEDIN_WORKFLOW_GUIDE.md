# LinkedIn Post Generator - Clarification Questions Workflow

## 🎯 Interactive Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INITIATES REQUEST                        │
│                                                                      │
│  👤 "Write a LinkedIn post about AI in insurance"                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   AGENT DETECTS LINKEDIN REQUEST                    │
│                                                                      │
│  🤖 Recognizes: "linkedin post", "write a post", "create post", etc │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              AGENT ASKS CLARIFYING QUESTIONS                         │
│                                                                      │
│  🤖 "Here are 3-4 questions to help shape your post:               │
│                                                                      │
│  1️⃣ Focus first - Are you highlighting a specific angle like       │
│     AI-driven claims processing, or broader thought leadership?     │
│                                                                      │
│  2️⃣ Names matter - Should we mention any insurance players or      │
│     companies? Any personal experiences?                           │
│                                                                      │
│  3️⃣ Vibe check - Casual and curious tone or authoritative with    │
│     statistics?                                                     │
│                                                                      │
│  Let me know and we'll craft something punchy! 🚀"                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  USER RESPONDS WITH DETAILS                          │
│                                                                      │
│  👤 "Focus on claims processing, mention AXA's 40% cost reduction, │
│      and use an authoritative tone with statistics"                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              AGENT GENERATES PROFESSIONAL POST                       │
│                                                                      │
│  🤖 "[Full LinkedIn post with:                                     │
│      - Hook with relevant emoji                                    │
│      - AXA context and relevance                                   │
│      - Claims processing details                                   │
│      - 40% cost reduction statistics                               │
│      - Authoritative tone                                          │
│      - Hashtags and CTA]"                                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   USER COPIES & SHARES ON LINKEDIN                   │
│                                                                      │
│  👤 [Copies full post and shares on LinkedIn profile]              │
└─────────────────────────────────────────────────────────────────────┘
```

## 📋 Request Detection Keywords

The agent automatically detects LinkedIn post requests with these phrases:

- "write a linkedin post"
- "write linkedin post"
- "create linkedin post"
- "generate linkedin post"
- "linkedin post"
- "write a post"
- "write post"
- "create a post"
- "generate post"

## 🎤 Clarification Questions Examples

### For General Requests
```
1. What's the main purpose?
   - Startup/product launch
   - Key industry insight
   - Career milestone
   - Something else?

2. Who needs a shoutout?
   - Specific people or companies?
   - Team mentions?
   - Partner references?

3. What's the #1 thing you want people to remember?
   - A lesson learned?
   - A call to action?
   - A reason to celebrate?

4. Casual or polished?
   - Fun/energetic tone?
   - Formal/professional tone?
```

### For Topic-Specific Requests
```
1. Focus first
   - Specific angle (e.g., claims processing, fraud detection)
   - Broader thought leadership
   - Personal experience

2. Names matter
   - Specific companies or tools to mention
   - Real examples or case studies
   - Personal experiences with the topic

3. Vibe check
   - Data-driven and authoritative
   - Casual and conversational
   - Mix of both
```

## 🔄 Two-Way Interaction Flow

### Option 1: Natural Conversation Flow
```
User: "Help me write a LinkedIn post"
    ↓
Agent: [Asks clarifying questions]
    ↓
User: [Answers questions]
    ↓
Agent: [Generates professional post]
    ↓
User: [Copies and shares]
```

### Option 2: Direct Generation (If Details Available)
```
User: Uses /concierge/generate-linkedin-post API
      with topic + key_points + tags + CTA
    ↓
Agent: [Generates post directly]
    ↓
User: [Copies and shares]
```

## 💡 Key Benefits

✅ **Gathers Context**: Questions ensure all needed details are collected
✅ **Personalized Posts**: Final post reflects user's unique perspective
✅ **Reduces Revisions**: Upfront details mean fewer edit cycles
✅ **Conversational**: Questions feel natural and engaging
✅ **Flexible**: Works with or without initial topic
✅ **Professional**: LLM-powered questions are insightful
✅ **Adaptive**: Questions adjust based on initial request

## 📊 Conversation Flow Diagram

```
START
  │
  ├─→ User asks for LinkedIn post
  │
  ├─→ Agent detects request type
  │   ├─→ Generic request? → Ask general questions
  │   ├─→ Topic mentioned? → Ask topic-specific questions
  │   └─→ Full details? → Go straight to generation
  │
  ├─→ User provides responses
  │
  ├─→ Agent generates post using:
  │   ├─ Clarification answers
  │   ├─ Topic information
  │   ├─ VC partner persona
  │   ├─ NVIDIA NIM LLM
  │   └─ 7-part structured format
  │
  ├─→ User receives polished post
  │
  └─→ User shares on LinkedIn
     END
```

## 🚀 Getting Started

### Via Chat/Natural Language
Simply ask the agent:
```
"I want to write a LinkedIn post about our new funding round"
```

The agent will respond with clarifying questions. Answer them, and you'll get a professional post!

### Via API (Direct Generation)
If you have all details, use the endpoint directly:
```bash
curl -X POST http://localhost:8000/concierge/generate-linkedin-post \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Your specific topic",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "people_companies_to_tag": ["@Company1", "@Person1"],
    "call_to_action": "Your desired CTA",
    "link": "https://your-link.com"
  }'
```

## 🎯 Pro Tips

1. **Be Specific**: The more details you provide in answers, the better the post
2. **Mention Companies**: Including company names helps add credibility
3. **Include Data**: Statistics and numbers make posts more compelling
4. **Clear Goals**: Know what you want readers to do (visit link, reply, share, etc.)
5. **Authentic Voice**: Use your real perspective - the agent builds on it

## ❓ FAQ

**Q: What if I want to go straight to generation?**
A: Use the `/concierge/generate-linkedin-post` API endpoint with all details provided.

**Q: Can I modify the generated post?**
A: Yes! The posts are copy-paste ready but feel free to edit for your specific style.

**Q: Does the agent understand startup context?**
A: Yes! The agent has access to startup database and can reference it in questions.

**Q: What tone does the agent use for questions?**
A: Conversational, friendly, and non-overwhelming - typically 3-4 key questions.

---

**Ready to write your next LinkedIn post?** Just ask the agent: *"Help me write a LinkedIn post"* and let the conversation flow! 🚀
