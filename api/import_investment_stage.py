#!/usr/bin/env python3
"""
Import investment stage from startups_data.json to fill gaps in funding_stage.
"""

import json
import sqlite3
import sys

DB_PATH = 'startup_swiper.db'
JSON_PATH = 'api/startups_data.json'

def import_investment_stage():
    """Import investment stage from JSON to fill funding_stage gaps."""
    
    with open(JSON_PATH, 'r') as f:
        json_startups = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    imported = 0
    updated = 0
    
    for startup in json_startups:
        name = startup.get('name', '').strip()
        if not name:
            continue
        
        imported += 1
        
        # Try to find in database
        cursor.execute(
            "SELECT id, funding_stage FROM startups WHERE company_name = ? LIMIT 1",
            (name,)
        )
        result = cursor.fetchone()
        
        if result:
            startup_id, existing_stage = result
            
            # Only update if funding_stage is NULL or empty
            if not existing_stage:
                investment_stage = startup.get('currentInvestmentStage')
                if investment_stage:
                    cursor.execute(
                        "UPDATE startups SET funding_stage = ? WHERE id = ?",
                        (investment_stage, startup_id)
                    )
                    updated += 1
        
        if imported % 500 == 0:
            print(f"Processed {imported}/{len(json_startups)} startups...", file=sys.stderr)
            conn.commit()
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Investment stage import complete:")
    print(f"  Total JSON startups processed: {imported}")
    print(f"  Records updated with funding_stage: {updated}")
    print(f"  Coverage: {updated}/{imported} ({100*updated//imported if imported else 0}%)")

if __name__ == '__main__':
    import_investment_stage()
