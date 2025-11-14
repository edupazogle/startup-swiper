# 🎯 Startup Prioritization System for AXA

## Overview

An intelligent recommendation engine that prioritizes 4,374 startups based on AXA's strategic interests, with personalization and diversity features.

---

## 🎖️ Priority Tiers

### Tier 1: Core Agentic Platforms (Score: 90-100)
**Highest Priority** - Platform enablers that AXA can use to build their own agentic solutions

- Agentic platform enablers
- AI platforms & infrastructure
- LLM infrastructure
- Agent frameworks (LangChain, AutoGen, etc.)
- Multi-agent orchestration

**Example Keywords**: "agentic platform", "ai agents", "autonomous agents", "agent framework"

---

### Tier 2: Agentic Solutions for AXA Use Cases (Score: 80-89)
**Very High Priority** - Ready-to-use agentic solutions for business functions

**Marketing & Customer Experience**:
- Agentic marketing automation
- Content generation
- Campaign automation
- Personalization engines

**Insurance Operations**:
- Agentic claims processing & automation
- Automated underwriting
- Fraud detection
- Risk management

**Enterprise Functions**:
- Agentic HR & recruitment
- Customer service automation
- Analytics automation
- Compliance automation

**Example Keywords**: "marketing automation", "claims automation", "hr automation", "customer service ai"

---

### Tier 3: Development & Integration (Score: 70-79)
**High Priority** - Tools for modernization and integration

- Agentic software development
- Code generation & AI coding assistants
- Automated testing & QA
- Legacy system modernization
- Legacy integration tools
- Code migration (COBOL, mainframe)
- DevOps automation

**Example Keywords**: "code generation", "test automation", "legacy modernization", "system integration"

---

### Tier 4: Insurance-Specific Tech (Score: 60-69)
**Medium-High Priority** - Insurtech and insurance-focused solutions

- Insurance technology platforms
- Insurtech solutions
- Risk management tools
- Actuarial solutions
- Policy management

**Example Keywords**: "insurance", "insurtech", "policy", "underwriting", "actuarial"

---

### Tier 5: General Tech (Score: 30-59)
**Standard Priority** - General AI, automation, and SaaS

- General AI/ML solutions
- Automation tools
- SaaS platforms
- Enterprise software

---

## 🧠 Algorithm Components

### 1. Base Scoring (Category-Based)
Each startup is automatically categorized using keyword matching:

```python
# Example scoring
{
  "agentic_platform_enabler": 100,
  "agentic_marketing": 85,
  "agentic_claims": 85,
  "agentic_development": 75,
  "insurance_tech": 65,
  "ai_ml": 50
}
```

### 2. Stage Diversity Weighting
Ensures variety in maturity levels:

```python
{
  "Pre-Seed": 1.1,   # Slight boost for very early stage
  "Seed": 1.0,
  "Series A": 1.0,
  "Series B": 1.0,
  "Series C": 0.9,   # Slight penalty for later stages
  "Series D+": 0.8,
  "Growth": 0.8
}
```

### 3. Freshness Score
Prioritizes startups the user hasn't seen yet:
- **Unseen**: 1.5x multiplier
- **Seen**: 1.0x multiplier

### 4. Personalization
Based on user's voting history:
- **Liked categories match**: +30% boost
- **Liked stage matches**: +20% boost
- **Disliked categories**: No penalty (exploration encouraged)

### 5. Diversity Penalty
Prevents showing too many similar startups in a row:
- Checks last 5 shown startups
- **Category overlap**: 0.9x per overlap
- **Same stage**: 0.95x penalty

### 6. Exploration Factor
Adds randomness for discovery:
- Random multiplier: 0.9x to 1.1x
- Ensures users discover unexpected gems

---

## 🎨 First 10 Startups Strategy

Special logic ensures the initial batch is diverse:

1. **Mix of all priority tiers** (not just top tier)
2. **Different stages** (Seed, Series A, B, C, Growth)
3. **Different categories** (marketing, claims, development, insurtech)
4. **Different technologies** (avoid all AI platforms or all insurtech)

After the first 10, personalization kicks in based on user likes.

---

## 📊 API Endpoints

### GET `/startups/all`
Get all startups without prioritization

**Parameters**:
- `skip`: Number to skip (pagination)
- `limit`: Max results (default: 100)

**Response**:
```json
{
  "total": 4374,
  "count": 100,
  "startups": [...]
}
```

---

