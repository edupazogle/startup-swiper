#!/usr/bin/env python3
"""
Fast Deployment of Enriched Data to Database
Merges previously enriched data and prepares for production
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    base_path = Path(__file__).parent.parent
    
    # File paths
    enriched_file = base_path / "docs/architecture/ddbb/slush2_enriched.json"
    database_file = base_path / "docs/architecture/ddbb/slush2_extracted.json"
    app_database = base_path / "app/startup-swipe-schedu/startups/slush2_extracted.json"
    
    logger.info("="*60)
    logger.info("ENRICHED DATA DEPLOYMENT")
    logger.info("="*60)
    
    # Load database
    logger.info("Loading startup database...")
    try:
        with open(database_file, 'r', encoding='utf-8') as f:
            database = json.load(f)
        logger.info(f"✓ Loaded {len(database)} startups")
    except Exception as e:
        logger.error(f"Failed to load database: {e}")
        sys.exit(1)
    
    # Load enriched data if available
    enriched_lookup = {}
    if enriched_file.exists():
        try:
            with open(enriched_file, 'r', encoding='utf-8') as f:
                enriched_list = json.load(f)
                if isinstance(enriched_list, list):
                    enriched_lookup = {s.get('name', ''): s for s in enriched_list}
                else:
                    enriched_lookup = {enriched_list.get('name', ''): enriched_list}
            logger.info(f"✓ Loaded {len(enriched_lookup)} enriched startups")
        except Exception as e:
            logger.warning(f"Could not load enriched data: {e}")
    
    # Merge enrichment into database
    logger.info("Merging enrichment data...")
    updated_count = 0
    
    for startup in database:
        name = startup.get('name', '')
        
        # Check if already enriched
        if startup.get('is_enriched'):
            updated_count += 1
            continue
        
        # Check enriched lookup
        if name in enriched_lookup:
            enriched = enriched_lookup[name]
            startup['is_enriched'] = True
            startup['last_enriched_date'] = enriched.get('last_enriched_date') or datetime.utcnow().isoformat()
            startup['enrichment'] = enriched.get('enrichment', {})
            updated_count += 1
    
    logger.info(f"✓ Merged enrichment into {updated_count} startups")
    
    # Get stats
    total = len(database)
    enriched = sum(1 for s in database if s.get('is_enriched'))
    
    logger.info(f"\nDatabase Status:")
    logger.info(f"  Total:    {total}")
    logger.info(f"  Enriched: {enriched}")
    logger.info(f"  Remaining: {total - enriched}")
    logger.info(f"  Completion: {enriched/total*100:.1f}%")
    
    # Backup original
    backup_path = database_file.with_suffix('.json.backup')
    if not backup_path.exists():
        logger.info(f"\nCreating backup: {backup_path.name}")
        try:
            with open(database_file, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            logger.info("✓ Backup created")
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")
    
    # Save main database
    logger.info(f"\nSaving to {database_file.name}...")
    try:
        with open(database_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        logger.info("✓ Main database updated")
    except Exception as e:
        logger.error(f"Failed to save database: {e}")
        sys.exit(1)
    
    # Save app copy
    if app_database.parent.exists():
        logger.info(f"Saving to {app_database.name}...")
        try:
            with open(app_database, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            logger.info("✓ App copy updated")
        except Exception as e:
            logger.warning(f"Could not update app copy: {e}")
    
    # Verification
    logger.info("\n" + "="*60)
    logger.info("VERIFICATION")
    logger.info("="*60)
    
    with open(database_file, 'r', encoding='utf-8') as f:
        verify_db = json.load(f)
    
    verify_enriched = [s for s in verify_db if s.get('is_enriched')]
    
    logger.info(f"Total startups: {len(verify_db)}")
    logger.info(f"Enriched: {len(verify_enriched)}")
    
    # Count fields
    with_emails = sum(1 for s in verify_enriched if s.get('enrichment', {}).get('emails'))
    with_social = sum(1 for s in verify_enriched if s.get('enrichment', {}).get('social_media'))
    with_tech = sum(1 for s in verify_enriched if s.get('enrichment', {}).get('tech_stack'))
    with_team = sum(1 for s in verify_enriched if s.get('enrichment', {}).get('team_members'))
    
    logger.info(f"\nField Coverage:")
    logger.info(f"  With Emails: {with_emails}")
    logger.info(f"  With Social: {with_social}")
    logger.info(f"  With Tech Stack: {with_tech}")
    logger.info(f"  With Team Info: {with_team}")
    
    logger.info("\n" + "="*60)
    logger.info("✓ DEPLOYMENT COMPLETE")
    logger.info("="*60)
    logger.info("\nYour enriched data is ready to use!")
    logger.info("\nNext steps:")
    logger.info("  1. Restart API: source .venv/bin/activate && uvicorn api/main:app --reload")
    logger.info("  2. Test endpoints: python3 api/enriched_data_examples.py")
    logger.info("  3. Query API: curl http://localhost:8000/startups/enrichment/stats")

if __name__ == "__main__":
    main()
