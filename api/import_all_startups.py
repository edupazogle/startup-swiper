#!/usr/bin/env python3
"""
Import all startups from slush_full.json into the database

This imports 6044 startups for comprehensive evaluation
"""

import json
import sys
from pathlib import Path
from database import SessionLocal
from models_startup import Startup
from datetime import datetime

def import_all_startups():
    """Import all startups from slush_full.json"""
    
    # Load startup data
    json_file = Path(__file__).parent.parent / 'app' / 'startup-swipe-schedu' / 'startups' / 'slush_full.json'
    
    if not json_file.exists():
        print(f"❌ File not found: {json_file}")
        sys.exit(1)
    
    print(f"📖 Loading startups from {json_file}...")
    with open(json_file, 'r') as f:
        all_startups = json.load(f)
    
    print(f"✓ Loaded {len(all_startups)} startups from JSON")
    
    # Connect to database
    db = SessionLocal()
    
    # Check existing
    existing_count = db.query(Startup).count()
    print(f"📊 Current database has {existing_count} startups")
    
    # Get existing company names to avoid duplicates
    existing_names = set([s.company_name for s in db.query(Startup.company_name).all()])
    print(f"✓ Found {len(existing_names)} existing company names")
    
    # Import new startups
    imported = 0
    skipped = 0
    errors = 0
    
    print(f"\n🚀 Starting import...")
    
    for i, startup_data in enumerate(all_startups, 1):
        try:
            company_name = startup_data.get('company_name')
            
            if not company_name:
                skipped += 1
                continue
            
            # Skip if already exists
            if company_name in existing_names:
                skipped += 1
                continue
            
            # Create new startup
            startup = Startup(
                company_name=company_name,
                company_type=startup_data.get('company_type'),
                company_country=startup_data.get('company_country'),
                company_city=startup_data.get('company_city'),
                website=startup_data.get('website'),
                company_linked_in=startup_data.get('company_linked_in'),
                company_description=startup_data.get('company_description'),
                founding_year=startup_data.get('founding_year'),
                primary_industry=startup_data.get('primary_industry'),
                secondary_industry=json.dumps(startup_data.get('secondary_industry')) if startup_data.get('secondary_industry') else None,
                focus_industries=startup_data.get('focus_industries'),
                business_types=json.dumps(startup_data.get('business_types')) if startup_data.get('business_types') else None,
                curated_collections_tags=startup_data.get('curated_collections_tags'),
                topics=json.dumps(startup_data.get('topics')) if startup_data.get('topics') else None,
                tech=json.dumps(startup_data.get('tech')) if startup_data.get('tech') else None,
                employees=startup_data.get('employees'),
                shortDescription=startup_data.get('shortDescription'),
                profile_link=startup_data.get('profile_link'),
                # CB Insights funding data (will be populated by enrichment service)
                funding_source='CB Insights API v2'
            )
            
            db.add(startup)
            imported += 1
            
            # Commit in batches
            if imported % 100 == 0:
                db.commit()
                print(f"  Progress: {imported} imported, {skipped} skipped, {errors} errors ({i}/{len(all_startups)})")
        
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ⚠️  Error importing {company_name}: {e}")
            continue
    
    # Final commit
    db.commit()
    
    print(f"\n{'='*80}")
    print(f"✅ Import Complete!")
    print(f"{'='*80}")
    print(f"  Imported: {imported} new startups")
    print(f"  Skipped: {skipped} (already in database)")
    print(f"  Errors: {errors}")
    print(f"  Total in database: {db.query(Startup).count()}")
    
    db.close()


if __name__ == '__main__':
    import_all_startups()