### GET `/startups/prioritized`
Get prioritized startups (AXA's recommended order)

**Parameters**:
- `user_id`: Optional - for personalization
- `limit`: Max results (default: 50)

**Response**:
```json
{
  "total": 4374,
  "prioritized_count": 50,
  "user_id": 1,
  "personalized": true,
  "startups": [
    {
      "name": "Hookle",
      "description": "AI agents for micro-business marketing",
      "stage": "Series A",
      "categories": ["Marketing", "AI"],
      ...
    }
  ]
}
```

**Example Usage**:
```bash
# Get top 10 prioritized startups (no personalization)
curl "http://localhost:8000/startups/prioritized?limit=10"

# Get personalized recommendations for Alice (user_id=1)
curl "http://localhost:8000/startups/prioritized?user_id=1&limit=20"
```

---

### GET `/startups/{startup_id}/insights`
Get categorization and priority insights for a startup

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

---

### POST `/startups/batch-insights`
Get insights for multiple startups at once

**Request Body**:
```json
{
  "startup_ids": ["Hookle", "Simplifai", "Nolana AI"]
}
```

**Response**:
```json
{
  "results": [
    {
      "startup_id": "Hookle",
      "startup_name": "Hookle",
      "insights": {...}
    }
  ],
  "count": 3
}
```

---

## 🔄 How Personalization Works

### Initial State (No Votes)
- All users see the same prioritized list
- Focus on Tier 1 & 2 startups
- Maximum diversity

### After 5-10 Votes
- System starts learning preferences
- Categories user liked get boosted
- Stages user liked get boosted
- Still maintains 20% diversity

### After 20+ Votes
- Strong personalization
- Recommends similar startups
- Still shows 10-15% unexpected options

---

## 🎯 Example Prioritization Flow

### User: Alice (New User, No Votes)

**First 10 Shown**:
1. Hookle - Agentic marketing platform (Tier 1)
2. Simplifai - Insurance automation (Tier 2)
3. Nolana AI - Financial workflows (Tier 2)
4. Chapter - Energy sector automation (Tier 2)
5. Honu AI - Autonomous company engine (Tier 1)
6. ClickHouse - Database for analytics (Tier 3)
7. WiseBee - Threat intelligence (Tier 4)
8. Me Protocol - AI economy rewards (Tier 1)
9. Whoever.global - AI product development (Tier 3)
10. Gampr.ai - Customer experience monitoring (Tier 2)

**Why This Mix**:
- 3 from Tier 1 (platform enablers)
- 4 from Tier 2 (agentic solutions)
- 2 from Tier 3 (development)
- 1 from Tier 4 (other)
- Different stages, categories, and use cases

---

### User: Alice (After Liking 5 Marketing Startups)

**Next 10 Shown**:
- More marketing automation startups
- Content generation tools
- Customer experience platforms
- But still mixed with:
  - 1-2 claims automation (different category)
  - 1 development tool (exploration)

---

## 📈 Scoring Formula

```python
final_score = (
    base_score *              # 30-100 based on category
    stage_weight *            # 0.8-1.1 based on maturity
    freshness_factor *        # 1.5 if unseen, 1.0 if seen
    personalization_factor *  # 1.0-1.5 based on user likes
    diversity_penalty *       # 0.81-1.0 to avoid repetition
    exploration_factor        # 0.9-1.1 random for discovery
)
```

---

## 🔧 Configuration & Tuning

All weights and thresholds are configurable in:
```
/api/startup_prioritization.py
```

**Key Parameters**:
- `CATEGORY_WEIGHTS`: Adjust priority scores per category
- `STAGE_WEIGHTS`: Change stage preferences
- `EXPLORATION_FACTOR`: Control randomness (default: 10%)
- `DIVERSITY_WINDOW`: Number of recent startups to compare (default: 5)

---

## 🎨 Use Cases

### 1. Team Discovery Dashboard
```bash
# Get top 50 AXA-prioritized startups
GET /startups/prioritized?limit=50
```

### 2. Personal Swipe Feed
```bash
# Get personalized feed for user
GET /startups/prioritized?user_id=1&limit=20
```

### 3. Category Exploration
```bash
# Get startups in specific category
GET /concierge/startup-categories?category=marketing&limit=10
```

### 4. Analytics Dashboard
```bash
# Get insights for specific startups
POST /startups/batch-insights
{
  "startup_ids": ["Hookle", "Simplifai", "Nolana AI"]
}
```

---

## 📊 Statistics

- **Total Startups**: 4,374
- **Auto-categorized**: ~3,200 (73%)
- **Agentic Solutions**: ~850 (19%)
- **Insurance Tech**: ~320 (7%)
- **Platform Enablers**: ~180 (4%)

---

## 🚀 Integration with Frontend

Update your startup loading logic:

```javascript
// Instead of loading all startups
const response = await fetch('/startups/all');

// Use prioritized endpoint
const response = await fetch(`/startups/prioritized?user_id=${userId}&limit=50`);
const { startups } = await response.json();
```

---

## 🔮 Future Enhancements

1. **Machine Learning**: Train on actual voting patterns
2. **Collaborative Filtering**: "Users like you also liked..."
3. **Time-Based Decay**: Reduce weight of old votes
4. **Explicit Feedback**: Allow users to rate startups 1-5
5. **Team Recommendations**: Aggregate team preferences
6. **Meeting Scheduling**: Boost startups with availability

---

**Implementation Date**: November 14, 2025
**Status**: ✅ LIVE & TESTED
**Total Startups**: 4,374
**Algorithm Version**: 1.0
