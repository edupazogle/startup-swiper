# Quick Reference - Database & API

## ✅ Status: COMPLETE & READY

The database has been normalized and the API is consuming from it.

## 📊 Statistics
```
Startups:        3,478 total (87.69% enriched)
Events:          52 calendar events
Ratings:         7 startup ratings
Ideas:           1 idea
Themes:          6 auroral themes
Data Version:    v3-6715-startups
```

## 🚀 Quick Start

### Start API Server
```bash
cd api
uvicorn main:app --reload --port 8000
```

### Test Endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/startups/all?limit=5
curl http://localhost:8000/startups/enrichment/stats
```

## 📂 Key Files

| File | Purpose |
|------|---------|
| `/api/main.py` | API endpoints (updated to use DB) |
| `/api/db_queries.py` | Query layer for all tables |
| `/api/database.py` | DB connection (points to root `/startup_swiper.db`) |
| `/backend/normalize_tables.py` | Creates normalized tables |
| `/backend/migrate_json_to_db.py` | Migrates JSON data to DB |

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `DATABASE_SCHEMA.md` | Full schema reference with sample queries |
| `MIGRATION_SUMMARY.md` | Migration process and statistics |
| `FRONTEND_INTEGRATION.md` | Frontend integration guide with examples |
| `COMPLETE.md` | This completion summary |

## 🔧 Common Commands

### Database Operations
```bash
# Create tables (one-time)
python backend/normalize_tables.py

# Migrate data (one-time)
python backend/migrate_json_to_db.py

# Verify connection
cd api && python -c "from database import SessionLocal; db = SessionLocal(); print('✓ Connected'); db.close()"

# Check counts
cd api && python -c "from database import SessionLocal; import db_queries; db = SessionLocal(); print(f'Startups: {db_queries.count_startups(db)}'); db.close()"
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Get startups
curl http://localhost:8000/startups/all?limit=10

# Get events
curl http://localhost:8000/calendar-events/

# Get enrichment stats
curl http://localhost:8000/startups/enrichment/stats

# Get current user
curl http://localhost:8000/api/current-user

# Get auroral themes
curl http://localhost:8000/api/auroral-themes
```

## 🎯 Top API Endpoints

```
GET  /health                                - Health check + DB stats
GET  /startups/all?skip=0&limit=100        - All startups (paginated)
GET  /startups/prioritized?user_id=X       - Prioritized for user
GET  /startups/enrichment/stats            - Enrichment statistics
GET  /calendar-events/                      - All calendar events
GET  /api/calendar-events/date-range       - Events in date range
POST /api/ratings                           - Add/update rating
GET  /api/ratings/average                   - Average ratings
GET  /ideas/                                - All ideas
POST /ideas/                                - Create idea
GET  /api/current-user                      - Get current user
POST /api/current-user                      - Set current user
GET  /api/finished-users                    - Finished users list
POST /api/finished-users                    - Mark user finished
GET  /api/auroral-themes                    - Auroral theme config
GET  /api/data-version                      - Data version string
```

## 🔍 Troubleshooting

### "No such table: startups"
```bash
# Database path might be wrong
cd api
python -c "from database import DB_PATH; print(f'DB Path: {DB_PATH}')"
# Should show: /home/akyo/startup_swiper/startup_swiper.db
```

### "Empty results"
```bash
# Re-run migration
python backend/migrate_json_to_db.py
```

### API won't start
```bash
# Test imports
cd api
python -c "import main; print('✓ main.py loads')"
```

## 📋 Checklist

- ✅ Tables created (`normalize_tables.py`)
- ✅ Data migrated (`migrate_json_to_db.py`)
- ✅ JSON syntax fixed (startup-ratings.md, finished-users.md)
- ✅ Query layer created (`db_queries.py`)
- ✅ Database path fixed (`database.py`)
- ✅ API endpoints updated (`main.py`)
- ✅ Utility endpoints added
- ✅ Documentation complete
- ✅ Verification passed

## 🎉 Next Steps

1. Start API server
2. Update frontend to use new API endpoints
3. Test all frontend features
4. Remove legacy JSON file reads
5. Deploy to production

## 📞 Support

See full documentation in `/docs/architecture/ddbb/` for:
- Complete schema reference
- Frontend integration examples
- API endpoint details
- Migration procedures
