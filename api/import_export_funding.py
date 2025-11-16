#!/usr/bin/env python3
"""
Import funding data from vclms export to enrich existing startups in the database.
Only imports matched startups (exact name match).
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path


def load_export_data():
    """Load the vclms export data."""
    export_path = Path('docs/startups_export.json')
    with open(export_path, 'r') as f:
        data = json.load(f)
    return data['startups']


def load_db_startups():
    """Load existing startups from DB."""
    conn = sqlite3.connect('startup_swiper.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, company_name FROM startups;")
    db_startups = {name.lower(): (id_, name) for id_, name in cursor.fetchall()}
    conn.close()
    return db_startups


def match_startups(export_startups, db_startups):
    """Match export startups to DB startups by name."""
    matches = []
    for export_startup in export_startups:
        export_name = export_startup['name'].lower()
        if export_name in db_startups:
            db_id, db_name = db_startups[export_name]
            matches.append({
                'db_id': db_id,
                'db_name': db_name,
                'export_startup': export_startup
            })
    return matches


def extract_funding_data(export_startup):
    """Extract funding-related fields from export startup."""
    return {
        'total_funding': export_startup.get('total_funding'),
        'funding_stage': export_startup.get('funding_stage'),
        'last_funding_date': export_startup.get('last_funding_date'),
        'lead_investors': export_startup.get('lead_investors'),
        'current_investment_stage': export_startup.get('current_investment_stage'),
    }


def update_startup_funding(conn, db_id, funding_data):
    """Update startup with funding data."""
    cursor = conn.cursor()
    
    # Parse funding amount (may be string with currency)
    total_funding = None
    if funding_data['total_funding']:
        try:
            if isinstance(funding_data['total_funding'], str):
                # Try to extract numeric value
                import re
                match = re.search(r'[\d.]+', funding_data['total_funding'].replace(',', ''))
                if match:
                    total_funding = float(match.group())
            else:
                total_funding = float(funding_data['total_funding'])
        except (ValueError, TypeError):
            pass
    
    # Parse last funding date
    last_funding_date = funding_data['last_funding_date']
    funding_stage = funding_data['funding_stage']
    
    # Update database with available columns
    cursor.execute("""
        UPDATE startups
        SET 
            total_funding = ?,
            last_funding_date = ?,
            funding_source = ?,
            last_enriched_date = ?
        WHERE id = ?
    """, (
        total_funding,
        last_funding_date,
        funding_stage,
        datetime.now().isoformat(),
        db_id
    ))
    conn.commit()


def main():
    print("=" * 70)
    print("STARTUP FUNDING IMPORT")
    print("=" * 70)
    
    # Load data
    print("\n[1/5] Loading export data...")
    export_startups = load_export_data()
    print(f"  Loaded {len(export_startups):,} startups from export")
    
    print("\n[2/5] Loading DB startups...")
    db_startups = load_db_startups()
    print(f"  Loaded {len(db_startups):,} startups from database")
    
    print("\n[3/5] Matching startups by name...")
    matches = match_startups(export_startups, db_startups)
    print(f"  Found {len(matches)} exact name matches")
    
    print("\n[4/5] Importing funding data...")
    conn = sqlite3.connect('startup_swiper.db')
    
    updated_count = 0
    funding_stats = {
        'total_funding_updated': 0,
        'last_funding_date_updated': 0,
        'funding_stage_updated': 0,
    }
    
    for match in matches:
        db_id = match['db_id']
        export_startup = match['export_startup']
        
        funding_data = extract_funding_data(export_startup)
        
        # Count updates
        if funding_data['total_funding']:
            funding_stats['total_funding_updated'] += 1
        if funding_data['last_funding_date']:
            funding_stats['last_funding_date_updated'] += 1
        if funding_data['funding_stage']:
            funding_stats['funding_stage_updated'] += 1
        
        update_startup_funding(conn, db_id, funding_data)
        updated_count += 1
    
    conn.close()
    
    print(f"  Updated {updated_count} startups with funding data:")
    print(f"    - total_funding: {funding_stats['total_funding_updated']} records")
    print(f"    - last_funding_date: {funding_stats['last_funding_date_updated']} records")
    print(f"    - funding_stage: {funding_stats['funding_stage_updated']} records")
    
    print("\n[5/5] Verification...")
    conn = sqlite3.connect('startup_swiper.db')
    cursor = conn.cursor()
    
    # Check how many startups now have funding data
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN total_funding IS NOT NULL THEN 1 END) as with_funding,
            COUNT(CASE WHEN last_funding_date IS NOT NULL THEN 1 END) as with_funding_date,
            COUNT(CASE WHEN funding_source IS NOT NULL THEN 1 END) as with_stage
        FROM startups
    """)
    counts = cursor.fetchone()
    print(f"  Startups with total_funding: {counts[0]:,}")
    print(f"  Startups with last_funding_date: {counts[1]:,}")
    print(f"  Startups with funding_stage: {counts[2]:,}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print(f"✓ Import complete - {updated_count} startups enriched with funding data")
    print("=" * 70)


if __name__ == '__main__':
    main()
