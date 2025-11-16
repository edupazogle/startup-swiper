#!/usr/bin/env python3
"""
Import logos from startups_data.json to the database.
Updates existing startups with logoUrl from the JSON export.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime


def load_json_startups():
    """Load startups from the JSON file."""
    json_path = Path('api/startups_data.json')
    with open(json_path, 'r') as f:
        return json.load(f)


def load_db_startups():
    """Load startup names from DB."""
    conn = sqlite3.connect('startup_swiper.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, company_name FROM startups")
    db_startups = {name.lower(): (id_, name) for id_, name in cursor.fetchall()}
    conn.close()
    return db_startups


def match_startups(json_startups, db_startups):
    """Match JSON startups to DB startups by name."""
    matches = []
    for json_startup in json_startups:
        json_name = json_startup['name'].lower()
        if json_name in db_startups:
            db_id, db_name = db_startups[json_name]
            if json_startup.get('logoUrl'):
                matches.append({
                    'db_id': db_id,
                    'db_name': db_name,
                    'json_name': json_startup['name'],
                    'logoUrl': json_startup['logoUrl']
                })
    return matches


def update_logos(conn, db_id, logo_url):
    """Update startup with logo URL."""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE startups
        SET logoUrl = ?
        WHERE id = ?
    """, (logo_url, db_id))
    conn.commit()


def main():
    print("=" * 70)
    print("LOGO IMPORT FROM startups_data.json")
    print("=" * 70)
    
    # Load data
    print("\n[1/4] Loading JSON startups...")
    json_startups = load_json_startups()
    print(f"  Loaded {len(json_startups)} startups from JSON")
    
    print("\n[2/4] Loading DB startups...")
    db_startups = load_db_startups()
    print(f"  Loaded {len(db_startups)} startups from database")
    
    print("\n[3/4] Matching startups and importing logos...")
    matches = match_startups(json_startups, db_startups)
    print(f"  Found {len(matches)} startups with logos to import")
    
    # Update database
    conn = sqlite3.connect('startup_swiper.db')
    updated_count = 0
    
    for match in matches:
        update_logos(conn, match['db_id'], match['logoUrl'])
        updated_count += 1
        if updated_count % 100 == 0:
            print(f"    Progress: {updated_count}/{len(matches)}")
    
    conn.close()
    
    print(f"  Updated {updated_count} startups with logos")
    
    # Verification
    print("\n[4/4] Verification...")
    conn = sqlite3.connect('startup_swiper.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM startups WHERE logoUrl IS NOT NULL")
    count = cursor.fetchone()[0]
    print(f"  Startups with logos: {count}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print(f"✓ Logo import complete - {updated_count} startups updated")
    print("=" * 70)


if __name__ == '__main__':
    main()
