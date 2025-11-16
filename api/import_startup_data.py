#!/usr/bin/env python3
"""
Import core startup fields from startups_data.json to database.
Matches startups by name and imports key missing fields.
"""

import json
import sqlite3
from datetime import datetime
import sys

DB_PATH = 'startup_swiper.db'
JSON_PATH = 'api/startups_data.json'

def load_json_data():
    """Load startup data from JSON file."""
    with open(JSON_PATH, 'r') as f:
        return json.load(f)

def extract_year(date_str):
    """Extract year from ISO date string."""
    if not date_str:
        return None
    try:
        return int(date_str.split('-')[0]) if isinstance(date_str, str) else None
    except:
        return None

def import_startup_data():
    """Import startup data from JSON to database."""
    json_startups = load_json_data()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create index for faster lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_name ON startups(company_name)")
    
    imported = 0
    matched = 0
    updated = 0
    
    for json_startup in json_startups:
        name = json_startup.get('name', '').strip()
        if not name:
            continue
        
        # Try to find in database
        cursor.execute("SELECT id FROM startups WHERE company_name = ? LIMIT 1", (name,))
        result = cursor.fetchone()
        
        if result:
            startup_id = result[0]
            matched += 1
            
            # Prepare update fields - only update if not already set
            updates = {}
            
            # Critical fields to import
            if json_startup.get('description'):
                updates['description'] = json_startup['description']
            
            if json_startup.get('shortDescription'):
                updates['shortDescription'] = json_startup['shortDescription']
            
            if json_startup.get('employees'):
                updates['employees'] = json_startup['employees']
            
            if json_startup.get('maturity'):
                updates['maturity'] = json_startup['maturity']
            
            if json_startup.get('maturity_score') is not None:
                updates['maturity_score'] = json_startup['maturity_score']
            
            # Extract year from dateFounded
            founded_date = json_startup.get('dateFounded')
            if founded_date:
                year = extract_year(founded_date)
                if year:
                    updates['founding_year'] = year
            
            # Billing info
            if json_startup.get('billingCity'):
                updates['billingCity'] = json_startup['billingCity']
            
            if json_startup.get('billingCountry'):
                updates['billingCountry'] = json_startup['billingCountry']
            
            if json_startup.get('billingState'):
                updates['billingState'] = json_startup['billingState']
            
            if json_startup.get('billingStreet'):
                updates['billingStreet'] = json_startup['billingStreet']
            
            if json_startup.get('billingPostalCode'):
                updates['billingPostalCode'] = json_startup['billingPostalCode']
            
            # Other enrichment fields
            if json_startup.get('pricingModel'):
                updates['pricingModel'] = json_startup['pricingModel']
            
            if json_startup.get('technologyReadiness'):
                updates['technologyReadiness'] = json_startup['technologyReadiness']
            
            if json_startup.get('legalEntity'):
                updates['legalEntity'] = json_startup['legalEntity']
            
            # Topics and tech (store as JSON)
            if json_startup.get('topics'):
                updates['topics'] = json.dumps(json_startup['topics'])
            
            if json_startup.get('tech'):
                updates['tech'] = json.dumps(json_startup['tech'])
            
            # Enrichment data
            if json_startup.get('enrichment'):
                updates['enrichment'] = json.dumps(json_startup['enrichment'])
            
            # Mark as enriched
            updates['is_enriched'] = 1
            updates['last_enriched_date'] = datetime.now().isoformat()
            
            # Build UPDATE query
            if updates:
                set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
                values = list(updates.values())
                values.append(startup_id)
                
                query = f"UPDATE startups SET {set_clause} WHERE id = ?"
                cursor.execute(query, values)
                updated += 1
        
        imported += 1
        if imported % 500 == 0:
            print(f"Processed {imported}/{len(json_startups)} startups...", file=sys.stderr)
            conn.commit()
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Import Complete:")
    print(f"  Total JSON startups processed: {imported}")
    print(f"  Matched in database: {matched}")
    print(f"  Records updated: {updated}")
    print(f"  Coverage: {matched}/{imported} ({100*matched//imported}%)")

if __name__ == '__main__':
    import_startup_data()
