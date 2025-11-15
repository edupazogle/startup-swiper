# AI Prompts Guide - Startup Rise 🚀

This guide shows you where all the AI capabilities are in your app and how to customize the prompts powering each feature.

---

## 📍 AI Features Overview

Your app has **5 AI-powered features**:

1. **AI Assistant** - General chatbot for startup/event questions
2. **LinkedIn Expert (FrankAI)** - Generates LinkedIn posts from Slush experiences
3. **AI Recommendations** - Suggests startups based on user interests
4. **AI Startup Insights** - Analyzes individual startups
5. **AI Time Slot Suggester** - Recommends optimal meeting times

---

## 1️⃣ AI Assistant

**Location:** `/src/components/AIAssistant.tsx` (Lines 60-71)

**What it does:** Answers questions about startups, events, and provides general advice

**Current Prompt:**
```typescript
const contextString = `You are an AI assistant for Startup Rise, a startup discovery platform at Slush 2025. 
Current user: ${currentUserName}

Context:
- Total startups: ${totalStartups}
- Interested startups: ${interestedCount}
- Upcoming events: ${upcomingCount}
- Interested startup categories: ${categories}

User question: ${userQuestion}

Provide helpful, concise responses about startups, events, or general advice. Be enthusiastic and supportive.`
```

