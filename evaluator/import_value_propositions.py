#!/usr/bin/env python3
"""
Import Value Propositions into Database

Imports generated value propositions into the startup database.
Adds new fields if they don't exist.

Usage:
    python3 evaluator/import_value_propositions.py
    python3 evaluator/import_value_propositions.py --input evaluator/downloads/value_propositions.json
"""

import json
import argparse
from pathlib import Path
import sys
import logging

# Add parent and api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from database import SessionLocal, engine
from models_startup import Startup
from sqlalchemy import Column, String, text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def ensure_value_prop_fields():
    """Ensure value proposition fields exist in database"""
    
    logger.info("🔧 Checking database schema...")
    
    with engine.connect() as conn:
        # For SQLite, use PRAGMA table_info
        result = conn.execute(text("PRAGMA table_info(startups)"))
        existing_columns = set(row[1] for row in result)
        
        # Add missing columns
        columns_to_add = {
            'value_proposition': 'TEXT',
            'core_product': 'TEXT',
            'target_customers': 'TEXT',
            'problem_solved': 'TEXT',
            'key_differentiator': 'TEXT',
            'business_model': 'VARCHAR(255)',
            'vp_competitors': 'TEXT',
            'vp_confidence': 'VARCHAR(50)',
            'vp_reasoning': 'TEXT'
        }
        
        added_count = 0
        for col_name, col_type in columns_to_add.items():
            if col_name not in existing_columns:
                try:
                    logger.info(f"  Adding column: {col_name}")
                    conn.execute(text(f"ALTER TABLE startups ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    added_count += 1
                except Exception as e:
                    logger.warning(f"  Could not add {col_name}: {e}")
        
        if added_count > 0:
            logger.info(f"✓ Added {added_count} new columns")
        else:
            logger.info("✓ All columns already exist")


def import_value_propositions(input_file: Path):
    """Import value propositions from JSON file"""
    
    # Ensure fields exist
    ensure_value_prop_fields()
    
    # Load JSON data
    logger.info(f"📂 Loading value propositions from {input_file}")
    with open(input_file) as f:
        data = json.load(f)
    
    value_props = data.get('value_propositions', [])
    logger.info(f"   Found {len(value_props)} value propositions")
    
    # Import into database
    db = SessionLocal()
    try:
        updated_count = 0
        not_found_count = 0
        
        for vp in value_props:
            company_name = vp.get('company_name')
            
            # Find startup
            startup = db.query(Startup).filter(
                Startup.company_name == company_name
            ).first()
            
            if not startup:
                logger.warning(f"⚠ Company not found: {company_name}")
                not_found_count += 1
                continue
            
            # Update value proposition fields
            # Convert lists to JSON strings for storage
            target_customers = vp.get('target_customers')
            if isinstance(target_customers, list):
                target_customers = json.dumps(target_customers)
            
            competitors = vp.get('competitors')
            if isinstance(competitors, list):
                competitors = json.dumps(competitors)
            
            startup.value_proposition = vp.get('value_proposition')
            startup.core_product = vp.get('core_product')
            startup.target_customers = target_customers
            startup.problem_solved = vp.get('problem_solved')
            startup.key_differentiator = vp.get('key_differentiator')
            startup.business_model = vp.get('business_model')
            startup.vp_competitors = competitors
            startup.vp_confidence = vp.get('confidence')
            startup.vp_reasoning = vp.get('reasoning')
            
            updated_count += 1
            logger.info(f"  ✓ Updated: {company_name}")
        
        # Commit changes
        db.commit()
        
        logger.info(f"\n✓ Successfully updated {updated_count} startups")
        if not_found_count > 0:
            logger.warning(f"⚠ {not_found_count} companies not found in database")
        
    except Exception as e:
        logger.error(f"✗ Error importing: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description='Import value propositions into database')
    parser.add_argument('--input', type=str, 
                       default='evaluator/downloads/value_propositions.json',
                       help='Input JSON file path')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        logger.error(f"✗ File not found: {input_path}")
        sys.exit(1)
    
    import_value_propositions(input_path)
    
    print("\n" + "="*80)
    print("VALUE PROPOSITION IMPORT COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
