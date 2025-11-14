# 🚀 Startup Prioritization - Quick Start

## TL;DR

Your API now intelligently ranks 4,374 startups based on AXA's priorities:
1. **Agentic platforms** (build your own AI agents)
2. **Agentic solutions** (marketing, claims, HR automation)
3. **Dev & integration** tools (legacy modernization)
4. **Insurtech** (insurance-specific solutions)

Plus personalization based on user likes + diversity for discovery.

---

## 🎯 Quick Examples

### Get Top 10 AXA-Priority Startups
```bash
curl "http://localhost:8000/startups/prioritized?limit=10"
```

**Results** (Nov 14, 2025):
1. Hookle - AI agents for micro-business marketing (Agentic Marketing)
2. WiseBee - Real-time threat intelligence (Security AI)
3. ClickHouse - Fast columnar database (Analytics Platform)
4. Nolana AI - Financial workflows automation (Finance AI)
5. Chapter - Energy sector automation (Vertical AI)
6. Simplifai - Insurance process automation (Insurtech)
7. Me Protocol - AI economy rewards layer (Platform)
8. Honu AI - Autonomous company engine (Agentic Platform)
9. Whoever.global - AI product development (AI Development)
10. Gampr.ai - Customer experience monitoring (CX Automation)

**Why this order?**
- Mix of platform enablers and ready-to-use solutions
- Different industries (marketing, insurance, finance, energy)
- Different stages (Seed to Series C)
- All highly relevant to AXA's AI strategy

---

### Get Personalized Recommendations for Alice
```bash
curl "http://localhost:8000/startups/prioritized?user_id=1&limit=10"
```

Alice's personalized list adapts based on what she's liked before.

---

### Check Why a Startup is Prioritized
```bash
curl "http://localhost:8000/startups/Hookle/insights"
```

**Response**:
```json
{
  "startup_id": "Hookle",
  "startup_name": "Hookle",
  "insights": {
    "categories": ["agentic_platform_enabler"],
    "base_score": 100,
    "priority_tier": "Top Priority (Agentic Solutions)",
    "stage": "Series A"
  }
}
```

**Explanation**: Hookle scores 100/100 because it's an agentic platform enabler - exactly what AXA needs.

---

## 🎖️ Priority Categories (What Gets Shown First)

### Tier 1 - Agentic Platforms (100 points)
Build your own AI agents
- **Keywords**: "agentic platform", "agent framework", "multi-agent"
- **Examples**: Hookle, Honu AI, Me Protocol

### Tier 2 - Agentic Solutions (80-85 points)
Ready-made AI automation for:
- **Marketing**: Content generation, campaigns
- **Claims**: Automated claims processing
- **HR**: Recruitment, talent management
- **Customer Service**: Chatbots, support automation
- **Examples**: Simplifai, Nolana AI, Gampr.ai

### Tier 3 - Development Tools (70-75 points)
- Code generation, testing, legacy modernization
- **Examples**: ClickHouse, Whoever.global

### Tier 4 - Insurtech (60-65 points)
- Insurance-specific technology
- **Examples**: Simplifai (also in Tier 2)

---

## 🔄 How It Adapts to Users

### Alice's Journey

**Week 1 - First 10 startups**: Diverse mix across all tiers
- Likes: 3 marketing automation startups ✓
- Dislikes: 2 insurtech startups ✗

**Week 2 - Next 10 startups**: More marketing, less insurtech
- Shows 6 marketing/content tools
- Shows 2 agentic platforms (always relevant)
- Shows 2 unexpected gems (discovery)

**Week 3 - Next 10 startups**: Strong personalization
- Shows advanced marketing AI tools
- Shows content generation platforms
- Still includes 1-2 different categories for discovery

---

## 🎨 Diversity Features

### Always Maintains Variety
- **First 10**: Maximum diversity (different stages, categories)
- **Next 40**: Personalized but still 20% diversity
- **Ongoing**: Never shows 3+ similar startups in a row

### Example Diversity
Instead of showing:
1. Marketing AI #1
2. Marketing AI #2
3. Marketing AI #3
4. Marketing AI #4

Shows:
1. Marketing AI #1
2. Claims automation (different category)
3. Marketing AI #2
4. Development tool (exploration)

---

## 📊 Live Statistics

```bash
curl http://localhost:8000/ | python3 -m json.tool
```

```json
{
  "message": "Startup Swiper API with AI Concierge & Smart Prioritization",
  "startups_loaded": 4374,
  "features": [
    "Smart Startup Prioritization (Agentic-First)",
    "Personalized Recommendations",
    ...
  ]
}
```

---

## 🔧 Integration Code

### React Frontend Example

```javascript
// Load prioritized startups for a user
async function loadStartups(userId) {
  const response = await fetch(
    `http://localhost:8000/startups/prioritized?user_id=${userId}&limit=50`
  );
  const data = await response.json();

  console.log(`Loaded ${data.prioritized_count} startups`);
  console.log(`Personalized: ${data.personalized}`);

  return data.startups;
}

// Get why a startup is prioritized
async function getStartupPriority(startupName) {
  const response = await fetch(
    `http://localhost:8000/startups/${startupName}/insights`
  );
  const data = await response.json();

  console.log(`${startupName} is in: ${data.insights.priority_tier}`);
  console.log(`Categories: ${data.insights.categories.join(', ')}`);

  return data.insights;
}

// Usage
const startups = await loadStartups(1); // Alice
const insights = await getStartupPriority('Hookle');
```

---

## 🎯 What Makes a Startup "High Priority" for AXA?

### ✅ Top Priority (90-100 points)
- Mentions "agentic platform", "AI agents", "agent framework"
- Platform for building autonomous AI systems
- Multi-agent orchestration
- LangChain, AutoGen, or similar frameworks

### ✅ Very High Priority (80-89 points)
- Marketing automation with AI
- Claims processing automation
- HR/recruitment AI
- Customer service AI
- Any AI solution directly applicable to AXA

### ✅ High Priority (70-79 points)
- Code generation & development AI
- Automated testing
- Legacy system modernization
- Integration tools
- DevOps automation

### ✅ Medium Priority (60-69 points)
- General insurtech
- Risk management
- Compliance automation

---

## 💡 Pro Tips

1. **Use personalization**: Pass `user_id` to get better recommendations over time
2. **Check insights**: Use `/insights` endpoint to understand why startups are prioritized
3. **Adjust limit**: Start with limit=20, increase as users engage more
4. **Batch insights**: Use `/batch-insights` for analytics dashboards
5. **Monitor preferences**: Track which categories users like most

---

## 🔗 Related Endpoints

- `GET /startups/all` - All 4,374 startups (no prioritization)
- `GET /startups/prioritized` - Smart prioritization (RECOMMENDED)
- `GET /startups/{id}/insights` - Why this startup is prioritized
- `POST /startups/batch-insights` - Get insights for multiple startups
- `GET /votes/` - Get all votes (for personalization)
- `POST /votes/` - Record a vote (updates personalization)

---

## 📖 Full Documentation

See `/api/STARTUP_PRIORITIZATION.md` for complete details on:
- Algorithm explanation
- Scoring formula
- Configuration options
- Future enhancements

---

**Status**: ✅ LIVE
**Total Startups**: 4,374
**API**: http://localhost:8000
**Docs**: http://localhost:8000/docs
