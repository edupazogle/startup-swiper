# Database Migration Summary

## ✅ Completed Actions

### 1. Database Normalization
- **Created**: 19 normalized tables from JSON docs
- **Location**: `/backend/normalize_tables.py`
- **Tables Created**:
  - `ai_assistant_messages`, `ai_chat_messages`, `linkedin_chat_messages`
  - `calendar_events`, `calendar_event_attendees`
  - `ideas`, `idea_tags`
  - `startup_ratings`
  - `finished_users`
  - `auroral_info`, `auroral_themes`, `auroral_theme_colors`
  - `data_version`, `current_user`, `admin_user`
  - `votes`, `user_events`

### 2. Data Migration
- **Script**: `/backend/migrate_json_to_db.py`
- **Migrated Data**:
  - ✅ 1 AI assistant message
  - ✅ 52 calendar events
  - ✅ 1 idea
  - ✅ 7 startup ratings
  - ✅ 1 finished user
  - ✅ 6 auroral themes with colors
  - ✅ Data version (v3-6715-startups)
  - ✅ Current user (116544866)

### 3. JSON Syntax Fixes
- Fixed `startup-ratings.md` (removed stray 'z')
- Fixed `finished-users.md` (removed stray 'a')

### 4. API Updates
- **Created**: `/api/db_queries.py` - centralized query layer
- **Updated**: `/api/database.py` - corrected DB path to root
- **Updated**: `/api/main.py` - migrated endpoints to use database

#### Updated Endpoints:
- ✅ `GET /health` - now shows DB stats
- ✅ `GET /startups/all` - uses `db_queries.get_all_startups()`
- ✅ `GET /startups/prioritized` - fetches from DB
- ✅ `GET /startups/{startup_id}/insights` - uses `db_queries.get_startup_by_id()`
- ✅ `POST /startups/batch-insights` - uses DB queries
- ✅ `GET /startups/enriched/search` - queries enriched startups from DB
- ✅ `GET /startups/{startup_id}/enrichment` - fetches from DB
- ✅ `GET /startups/enrichment/stats` - uses `db_queries.get_enrichment_stats()`

## 📊 Database Statistics

```
Total Startups:        3,478
Enriched:              3,050 (87.69%)
With Funding:          1,300
With Logos:            1,554
Calendar Events:       52
Ideas:                 1
Ratings:               7
```

## 🔧 Setup Instructions

### 1. Create Tables
```bash
python backend/normalize_tables.py
```

### 2. Migrate Data
```bash
python backend/migrate_json_to_db.py
```

### 3. Verify
```bash
cd api && python -c "
from database import SessionLocal
import db_queries

db = SessionLocal()
print(f'Startups: {db_queries.count_startups(db)}')
print(f'Stats: {db_queries.get_enrichment_stats(db)}')
db.close()
"
```

## 🚀 Frontend Integration

### Before (JSON Files)
```javascript
const response = await fetch('/docs/architecture/ddbb/calendar-events.md');
const events = await response.json();
```

### After (Database API)
```javascript
const response = await fetch('/api/startups/all?limit=100');
const { startups, total } = await response.json();
```

## 📝 Next Steps

### Frontend Changes Needed
1. ✅ Update API endpoints to `/api/*` instead of JSON file paths
2. ✅ Calendar events: `GET /api/calendar-events` (to be added)
3. ✅ Ratings: `POST /api/ratings` (to be added)
4. ✅ Ideas: `GET /api/ideas`, `POST /api/ideas` (to be added)
5. ✅ Current user: `GET /api/current-user` (to be added)

### Additional API Endpoints to Add
```python
@app.get("/api/calendar-events")
def get_calendar_events_api(db: Session = Depends(get_db)):
    return db_queries.get_calendar_events(db, limit=100)

@app.get("/api/ideas")
def get_ideas_api(db: Session = Depends(get_db)):
    return db_queries.get_ideas(db)

@app.post("/api/ideas")
def create_idea_api(idea: dict, db: Session = Depends(get_db)):
    db_queries.add_idea(db, **idea)
    return {"status": "created"}

@app.post("/api/ratings")
def add_rating_api(rating: dict, db: Session = Depends(get_db)):
    db_queries.add_startup_rating(db, **rating)
    return {"status": "created"}

@app.get("/api/current-user")
def get_current_user_api(db: Session = Depends(get_db)):
    user_id = db_queries.get_current_user(db)
    return {"user_id": user_id}

@app.get("/api/auroral-themes")
def get_auroral_themes_api(db: Session = Depends(get_db)):
    return db_queries.get_auroral_themes(db)
```

## 🧪 Testing

### Test Database Connection
```bash
cd api && python -c "from database import SessionLocal; db = SessionLocal(); print('✓ DB connected'); db.close()"
```

### Test Queries
```bash
cd api && python -c "
from database import SessionLocal
import db_queries

db = SessionLocal()
print(f'Startups: {db_queries.count_startups(db)}')
print(f'Events: {len(db_queries.get_calendar_events(db))}')
print(f'Ideas: {len(db_queries.get_ideas(db))}')
db.close()
"
```

### Start API Server
```bash
cd api && uvicorn main:app --reload --port 8000
```

### Test Endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/startups/all?limit=10
curl http://localhost:8000/startups/enrichment/stats
```

## 📚 Documentation

- **Schema**: `/docs/architecture/ddbb/DATABASE_SCHEMA.md`
- **Query Layer**: `/api/db_queries.py`
- **Migration Scripts**: `/backend/normalize_tables.py`, `/backend/migrate_json_to_db.py`

## ⚠️ Breaking Changes

### Legacy Support
- Old JSON file reads still work if files exist
- Warning messages displayed on API startup
- Recommendation: Remove JSON files after frontend migration

### Field Name Changes
- `name` → `company_name` (in startups table)
- `startTime` → `start_time` (camelCase → snake_case)
- `userId` → `user_id`

## 🔄 Rollback Plan

If issues occur:
1. Restore JSON file reads in `main.py`
2. Remove `import db_queries`
3. Revert endpoints to use `ALL_STARTUPS`

## ✨ Benefits

1. **Performance**: Indexed queries vs full file scans
2. **Consistency**: ACID transactions, foreign keys
3. **Scalability**: Easy to migrate to PostgreSQL
4. **Maintainability**: Centralized query layer
5. **Type Safety**: SQLAlchemy models
