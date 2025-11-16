#!/usr/bin/env python3
"""
Import funding_stage from vclms export to database.
"""

import json
import sqlite3
import sys

DB_PATH = 'startup_swiper.db'
VCLMS_PATH = 'docs/startups_export.json'

def import_funding_stage():
    """Import funding stage from vclms export."""
    
    # Load vclms data
    with open(VCLMS_PATH, 'r') as f:
        vclms_data = json.load(f)
    
    startups = vclms_data.get('startups', [])
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    imported = 0
    updated = 0
    
    for startup in startups:
        name = startup.get('name', '').strip()
        if not name:
            continue
        
        imported += 1
        
        # Try to find in database
        cursor.execute("SELECT id FROM startups WHERE company_name = ? LIMIT 1", (name,))
        result = cursor.fetchone()
        
        if result:
            funding_stage = startup.get('funding_stage')
            if funding_stage:
                cursor.execute(
                    "UPDATE startups SET funding_stage = ? WHERE id = ?",
                    (funding_stage, result[0])
                )
                updated += 1
        
        if imported % 5000 == 0:
            print(f"Processed {imported}/{len(startups)} startups...", file=sys.stderr)
            conn.commit()
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Funding stage import complete:")
    print(f"  Total vclms startups processed: {imported}")
    print(f"  Records updated with funding_stage: {updated}")
    print(f"  Coverage: {updated}/{imported} ({100*updated//imported if imported else 0}%)")

if __name__ == '__main__':
    import_funding_stage()
