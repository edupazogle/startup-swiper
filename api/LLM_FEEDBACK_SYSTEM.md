# 🤖 LLM-Powered Feedback Collection System

## Overview

An intelligent, conversational system that uses LLM to collect structured meeting insights through natural chat interactions.

---

## 🎯 What It Does

### Before (Manual Form)
User clicks notification → Sees generic form → Fills 3 text boxes → Submits

### After (LLM Chat)
User clicks notification → Full-screen chat opens → LLM asks 3 smart questions → Natural conversation → Auto-saves insights

---

## 🧠 Key Features

### 1. **Context-Aware Questions**
LLM generates 3 specific questions based on:
- Startup name
- Startup description
- Meeting context
- Industry/category

**Example for "Hookle" (Marketing AI)**:
1. "What specific marketing automation capabilities did Hookle demonstrate that could benefit AXA?"
2. "How does their AI agent technology compare to current marketing tools at AXA?"
3. "What would be the recommended next steps for evaluating Hookle?"

### 2. **Conversational Flow**
- LLM asks questions one at a time
- Acknowledges answers warmly
- Can request clarification if answer is too brief
- Maintains natural conversation tone

### 3. **Structured Storage**
- Answers saved in structured Q&A format
- Tagged by category (technical/business/action)
- Fully editable after submission
- Linked to meeting and startup

### 4. **Auto-Generated Insights**
- Combines answers into formatted insight text
- Assigns rating based on answer quality
- Detects follow-up actions automatically
- Ready for team dashboards

---

## 📊 Database Schema

### New Table: `feedback_sessions`
```sql
- id: Primary key
- meetingId: Link to calendar event
- userId: Who's providing feedback
- startupId: Which startup
- startupName: Startup name
- questions: JSON array of 3 generated questions
- answers: JSON object of Q&A pairs
- conversation_history: Full chat transcript
- current_question_index: Progress tracker
- status: in_progress | completed | abandoned
- started_at, completed_at, last_interaction
```

### Updated Table: `meeting_insights`
```sql
+ structured_qa: JSON array of Q&A pairs (NEW!)
  - Enables editing individual answers
  - Preserves original questions
  - Shows answer categories
```

---

## 🚀 API Endpoints

### 1. Start Feedback Session
```http
POST /feedback/start
```

**Request**:
```json
{
  "meeting_id": "mtg_123",
  "user_id": "1",
  "startup_id": "hookle",
  "startup_name": "Hookle",
  "startup_description": "AI agents for micro-business marketing..."
}
```

**Response**:
```json
{
  "session_id": 42,
  "resumed": false,
  "message": "Thanks for taking a moment to share your insights! Let's capture the key takeaways from your meeting.\\n\\n**Question 1 of 3:**\\nWhat specific marketing automation capabilities did Hookle demonstrate?",
  "current_question": {
    "id": 1,
    "question": "What specific marketing automation capabilities...",
    "category": "technical",
    "placeholder": "Describe their key technology..."
  },
  "progress": {
    "current": 1,
    "total": 3,
    "answered": 0
  }
}
```

---

### 2. Send Chat Message
```http
POST /feedback/chat
```

**Request**:
```json
{
  "session_id": 42,
  "message": "They showed autonomous social media posting across 5 platforms with AI-generated content that adapts to each platform's style."
}
```

**Response**:
```json
{
  "response": "Great insight! That cross-platform capability with adaptive content sounds powerful.\\n\\n**Question 2 of 3:**\\nWhat specific business value could Hookle provide to AXA?",
  "question_id": 2,
  "current_question": {
    "id": 2,
    "question": "What specific business value...",
    "category": "business"
  },
  "progress": {
    "current": 2,
    "total": 3,
    "answered": 1
  },
  "session_id": 42,
  "completed": false
}
```

**Final Response (After Q3)**:
```json
{
  "response": "Perfect! Your insights about Hookle have been saved. You can review or edit them anytime from the insights section. Thanks for sharing!",
  "question_id": null,
  "current_question": null,
  "progress": {
    "current": 3,
    "total": 3,
    "answered": 3
  },
  "session_id": 42,
  "completed": true
}
```

---

### 3. Get Session Details
```http
GET /feedback/session/{session_id}
```

Returns full session including conversation history and all answers.

---

### 4. Edit Insight
```http
PUT /insights/{insight_id}/edit
```

**Request**:
```json
{
  "updated_qa": [
    {
      "id": 1,
      "question": "What technical capabilities...",
      "answer": "UPDATED: They showed even more impressive multi-agent coordination...",
      "category": "technical"
    },
    {
      "id": 2,
      "question": "What business value...",
      "answer": "Could reduce marketing team workload by 60%...",
      "category": "business"
    },
    {
      "id": 3,
      "question": "What next steps...",
      "answer": "Schedule product demo for marketing team...",
      "category": "action"
    }
  ]
}
```

---

### 5. Preview Questions
```http
GET /feedback/preview/{meeting_id}?startup_name=Hookle&startup_description=...
```

Shows what questions would be generated without creating a session.

---

## 💬 User Flow

### Step 1: Notification
- 5 minutes after meeting ends
- Push notification: "Share insights from your meeting with Hookle?"
- User clicks notification

