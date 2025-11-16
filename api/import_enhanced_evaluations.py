#!/usr/bin/env python3
"""
Import Enhanced AXA Evaluations into Database
Imports evaluation results from JSON file to startup_swiper.db
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

from database import SessionLocal
from models_startup import Startup
from sqlalchemy import text

# Add evaluator directory to path for topic_mapping
sys.path.insert(0, str(Path(__file__).parent.parent / "evaluator"))
from topic_mapping import convert_topic_code_to_name, convert_use_case_code_to_name

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def import_evaluations(json_file: str, dry_run: bool = False):
    """Import evaluations from JSON file into database"""
    
    # Load JSON data
    logger.info(f"📖 Loading evaluations from {json_file}")
    with open(json_file, 'r') as f:
        evaluations = json.load(f)
    
    logger.info(f"✅ Loaded {len(evaluations)} evaluations")
    
    # Connect to database
    db = SessionLocal()
    
    stats = {
        'total': len(evaluations),
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'tier_1': 0,
        'tier_2': 0,
        'tier_3': 0,
        'tier_4': 0,
        'providers': 0,
        'non_providers': 0
    }
    
    try:
        for idx, eval_data in enumerate(evaluations, 1):
            startup_id = eval_data['startup_id']
            
            if idx % 100 == 0:
                logger.info(f"⏳ Processing {idx}/{len(evaluations)}...")
            
            try:
                # Get startup from database
                startup = db.query(Startup).filter(Startup.id == startup_id).first()
                
                if not startup:
                    logger.warning(f"⚠️  Startup {startup_id} not found in database")
                    stats['skipped'] += 1
                    continue
                
                # Count stats regardless of dry-run
                tier = eval_data.get('priority_tier', '')
                if 'Tier 1' in tier:
                    stats['tier_1'] += 1
                elif 'Tier 2' in tier:
                    stats['tier_2'] += 1
                elif 'Tier 3' in tier:
                    stats['tier_3'] += 1
                elif 'Tier 4' in tier:
                    stats['tier_4'] += 1
                
                if eval_data.get('can_use_as_provider', False):
                    stats['providers'] += 1
                else:
                    stats['non_providers'] += 1
                
                if dry_run:
                    logger.debug(f"[DRY RUN] Would update startup {startup_id} ({eval_data['startup_name']})")
                    stats['updated'] += 1
                    continue
                
                # Update startup with evaluation data
                # Parse datetime string if present
                eval_date_str = eval_data.get('evaluation_date')
                if eval_date_str:
                    try:
                        startup.axa_evaluation_date = datetime.fromisoformat(eval_date_str)
                    except:
                        startup.axa_evaluation_date = datetime.now()
                else:
                    startup.axa_evaluation_date = datetime.now()
                
                startup.axa_overall_score = float(eval_data.get('overall_score', 0))
                startup.axa_priority_tier = eval_data.get('priority_tier', 'Tier 4: Low Priority')
                startup.axa_fit_summary = eval_data.get('axa_fit_summary', '')
                startup.axa_can_use_as_provider = eval_data.get('can_use_as_provider', False)
                startup.axa_business_leverage = eval_data.get('business_leverage', '')
                
                # Store matched topics, categories, and scores as JSON
                startup.axa_categories_matched = json.dumps(eval_data.get('categories_matched', []))
                startup.axa_matched_rules = json.dumps(eval_data.get('matched_topics', []))  # Store topics in old rules field for compatibility
                startup.axa_rule_scores = json.dumps(eval_data.get('topic_scores', {}))
                
                # Extract primary topic and use cases
                # Use friendly names if available, otherwise convert from codes
                primary_topic_code = eval_data.get('primary_topic', 'Topic 11')
                primary_topic_name = eval_data.get('primary_topic_name') or convert_topic_code_to_name(primary_topic_code)
                startup.axa_primary_topic = primary_topic_name  # Store friendly name
                
                # Convert use case codes to friendly names
                use_case_codes = eval_data.get('use_cases', [])
                use_case_names = eval_data.get('use_case_names') or [convert_use_case_code_to_name(uc) for uc in use_case_codes]
                startup.axa_use_cases = json.dumps(use_case_names)  # Store friendly names as JSON array
                
                # Update stats
                stats['updated'] += 1
                
                # Commit every 100 records
                if idx % 100 == 0:
                    db.commit()
                    logger.info(f"💾 Committed batch at {idx}/{len(evaluations)}")
            
            except Exception as e:
                logger.error(f"❌ Error processing startup {startup_id}: {e}")
                stats['errors'] += 1
                db.rollback()  # Rollback failed transaction
                continue
        
        # Final commit
        if not dry_run:
            db.commit()
            logger.info("💾 Final commit complete")
    
    finally:
        db.close()
    
    # Print summary
    print("\n" + "="*70)
    print("📊 IMPORT SUMMARY")
    print("="*70)
    print(f"Total evaluations:     {stats['total']}")
    print(f"✅ Updated:            {stats['updated']}")
    print(f"⏭️  Skipped:            {stats['skipped']}")
    print(f"❌ Errors:             {stats['errors']}")
    print()
    print("By Tier:")
    print(f"  Tier 1 (Must Meet):       {stats['tier_1']}")
    print(f"  Tier 2 (High Priority):   {stats['tier_2']}")
    print(f"  Tier 3 (Medium Priority): {stats['tier_3']}")
    print(f"  Tier 4 (Low Priority):    {stats['tier_4']}")
    print()
    print("By Provider Status:")
    print(f"  ✓ Usable as provider:     {stats['providers']}")
    print(f"  ✗ Not provider:           {stats['non_providers']}")
    print("="*70)
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes were made to database")
    else:
        print("\n✅ Import complete! Database updated successfully.")


def verify_import(db_session):
    """Verify the import worked"""
    logger.info("\n🔍 Verifying import...")
    
    # Count evaluations
    total = db_session.query(Startup).filter(Startup.axa_evaluation_date != None).count()
    providers = db_session.query(Startup).filter(Startup.axa_can_use_as_provider == True).count()
    
    # Count by tier
    tier_1 = db_session.query(Startup).filter(Startup.axa_priority_tier.like('%Tier 1%')).count()
    tier_2 = db_session.query(Startup).filter(Startup.axa_priority_tier.like('%Tier 2%')).count()
    tier_3 = db_session.query(Startup).filter(Startup.axa_priority_tier.like('%Tier 3%')).count()
    
    print("\n" + "="*70)
    print("🔍 DATABASE VERIFICATION")
    print("="*70)
    print(f"Total startups with evaluations: {total}")
    print(f"Usable as providers:             {providers}")
    print()
    print("By Tier:")
    print(f"  Tier 1: {tier_1}")
    print(f"  Tier 2: {tier_2}")
    print(f"  Tier 3: {tier_3}")
    print("="*70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Import AXA Enhanced Evaluations to Database')
    parser.add_argument('--input', type=str, default='downloads/axa_enhanced_results.json',
                       help='Input JSON file with evaluations')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run - show what would be imported without making changes')
    parser.add_argument('--verify', action='store_true',
                       help='Verify import after completion')
    
    args = parser.parse_args()
    
    # Check if input file exists
    input_file = Path(args.input)
    if not input_file.exists():
        logger.error(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("🚀 AXA ENHANCED EVALUATIONS IMPORTER")
    print("="*70)
    print(f"Input file: {input_file}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE IMPORT'}")
    print("="*70 + "\n")
    
    # Run import
    import_evaluations(str(input_file), dry_run=args.dry_run)
    
    # Verify if requested
    if args.verify and not args.dry_run:
        db = SessionLocal()
        try:
            verify_import(db)
        finally:
            db.close()


if __name__ == '__main__':
    main()
