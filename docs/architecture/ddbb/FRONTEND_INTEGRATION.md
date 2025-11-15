# Frontend Integration Guide

## ✅ Backend Ready

The API now uses the normalized database. All endpoints are ready for frontend consumption.

## 📡 Available API Endpoints

### Startup Endpoints
```javascript
// Get all startups (paginated)
GET /startups/all?skip=0&limit=100
Response: { total: number, count: number, startups: Startup[] }

// Get prioritized startups for AXA
GET /startups/prioritized?user_id=123&limit=100&min_score=30
Response: { total, prioritized_count, personalized, startups: Startup[] }

// Get startup insights
GET /startups/{startup_id}/insights
Response: { startup_id, startup_name, insights: {} }

// Batch insights
POST /startups/batch-insights
Body: string[]
Response: { results: [], count: number }

// Enriched startup search
GET /startups/enriched/search?query=AI&enrichment_type=emails&limit=20
Response: { results: [], count, enrichment_type, query }

// Get enrichment data
GET /startups/{startup_id}/enrichment
Response: { startup_id, startup_name, website, enrichment: {}, last_enriched }

// Enrichment statistics
GET /startups/enrichment/stats
Response: { total_startups, enriched_count, with_funding, with_logo, enrichment_percentage }
```

### Calendar Events
```javascript
// Get all events
GET /calendar-events/?skip=0&limit=100
Response: CalendarEvent[]

// Get events by date range
GET /api/calendar-events/date-range?start_date=2025-11-19T00:00:00.000Z&end_date=2025-11-20T23:59:59.000Z
Response: { events: [], count: number }

// Create event
POST /calendar-events/
Body: { title, startTime, endTime, type, attendees, stage, category }
Response: CalendarEvent

// Update event
PUT /calendar-events/{event_id}
Body: CalendarEventCreate
Response: CalendarEvent

// Delete event
DELETE /calendar-events/{event_id}
Response: { message: "Calendar event deleted" }
```

### Ratings
```javascript
// Get average ratings
GET /api/ratings/average?limit=100
Response: { ratings: [{ startup_id, avg_rating, num_ratings }], count }

// Add/update rating
POST /api/ratings
Body: { startup_id: string, user_id: string, rating: number (1-5) }
Response: { startup_id, user_id, rating, status: "saved" }

// Get all ratings
GET /startup-ratings/?skip=0&limit=100
Response: StartupRating[]
```

### Ideas
```javascript
// Get all ideas
GET /ideas/?skip=0&limit=100
Response: Idea[]

// Create idea
POST /ideas/
Body: { name, title, category, description, tags: string[] }
Response: Idea
```

### User Management
```javascript
// Get current user
GET /api/current-user
Response: { user_id: string }

// Set current user
POST /api/current-user
Body: { user_id: string }
Response: { user_id, status: "updated" }

// Get finished users
GET /api/finished-users
Response: { finished_users: string[], count: number }

// Mark user as finished
POST /api/finished-users
Body: { user_id: string }
Response: { user_id, status: "marked_finished" }
```

### Aurora Themes
```javascript
// Get all themes with colors
GET /api/auroral-themes
Response: { description, last_viewed, themes: [{ name, hours, mood, colors: [] }] }

// Get/Update auroral info
GET /auroral-info/
POST /auroral-info/
```

### Messages
```javascript
// Get AI assistant messages
GET /api/messages/ai-assistant?limit=100
Response: { messages: [{ id, role, content, timestamp }], count }

// LinkedIn messages
GET /linkedin-chat-messages/?skip=0&limit=100
POST /linkedin-chat-messages/
```

### Metadata
```javascript
// Get data version
GET /api/data-version
Response: { version: "v3-6715-startups" }

// Health check
GET /health
Response: { status, version, startups_in_db, legacy_startups_loaded }
```

## 🔄 Migration Examples

### Before (JSON Files)
```javascript
// ❌ Old way - reading JSON files directly
const response = await fetch('/docs/architecture/ddbb/calendar-events.md');
const events = await response.json();
```

### After (Database API)
```javascript
// ✅ New way - using API endpoints
const response = await fetch('http://localhost:8000/calendar-events/');
const events = await response.json();
```

## 📝 Frontend Code Examples

