"""Migration script: populates normalized tables from JSON docs.
Run: python backend/migrate_json_to_db.py
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / 'startup_swiper.db'
DOCS_PATH = Path(__file__).resolve().parent.parent / 'docs' / 'architecture' / 'ddbb'

def migrate_messages(conn, file_name, table_name):
    """Migrate message JSON arrays to message tables."""
    file_path = DOCS_PATH / file_name
    if not file_path.exists():
        print(f'  ⚠️  {file_name} not found, skipping')
        return
    
    data = json.loads(file_path.read_text() or '[]')
    if not data:
        print(f'  ⚠️  {file_name} empty, skipping')
        return
    
    cur = conn.cursor()
    for msg in data:
        cur.execute(f'''
            INSERT OR REPLACE INTO {table_name} (id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (msg['id'], msg['role'], msg['content'], msg['timestamp']))
    conn.commit()
    print(f'  ✓ Migrated {len(data)} messages to {table_name}')

def migrate_calendar_events(conn):
    """Migrate calendar events from JSON."""
    file_path = DOCS_PATH / 'calendar-events.md'
    if not file_path.exists():
        print(f'  ⚠️  calendar-events.md not found, skipping')
        return
    
    data = json.loads(file_path.read_text() or '[]')
    if not data:
        print(f'  ⚠️  calendar-events.md empty, skipping')
        return
    
    cur = conn.cursor()
    for event in data:
        cur.execute('''
            INSERT OR REPLACE INTO calendar_events 
            (id, title, start_time, end_time, type, stage, category, link, is_fixed, highlight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event['id'],
            event.get('title'),
            event.get('startTime'),
            event.get('endTime'),
            event.get('type'),
            event.get('stage'),
            event.get('category'),
            event.get('link'),
            event.get('isFixed', False),
            event.get('highlight', False)
        ))
        
        # Migrate attendees
        for attendee in event.get('attendees', []):
            cur.execute('''
                INSERT OR IGNORE INTO calendar_event_attendees (event_id, attendee)
                VALUES (?, ?)
            ''', (event['id'], attendee))
    
    conn.commit()
    print(f'  ✓ Migrated {len(data)} calendar events')

def migrate_ideas(conn):
    """Migrate ideas from JSON."""
    file_path = DOCS_PATH / 'ideas.md'
    if not file_path.exists():
        print(f'  ⚠️  ideas.md not found, skipping')
        return
    
    data = json.loads(file_path.read_text() or '[]')
    if not data:
        print(f'  ⚠️  ideas.md empty, skipping')
        return
    
    cur = conn.cursor()
    for idea in data:
        cur.execute('''
            INSERT OR REPLACE INTO ideas (id, name, title, category, description, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            idea['id'],
            idea.get('name'),
            idea.get('title'),
            idea.get('category'),
            idea.get('description'),
            idea.get('timestamp')
        ))
        
        # Migrate tags
        for tag in idea.get('tags', []):
            cur.execute('''
                INSERT OR IGNORE INTO idea_tags (idea_id, tag)
                VALUES (?, ?)
            ''', (idea['id'], tag))
    
    conn.commit()
    print(f'  ✓ Migrated {len(data)} ideas')

def migrate_startup_ratings(conn):
    """Migrate startup ratings from JSON."""
    file_path = DOCS_PATH / 'startup-ratings.md'
    if not file_path.exists():
        print(f'  ⚠️  startup-ratings.md not found, skipping')
        return
    
    content = file_path.read_text().strip()
    if not content:
        print(f'  ⚠️  startup-ratings.md empty, skipping')
        return
    
    data = json.loads(content)
    cur = conn.cursor()
    count = 0
    for startup_id, ratings in data.items():
        for user_id, rating in ratings.items():
            cur.execute('''
                INSERT OR REPLACE INTO startup_ratings (startup_id, user_id, rating)
                VALUES (?, ?, ?)
            ''', (startup_id, user_id, rating))
            count += 1
    
    conn.commit()
    print(f'  ✓ Migrated {count} startup ratings')

def migrate_finished_users(conn):
    """Migrate finished users from JSON."""
    file_path = DOCS_PATH / 'finished-users.md'
    if not file_path.exists():
        print(f'  ⚠️  finished-users.md not found, skipping')
        return
    
    content = file_path.read_text().strip()
    if not content:
        print(f'  ⚠️  finished-users.md empty, skipping')
        return
    
    data = json.loads(content)
    cur = conn.cursor()
    for user_id in data:
        cur.execute('''
            INSERT OR IGNORE INTO finished_users (user_id)
            VALUES (?)
        ''', (user_id,))
    
    conn.commit()
    print(f'  ✓ Migrated {len(data)} finished users')

def migrate_auroral_info(conn):
    """Migrate auroral info from JSON."""
    file_path = DOCS_PATH / 'auroral-info.md'
    if not file_path.exists():
        print(f'  ⚠️  auroral-info.md not found, skipping')
        return
    
    content = file_path.read_text().strip()
    if not content:
        print(f'  ⚠️  auroral-info.md empty, skipping')
        return
    
    data = json.loads(content)
    cur = conn.cursor()
    
    # Insert main auroral info
    cur.execute('''
        INSERT OR REPLACE INTO auroral_info (id, description, last_viewed)
        VALUES (1, ?, ?)
    ''', (data.get('description'), data.get('lastViewed')))
    
    # Clear and re-insert themes
    cur.execute('DELETE FROM auroral_theme_colors')
    cur.execute('DELETE FROM auroral_themes')
    
    for theme in data.get('themes', []):
        cur.execute('''
            INSERT INTO auroral_themes (name, hours, mood)
            VALUES (?, ?, ?)
        ''', (theme['name'], theme['hours'], theme['mood']))
        theme_id = cur.lastrowid
        
        for color in theme.get('colors', []):
            cur.execute('''
                INSERT INTO auroral_theme_colors (theme_id, color)
                VALUES (?, ?)
            ''', (theme_id, color))
    
    conn.commit()
    print(f'  ✓ Migrated auroral info with {len(data.get("themes", []))} themes')

def migrate_data_version(conn):
    """Migrate data version from text file."""
    file_path = DOCS_PATH / 'data-version.md'
    if not file_path.exists():
        print(f'  ⚠️  data-version.md not found, skipping')
        return
    
    version = file_path.read_text().strip()
    if not version:
        print(f'  ⚠️  data-version.md empty, skipping')
        return
    
    cur = conn.cursor()
    cur.execute('''
        INSERT OR REPLACE INTO data_version (version)
        VALUES (?)
    ''', (version,))
    conn.commit()
    print(f'  ✓ Migrated data version: {version}')

def migrate_current_user(conn):
    """Migrate current user ID from text file."""
    file_path = DOCS_PATH / 'current-user-id.md'
    if not file_path.exists():
        print(f'  ⚠️  current-user-id.md not found, skipping')
        return
    
    user_id = file_path.read_text().strip()
    if not user_id:
        print(f'  ⚠️  current-user-id.md empty, skipping')
        return
    
    cur = conn.cursor()
    cur.execute('''
        INSERT OR REPLACE INTO current_user (id)
        VALUES (?)
    ''', (user_id,))
    conn.commit()
    print(f'  ✓ Migrated current user: {user_id}')

def main():
    print('🔄 Starting migration from JSON to normalized tables...\n')
    
    conn = sqlite3.connect(DB_PATH)
    
    print('📧 Migrating message tables...')
    migrate_messages(conn, 'ai-assistant-messages.md', 'ai_assistant_messages')
    migrate_messages(conn, 'ai-chat-messages.md', 'ai_chat_messages')
    migrate_messages(conn, 'linkedin-chat-messages.md', 'linkedin_chat_messages')
    
    print('\n📅 Migrating calendar events...')
    migrate_calendar_events(conn)
    
    print('\n💡 Migrating ideas...')
    migrate_ideas(conn)
    
    print('\n⭐ Migrating startup ratings...')
    migrate_startup_ratings(conn)
    
    print('\n✅ Migrating finished users...')
    migrate_finished_users(conn)
    
    print('\n🌌 Migrating auroral info...')
    migrate_auroral_info(conn)
    
    print('\n📊 Migrating metadata...')
    migrate_data_version(conn)
    migrate_current_user(conn)
    
    conn.close()
    print('\n✨ Migration complete!')

if __name__ == '__main__':
    main()
