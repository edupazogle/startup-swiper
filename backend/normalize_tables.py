"""Normalization script: creates additional tables representing previously JSON-stored datasets.
Run: python backend/normalize_tables.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'startup_swiper.db'

DDL = [
    # Messages
    '''CREATE TABLE IF NOT EXISTS ai_assistant_messages (
        id TEXT PRIMARY KEY,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp INTEGER NOT NULL
    )''',
    '''CREATE TABLE IF NOT EXISTS ai_chat_messages (
        id TEXT PRIMARY KEY,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp INTEGER NOT NULL
    )''',
    '''CREATE TABLE IF NOT EXISTS linkedin_chat_messages (
        id TEXT PRIMARY KEY,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp INTEGER NOT NULL
    )''',

    # Calendar events
    '''CREATE TABLE IF NOT EXISTS calendar_events (
        id TEXT PRIMARY KEY,
        title TEXT,
        start_time DATETIME,
        end_time DATETIME,
        type TEXT,
        stage TEXT,
        category TEXT,
        link TEXT,
        is_fixed BOOLEAN DEFAULT 0,
        highlight BOOLEAN DEFAULT 0
    )''',
    '''CREATE TABLE IF NOT EXISTS calendar_event_attendees (
        event_id TEXT NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
        attendee TEXT NOT NULL,
        PRIMARY KEY(event_id, attendee)
    )''',

    # Ideas
    '''CREATE TABLE IF NOT EXISTS ideas (
        id TEXT PRIMARY KEY,
        name TEXT,
        title TEXT,
        category TEXT,
        description TEXT,
        timestamp INTEGER
    )''',
    '''CREATE TABLE IF NOT EXISTS idea_tags (
        idea_id TEXT NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
        tag TEXT NOT NULL,
        PRIMARY KEY(idea_id, tag)
    )''',

    # Ratings
    '''CREATE TABLE IF NOT EXISTS startup_ratings (
        startup_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        PRIMARY KEY(startup_id, user_id)
    )''',

    # Finished users
    '''CREATE TABLE IF NOT EXISTS finished_users (
        user_id TEXT PRIMARY KEY,
        finished_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''',

    # Auroral info (themes + colors)
    '''CREATE TABLE IF NOT EXISTS auroral_info (
        id INTEGER PRIMARY KEY CHECK(id=1),
        description TEXT,
        last_viewed DATETIME
    )''',
    '''CREATE TABLE IF NOT EXISTS auroral_themes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        hours TEXT,
        mood TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS auroral_theme_colors (
        theme_id INTEGER NOT NULL REFERENCES auroral_themes(id) ON DELETE CASCADE,
        color TEXT NOT NULL,
        PRIMARY KEY(theme_id, color)
    )''',

    # Data/versioning & current user/admin
    '''CREATE TABLE IF NOT EXISTS data_version (
        version TEXT PRIMARY KEY,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE IF NOT EXISTS current_user (
        id TEXT PRIMARY KEY,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE IF NOT EXISTS admin_user (
        id TEXT PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''',

    # Votes (generic)
    '''CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        target_id TEXT,
        vote_value INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''',

    # User events (generic event log)
    '''CREATE TABLE IF NOT EXISTS user_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        event_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        metadata JSON
    )''',

    # Helpful indexes
    'CREATE INDEX IF NOT EXISTS ix_ai_assistant_messages_timestamp ON ai_assistant_messages(timestamp)',
    'CREATE INDEX IF NOT EXISTS ix_calendar_events_start ON calendar_events(start_time)',
    'CREATE INDEX IF NOT EXISTS ix_startup_ratings_user ON startup_ratings(user_id)',
    'CREATE INDEX IF NOT EXISTS ix_user_events_user ON user_events(user_id)',
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for stmt in DDL:
        cur.execute(stmt)
    conn.commit()
    print('Normalized tables ensured.')

if __name__ == '__main__':
    main()
