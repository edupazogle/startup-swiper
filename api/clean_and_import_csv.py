#!/usr/bin/env python3
"""
Clean Database and Import Only CSV Startups

This script:
1. Reads docs/slush_complete.csv (3666 startups)
2. Removes startups from DB that are NOT in CSV (2524 to remove)
3. Adds startups from CSV that are NOT in DB (144 to add)
4. Final result: 3666 startups in DB (matching CSV exactly)

Usage:
    python3 api/clean_and_import_csv.py
"""

import csv
import json
from pathlib import Path
from database import SessionLocal
from models_startup import Startup
from datetime import datetime

def clean_and_import():
    """Clean database and import only CSV startups"""
    
    print("\n" + "="*80)
    print("DATABASE CLEANUP - Keep Only CSV Startups")
    print("="*80)
    
    # Load CSV
    csv_path = Path(__file__).parent.parent / 'docs' / 'slush_complete.csv'
    
    print(f"\n📖 Loading CSV: {csv_path}")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_startups = list(reader)
    
    print(f"✓ Loaded {len(csv_startups)} startups from CSV")
    
    # Create lookup by company name
    csv_dict = {}
    for row in csv_startups:
        # Handle BOM in first column
        name_key = '﻿company_name' if '﻿company_name' in row else 'company_name'
        company_name = row[name_key].strip()
        csv_dict[company_name] = row
    
    csv_names = set(csv_dict.keys())
    print(f"✓ {len(csv_names)} unique company names in CSV")
    
    # Connect to database
    db = SessionLocal()
    
    # Get all current startups
    all_startups = db.query(Startup).all()
    current_count = len(all_startups)
    print(f"\n📊 Current database: {current_count} startups")
    
    # Compare
    db_names = set([s.company_name for s in all_startups])
    
    to_delete = db_names - csv_names
    to_add = csv_names - db_names
    to_keep = db_names & csv_names
    
    print(f"\n📊 Analysis:")
    print(f"  Startups in both: {len(to_keep)}")
    print(f"  To DELETE: {len(to_delete)}")
    print(f"  To ADD: {len(to_add)}")
    
    # Confirm action
    print(f"\n⚠️  WARNING:")
    print(f"  This will DELETE {len(to_delete)} startups from database")
    print(f"  This will ADD {len(to_add)} startups from CSV")
    print(f"  Final count will be: {len(csv_names)} startups")
    
    response = input(f"\n  Proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Aborted")
        db.close()
        return
    
    # Step 1: Delete startups not in CSV
    print(f"\n🗑️  Deleting {len(to_delete)} startups not in CSV...")
    deleted = 0
    for startup in all_startups:
        if startup.company_name in to_delete:
            db.delete(startup)
            deleted += 1
            if deleted % 100 == 0:
                db.commit()
                print(f"  Deleted {deleted}/{len(to_delete)}...")
    
    db.commit()
    print(f"✓ Deleted {deleted} startups")
    
    # Step 2: Add startups from CSV that aren't in DB
    print(f"\n➕ Adding {len(to_add)} new startups from CSV...")
    added = 0
    errors = 0
    
    for company_name in to_add:
        try:
            row = csv_dict[company_name]
            
            # Get the correct column name (with or without BOM)
            name_key = '﻿company_name' if '﻿company_name' in row else 'company_name'
            
            # Parse JSON fields
            secondary_industry = row.get('secondary_industry', '')
            if secondary_industry and secondary_industry != '':
                try:
                    # Already JSON string, just validate
                    json.loads(secondary_industry)
                except:
                    secondary_industry = json.dumps([secondary_industry])
            else:
                secondary_industry = None
            
            business_types = row.get('business_types', '')
            if business_types and business_types != '':
                try:
                    json.loads(business_types)
                except:
                    business_types = json.dumps([business_types])
            else:
                business_types = None
            
            # Create startup
            startup = Startup(
                company_name=row[name_key].strip(),
                company_type=row.get('company_type'),
                company_country=row.get('company_country'),
                company_city=row.get('company_city'),
                website=row.get('website'),
                company_linked_in=row.get('company_linked_in'),
                company_description=row.get('company_description'),
                founding_year=int(row['founding_year']) if row.get('founding_year') and row['founding_year'].isdigit() else None,
                primary_industry=row.get('primary_industry'),
                secondary_industry=secondary_industry,
                focus_industries=row.get('focus_industries'),
                business_types=business_types,
                curated_collections_tags=row.get('curated_collections_tags'),
                prominent_investors=row.get('prominent_investors'),
                profile_link=row.get('profile_link')
            )
            
            db.add(startup)
            added += 1
            
            if added % 50 == 0:
                db.commit()
                print(f"  Added {added}/{len(to_add)}...")
        
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ⚠️  Error adding {company_name}: {e}")
            continue
    
    db.commit()
    print(f"✓ Added {added} new startups")
    
    # Verify final count
    final_count = db.query(Startup).count()
    
    print(f"\n{'='*80}")
    print(f"✅ Database Cleanup Complete!")
    print(f"{'='*80}")
    print(f"  Previous count: {current_count}")
    print(f"  Deleted: {deleted}")
    print(f"  Added: {added}")
    print(f"  Final count: {final_count}")
    print(f"  Expected: {len(csv_names)}")
    
    if final_count == len(csv_names):
        print(f"\n✅ SUCCESS: Database matches CSV exactly!")
    else:
        print(f"\n⚠️  WARNING: Count mismatch - Expected {len(csv_names)}, got {final_count}")
    
    db.close()


if __name__ == '__main__':
    clean_and_import()
