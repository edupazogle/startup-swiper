# Database Schema Documentation

## Overview
The database has been normalized from JSON files into proper relational tables.

## Setup

### 1. Create Normalized Tables
```bash
python backend/normalize_tables.py
```

### 2. Migrate Existing JSON Data
```bash
python backend/migrate_json_to_db.py
```

## Database Schema

### Core Tables

#### `startups` (3478 records)
Main startup data with enriched information.
- **Primary Key**: `id` (INTEGER)
- **Key Fields**: company_name, company_type, website, employees, totalFunding, currentInvestmentStage
- **JSON Fields**: secondary_industry, business_types, topics, tech, files, enrichment
- **Indexes**: company_name, company_country, primary_industry, is_enriched

#### `ai_assistant_messages` (1 record)
AI assistant chat history.
- **Primary Key**: `id` (TEXT)
- **Fields**: role, content, timestamp
- **Index**: timestamp

#### `ai_chat_messages`
General AI chat messages (currently empty).
- **Schema**: Same as ai_assistant_messages

#### `linkedin_chat_messages`
LinkedIn chat integration messages (currently empty).
- **Schema**: Same as ai_assistant_messages

#### `calendar_events` (52 records)
Slush 2025 event schedule.
- **Primary Key**: `id` (TEXT)
- **Fields**: title, start_time, end_time, type, stage, category, link, is_fixed, highlight
- **Related**: calendar_event_attendees (attendee list)
- **Index**: start_time

#### `calendar_event_attendees`
Many-to-many relationship for event attendees.
- **Composite Key**: (event_id, attendee)
- **Foreign Key**: event_id → calendar_events(id)

#### `ideas` (1 record)
User-submitted startup ideas.
- **Primary Key**: `id` (TEXT)
- **Fields**: name, title, category, description, timestamp
- **Related**: idea_tags (tag list)

#### `idea_tags`
Tags associated with ideas.
- **Composite Key**: (idea_id, tag)
- **Foreign Key**: idea_id → ideas(id)

#### `startup_ratings` (7 records)
User ratings for startups (1-5 stars).
- **Composite Key**: (startup_id, user_id)
- **Constraint**: rating BETWEEN 1 AND 5
- **Index**: user_id

#### `finished_users` (1 record)
Users who completed the swiper flow.
- **Primary Key**: `user_id` (TEXT)
- **Fields**: finished_at (timestamp)

#### `auroral_info` (1 record)
Aurora background configuration.
- **Primary Key**: `id` (INTEGER, must be 1)
- **Fields**: description, last_viewed
- **Related**: auroral_themes

#### `auroral_themes` (6 records)
Time-based color themes for aurora effect.
- **Primary Key**: `id` (AUTOINCREMENT)
- **Fields**: name, hours, mood
- **Related**: auroral_theme_colors (color palette)

#### `auroral_theme_colors`
Colors for each theme.
- **Composite Key**: (theme_id, color)
- **Foreign Key**: theme_id → auroral_themes(id)

#### `data_version` (1 record)
Dataset version tracking.
- **Primary Key**: `version` (TEXT)
- **Current**: v3-6715-startups
- **Fields**: updated_at (timestamp)

#### `current_user` (1 record)
Current active user ID.
- **Primary Key**: `id` (TEXT)
- **Current**: 116544866
- **Fields**: updated_at (timestamp)

#### `admin_user`
Administrative users (currently empty).
- **Primary Key**: `id` (TEXT)
- **Fields**: created_at (timestamp)

#### `votes`
Generic voting system (currently empty).
- **Primary Key**: `id` (AUTOINCREMENT)
- **Fields**: user_id, target_id, vote_value, created_at

#### `user_events`
Event logging system (currently empty).
- **Primary Key**: `id` (AUTOINCREMENT)
- **Fields**: user_id, event_type, event_timestamp, metadata (JSON)
- **Index**: user_id

## Data Sources

Original JSON files located in `docs/architecture/ddbb/`:
- ✅ `ai-assistant-messages.md` → ai_assistant_messages
- ✅ `calendar-events.md` → calendar_events + calendar_event_attendees
- ✅ `ideas.md` → ideas + idea_tags
- ✅ `startup-ratings.md` → startup_ratings (fixed JSON syntax)
- ✅ `finished-users.md` → finished_users (fixed JSON syntax)
- ✅ `auroral-info.md` → auroral_info + auroral_themes + auroral_theme_colors
- ✅ `data-version.md` → data_version
- ✅ `current-user-id.md` → current_user

## Issues Fixed

### JSON Syntax Errors Corrected
1. **startup-ratings.md**: Removed stray 'z' character on line 7
2. **finished-users.md**: Removed stray 'a' character on line 2

## Sample Queries

### Get upcoming calendar events
```sql
SELECT id, title, start_time, stage 
FROM calendar_events 
WHERE start_time > datetime('now')
ORDER BY start_time
LIMIT 10;
```

### Get top-rated startups
```sql
SELECT s.company_name, AVG(sr.rating) as avg_rating, COUNT(sr.user_id) as num_ratings
FROM startups s
JOIN startup_ratings sr ON CAST(s.id AS TEXT) = sr.startup_id
GROUP BY s.id, s.company_name
ORDER BY avg_rating DESC, num_ratings DESC;
```

### Get events by category
```sql
SELECT category, COUNT(*) as event_count
FROM calendar_events
WHERE category IS NOT NULL
GROUP BY category
ORDER BY event_count DESC;
```

### Find enriched startups with funding
```sql
SELECT company_name, totalFunding, currentInvestmentStage, employees
FROM startups
WHERE is_enriched = 1 
  AND totalFunding IS NOT NULL
ORDER BY totalFunding DESC
LIMIT 20;
```

### Get auroral theme for current hour
```sql
SELECT t.name, t.mood, GROUP_CONCAT(tc.color) as colors
FROM auroral_themes t
JOIN auroral_theme_colors tc ON t.id = tc.theme_id
WHERE CAST(strftime('%H', 'now', 'localtime') AS INTEGER) 
  BETWEEN CAST(substr(t.hours, 1, 2) AS INTEGER) 
  AND CAST(substr(t.hours, 8, 2) AS INTEGER)
GROUP BY t.id;
```

## Next Steps

1. ✅ Normalize tables created
2. ✅ JSON data migrated
3. ✅ JSON syntax errors fixed
4. 🔄 Update application code to use SQL instead of JSON files
5. 🔄 Add foreign key constraints to startups table for referential integrity
6. 🔄 Create views for common queries
7. 🔄 Add migration script to CI/CD pipeline

## Maintenance

Re-run migration after updating JSON files:
```bash
python backend/migrate_json_to_db.py
```

This will use `INSERT OR REPLACE` to update existing records.