### Fetch All Startups
```javascript
async function getStartups(skip = 0, limit = 100) {
  const response = await fetch(
    `http://localhost:8000/startups/all?skip=${skip}&limit=${limit}`
  );
  const data = await response.json();
  return data.startups;
}
```

### Get Calendar Events for Date Range
```javascript
async function getEventsForDate(startDate, endDate) {
  const params = new URLSearchParams({
    start_date: startDate.toISOString(),
    end_date: endDate.toISOString()
  });
  
  const response = await fetch(
    `http://localhost:8000/api/calendar-events/date-range?${params}`
  );
  const data = await response.json();
  return data.events;
}
```

### Add Startup Rating
```javascript
async function rateStartup(startupId, userId, rating) {
  const response = await fetch('http://localhost:8000/api/ratings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ startup_id: startupId, user_id: userId, rating })
  });
  return await response.json();
}
```

### Search Enriched Startups
```javascript
async function searchEnrichedStartups(query, type = null) {
  const params = new URLSearchParams({ query, limit: 20 });
  if (type) params.append('enrichment_type', type);
  
  const response = await fetch(
    `http://localhost:8000/startups/enriched/search?${params}`
  );
  const data = await response.json();
  return data.results;
}
```

### Create New Idea
```javascript
async function createIdea(ideaData) {
  const response = await fetch('http://localhost:8000/ideas/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: ideaData.name,
      title: ideaData.title,
      category: ideaData.category,
      description: ideaData.description,
      tags: ideaData.tags || []
    })
  });
  return await response.json();
}
```

### Get Current User
```javascript
async function getCurrentUser() {
  const response = await fetch('http://localhost:8000/api/current-user');
  const data = await response.json();
  return data.user_id;
}
```

### Get Auroral Theme for Time
```javascript
async function getAuroralThemes() {
  const response = await fetch('http://localhost:8000/api/auroral-themes');
  const data = await response.json();
  
  // Find theme for current hour
  const hour = new Date().getHours();
  const currentTheme = data.themes.find(theme => {
    const [start, end] = theme.hours.split(' - ').map(h => parseInt(h));
    return hour >= start && hour < end;
  });
  
  return currentTheme || data.themes[0];
}
```

## 🚀 Quick Start

### 1. Start API Server
```bash
cd api
uvicorn main:app --reload --port 8000
```

### 2. Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Get startups
curl http://localhost:8000/startups/all?limit=5

# Get enrichment stats
curl http://localhost:8000/startups/enrichment/stats

# Get calendar events
curl http://localhost:8000/calendar-events/

# Get current user
curl http://localhost:8000/api/current-user
```

### 3. Update Frontend Config
```javascript
// config.js or similar
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = {
  startups: {
    getAll: (skip, limit) => `${API_BASE_URL}/startups/all?skip=${skip}&limit=${limit}`,
    getPrioritized: (userId, limit) => `${API_BASE_URL}/startups/prioritized?user_id=${userId}&limit=${limit}`,
    getInsights: (id) => `${API_BASE_URL}/startups/${id}/insights`,
    getEnrichment: (id) => `${API_BASE_URL}/startups/${id}/enrichment`,
  },
  calendar: {
    getAll: () => `${API_BASE_URL}/calendar-events/`,
    getByDate: (start, end) => `${API_BASE_URL}/api/calendar-events/date-range?start_date=${start}&end_date=${end}`,
  },
  ratings: {
    add: () => `${API_BASE_URL}/api/ratings`,
    getAverage: () => `${API_BASE_URL}/api/ratings/average`,
  },
  ideas: {
    getAll: () => `${API_BASE_URL}/ideas/`,
    create: () => `${API_BASE_URL}/ideas/`,
  },
  user: {
    getCurrent: () => `${API_BASE_URL}/api/current-user`,
    setCurrent: () => `${API_BASE_URL}/api/current-user`,
    getFinished: () => `${API_BASE_URL}/api/finished-users`,
    markFinished: () => `${API_BASE_URL}/api/finished-users`,
  },
  auroral: {
    getThemes: () => `${API_BASE_URL}/api/auroral-themes`,
  }
};
```

## 🔍 Debugging

### Check Database Connection
```bash
cd api
python -c "from database import SessionLocal; db = SessionLocal(); print('✓ Connected'); db.close()"
```

### Verify Data
```bash
cd api
python -c "
from database import SessionLocal
import db_queries

db = SessionLocal()
print(f'Startups: {db_queries.count_startups(db)}')
print(f'Events: {len(db_queries.get_calendar_events(db))}')
print(f'Ideas: {len(db_queries.get_ideas(db))}')
db.close()
"
```

### API Logs
Check console output when starting uvicorn for:
- Database connection status
- Startup count
- Legacy JSON file warnings

## 📊 Database vs JSON Comparison

| Feature | JSON Files | Database API |
|---------|-----------|--------------|
| Query Speed | Slow (full scan) | Fast (indexed) |
| Concurrent Access | Limited | Unlimited |
| Transactions | None | ACID |
| Relationships | Manual | Foreign keys |
| Scalability | Poor | Excellent |
| Type Safety | None | SQLAlchemy models |

## ⚠️ Important Notes

1. **API Base URL**: Update in frontend config when deploying
2. **CORS**: Already configured in API for all origins
3. **Rate Limiting**: Not yet implemented
4. **Authentication**: Currently optional, add as needed
5. **Legacy Support**: JSON files still loaded as fallback

## 🎯 Next Steps

1. ✅ Update frontend API calls to use new endpoints
2. ✅ Remove direct JSON file reads
3. ✅ Test all features end-to-end
4. ✅ Add error handling for API failures
5. ✅ Implement loading states
6. ✅ Add API retry logic
7. ✅ Monitor API performance

## 📚 Related Documentation

- **Schema**: `/docs/architecture/ddbb/DATABASE_SCHEMA.md`
- **Migration**: `/docs/architecture/ddbb/MIGRATION_SUMMARY.md`
- **Query Layer**: `/api/db_queries.py`
- **API Code**: `/api/main.py`