### Step 2: Full-Screen Chat Opens
```
🤖 AI Assistant
Thanks for taking a moment to share your insights! Let's capture
the key takeaways from your meeting with Hookle.

**Question 1 of 3:**
What specific marketing automation capabilities did Hookle
demonstrate that could benefit AXA's marketing operations?

[Progress: 1/3 ●○○]

┌─────────────────────────────────────────────┐
│ Type your answer...                         │
│                                             │
└─────────────────────────────────────────────┘
                                    [Send ➤]
```

### Step 3: User Answers
```
👤 User
They showed autonomous social media posting across 5 platforms
with AI-generated content that adapts to each platform's style.
Impressive multi-agent coordination.

🤖 AI Assistant
Great insight! That cross-platform capability with adaptive
content sounds powerful for scaling our social presence.

**Question 2 of 3:**
What specific business value or use cases could Hookle provide
to AXA's marketing team?

[Progress: 2/3 ●●○]
```

### Step 4: Continue Until Done
After 3 questions:
```
🤖 AI Assistant
Perfect! Your insights about Hookle have been saved.

Summary of what you shared:
✓ Technical capabilities captured
✓ Business value identified
✓ Next steps documented

You can review or edit these insights anytime from your
dashboard. Thanks for taking the time!

[View Insights] [Close]
```

---

## 🎨 Frontend Integration

### React Component Example

```javascript
import { useState, useEffect } from 'react';

function FeedbackChat({ meetingId, userId, startupName, startupDescription }) {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Start session when component mounts
  useEffect(() => {
    startFeedbackSession();
  }, []);

  const startFeedbackSession = async () => {
    const response = await fetch('/feedback/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        meeting_id: meetingId,
        user_id: userId,
        startup_name: startupName,
        startup_description: startupDescription
      })
    });

    const data = await response.json();
    setSession(data);
    setMessages([{ role: 'assistant', content: data.message }]);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to UI
    setMessages([...messages, { role: 'user', content: input }]);
    setLoading(true);

    // Send to API
    const response = await fetch('/feedback/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: session.session_id,
        message: input
      })
    });

    const data = await response.json();

    // Add assistant response
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: data.response
    }]);

    setInput('');
    setLoading(false);

    // Check if completed
    if (data.completed) {
      // Show completion UI
      setTimeout(() => {
        onComplete();
      }, 2000);
    }
  };

  return (
    <div className="feedback-chat-fullscreen">
      <div className="chat-header">
        <h2>Meeting Insights: {startupName}</h2>
        <div className="progress">
          {session?.progress.current} / {session?.progress.total}
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>

      <div className="chat-input">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your answer..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          {loading ? 'Sending...' : 'Send ➤'}
        </button>
      </div>
    </div>
  );
}
```

---

## 🔧 LLM Configuration

### Models Used
- **Question Generation**: GPT-4o-mini (fast, creative)
- **Conversation**: GPT-4o-mini (natural, friendly)
- **Answer Enhancement**: GPT-4o-mini (concise, helpful)

### Prompts
1. **Question Generator**: Generates 3 contextual questions
2. **Conversation Guide**: Maintains natural chat flow
3. **Answer Enhancer**: Optionally requests clarification

All prompts are in `/api/meeting_feedback_llm.py`

---

## 📈 Benefits

### For Users
- ✅ Natural conversation vs boring form
- ✅ Context-aware questions
- ✅ Can edit answers later
- ✅ Takes 2-3 minutes

### For AXA
- ✅ Structured, searchable insights
- ✅ Higher completion rate (chat is engaging)
- ✅ Better quality answers (LLM asks follow-ups)
- ✅ Automatic tagging and categorization
- ✅ Detects action items automatically

---

## 🎯 Example Questions Generated

### For Marketing AI Startup (Hookle)
1. **Technical**: "What marketing automation capabilities did they demonstrate?"
2. **Business**: "What specific value could this provide to AXA?"
3. **Action**: "What are the recommended next steps?"

### For Claims Automation Startup (Simplifai)
1. **Technical**: "How does their AI handle complex insurance claims processing?"
2. **Business**: "What claims processes could be automated and what's the ROI?"
3. **Action**: "What would a pilot program look like?"

### For Legacy Modernization Startup
1. **Technical**: "What approach did they demonstrate for legacy system integration?"
2. **Business**: "Which of AXA's legacy systems could benefit most?"
3. **Action**: "What's needed for a technical assessment?"

---

## 🔮 Future Enhancements

1. **Voice Input**: Speak answers instead of typing
2. **Multi-Language**: Support for French, German, etc.
3. **Smart Summaries**: AI generates executive summary
4. **Sentiment Analysis**: Detect enthusiasm level
5. **Auto-Recommendations**: "Based on your answers, you should also meet..."
6. **Team Insights**: "3 other team members also liked this startup"

---

**Implementation Date**: November 14, 2025
**Status**: ✅ READY FOR INTEGRATION
**Dependencies**: LiteLLM, GPT-4o-mini
**Files**:
- `/api/meeting_feedback_llm.py` - Core logic
- `/api/models.py` - Database models (updated)
- `/api/schemas.py` - API schemas (updated)
- Endpoints need to be added to `/api/main.py`