**How to customize:**
- Change the tone (e.g., "Be professional" vs "Be casual and fun")
- Add more context data (e.g., user's past meetings, voting patterns)
- Modify the assistant's role (e.g., "You are a VC advisor" vs "You are a startup founder")

---

## 2️⃣ LinkedIn Expert (FrankAI)

**Location:** `/src/components/LinkedInExpertView.tsx` (Lines 49-136)

**What it does:** Transforms user experiences into engaging LinkedIn posts with proper formatting, tagging, and hashtags

**Current Prompt:** (Very detailed - 80+ lines)
```typescript
const promptText = `You are the "on-the-ground" digital voice for ${currentUserName} at Slush 2024...
```

**Key sections you can edit:**
- **PERSONA & MISSION** (Lines 52-58): Change the voice/tone
- **CONTENT STYLE** (Lines 64-86): Modify post structure
- **TIMING GUIDELINES** (Lines 89-92): Adjust when to post
- **TAGGING STRATEGY** (Lines 95-101): Change how people/companies are tagged
- **HASHTAG RULES** (Lines 103-107): Modify hashtag usage
- **HOOK GUIDELINES** (Lines 116-120): Change opening line style

**Example customizations:**
- Make it more formal: Change "Enthusiastic & Passionate" to "Professional & Analytical"
- Different emoji set: Modify the emoji suggestions
- Longer/shorter posts: Adjust the content structure guidelines

---

## 3️⃣ AI Recommendations

**Location:** `/src/components/AIRecommendations.tsx` (Lines 57-82)

**What it does:** Analyzes user's voting patterns and recommends similar unseen startups

**Current Prompt:**
```typescript
const context = `
Based on user interests, recommend top 3 startups from the unseen list.

User has shown interest in:
- Categories: ${interestedCategories.join(', ')}
- Stages: ${interestedStages.join(', ')}
- Companies: ${interestedStartups.slice(0, 3).map(s => s["Company Name"]).join(', ')}

Unseen startups (pick 3 best matches):
${unseenStartups.slice(0, 10).map((s, i) => 
  `${i + 1}. ${s["Company Name"]} (${s.Category}, ${s.Stage}) - ${s["Company Description"].slice(0, 100)}`
).join('\n')}

Return recommendations as JSON:
{
  "recommendations": [
    {
      "startupId": "startup-id",
      "reason": "brief reason why this matches user interests (max 80 chars)",
      "confidence": 0.95
    }
  ]
}

Only recommend startups that genuinely match the user's interests.
`
```

**How to customize:**
- Change number of recommendations (currently 3)
- Add more criteria (e.g., funding amount, location)
- Adjust the matching algorithm instructions
- Change the reason length (currently 80 chars max)

---

## 4️⃣ AI Startup Insights

**Location:** `/src/components/AIStartupInsights.tsx` (Lines 38-61)

**What it does:** Provides analysis of individual startups with strengths, opportunities, and recommendations

**Current Prompt:**
```typescript
const context = `
Analyze this startup and provide 3-4 concise insights:

Startup: ${startup["Company Name"]}
Description: ${startup["Company Description"]}
Category: ${startup.Category}
Stage: ${startup.Stage}
USP: ${startup.USP}
Funding: ${startup.Funding}
Priority Score: ${startup["Final Priority Score"]}

User's interest patterns: ${interestedCategories.join(', ')}

Provide insights in JSON format with this structure:
{
  "insights": [
    {"type": "strength", "content": "brief insight"},
    {"type": "opportunity", "content": "brief insight"},
    {"type": "recommendation", "content": "brief insight"}
  ]
}

Focus on: key strengths, market opportunities, and why this startup might be relevant to someone interested in: ${interestedCategories.join(', ')}.
Keep each insight under 100 characters.
`
```

**How to customize:**
- Change insight types (add "risk" or "competitive-advantage")
- Adjust character limit (currently 100 chars)
- Change number of insights (currently 3-4)
- Add more startup data fields to analyze

---

## 5️⃣ AI Time Slot Suggester

**Location:** `/src/components/AITimeSlotSuggester.tsx` (Lines 37-59)

**What it does:** Suggests optimal meeting times based on existing calendar events

**Current Prompt:**
```typescript
const context = `
You are a smart meeting scheduler for Slush 2025 (Nov 18-20, 2024).

Existing upcoming meetings:
${upcomingEvents.map(e => `- ${e.title}: ${new Date(e.start).toLocaleString()} to ${new Date(e.end).toLocaleString()}`).join('\n')}

Suggest 3 optimal 30-minute meeting time slots that:
1. Don't overlap with existing meetings
2. Are during business hours (9 AM - 6 PM)
3. Are within the Slush dates (Nov 18-20, 2024)
4. Avoid lunch time (12:00-13:00)
5. Prefer morning slots (better for networking)

Return as JSON:
{
  "suggestions": [
    {
      "startTime": "2024-11-18T10:00:00",
      "endTime": "2024-11-18T10:30:00",
      "reason": "Morning slot, no conflicts"
    }
  ]
}
`
```

**How to customize:**
- Change meeting duration (currently 30 minutes)
- Adjust business hours (currently 9 AM - 6 PM)
- Modify lunch time window
- Change preference (e.g., prefer afternoon instead of morning)
- Update event dates for future conferences

---

## 🔧 How to Edit AI Prompts

### Step 1: Locate the Component
Find the component file from the locations above.

### Step 2: Find the Prompt
Search for the `spark.llm()` call or the prompt variable (usually `context`, `promptText`, or `contextString`).

### Step 3: Edit the Prompt
Modify the prompt text within the backticks. Remember:
- Use `${variable}` for dynamic data
- Keep JSON structure format if using `jsonMode: true`
- Test changes incrementally

### Step 4: Test
Try the feature in the app to see how the AI responds with your new prompt.

---

## 💡 Prompt Engineering Tips

1. **Be Specific:** "Write a professional LinkedIn post" is better than "Write a post"
2. **Provide Examples:** Show the AI what you want (format, tone, length)
3. **Set Constraints:** Character limits, JSON format, number of items
4. **Give Context:** More relevant data = better responses
5. **Iterate:** Test and refine based on actual outputs

---

## 🎯 Common Customizations

### Make AI More Formal
Change phrases like:
- "Be enthusiastic" → "Be professional and analytical"
- "Use emojis" → "Avoid emojis, use bullet points"

### Add More Context
Include additional data:
```typescript
- User location: ${userLocation}
- Company size preference: ${sizePreference}
- Investment focus: ${investmentFocus}
```

### Change Output Length
Adjust constraints:
- "Keep under 100 characters" → "Keep under 200 characters"
- "Provide 3 insights" → "Provide 5 insights"

### Modify JSON Structure
Change the expected response format:
```typescript
{
  "insights": [
    {"type": "strength", "content": "...", "priority": "high"}
  ]
}
```

---

## 🚀 Advanced: Adding New AI Features

To add a new AI-powered feature:

1. **Create the prompt:**
```typescript
const prompt = spark.llmPrompt`Your instruction here with ${dynamicData}`
```

2. **Call the AI:**
```typescript
const response = await spark.llm(prompt, 'gpt-4o', false)
// or with JSON mode:
const response = await spark.llm(prompt, 'gpt-4o', true)
const data = JSON.parse(response)
```

3. **Handle the response:**
```typescript
// Use the AI-generated content in your component
```

---

## 📚 Available Models

- `gpt-4o` - Default, most capable (used by all features currently)
- `gpt-4o-mini` - Faster, cheaper, good for simpler tasks

**Usage:**
```typescript
await spark.llm(prompt, 'gpt-4o')      // Full model
await spark.llm(prompt, 'gpt-4o-mini') // Mini model
```

---

## ❓ FAQ

**Q: Can I use different models for different features?**
A: Yes! Just change the second parameter in `spark.llm()` calls.

**Q: What if the AI returns malformed JSON?**
A: Add more explicit JSON structure instructions and examples in your prompt.

**Q: How do I make responses faster?**
A: Use `gpt-4o-mini` or make prompts more concise.

**Q: Can I add context from external APIs?**
A: Yes! Fetch data first, then include it in your prompt template.

---

## 📝 Summary

All AI features use the `spark.llm()` API with carefully crafted prompts. Each prompt can be customized by editing the component files listed above. The prompts use template literals with dynamic data insertion to provide context-aware responses.

**Happy customizing! 🎉**
