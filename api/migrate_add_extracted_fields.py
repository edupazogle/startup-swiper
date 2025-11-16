#!/usr/bin/env python3
"""
Add extracted product fields to startups table and populate from CSV
"""

import csv
from database import SessionLocal, engine
from models_startup import Startup
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_columns_if_not_exist():
    """Add new columns to startups table"""
    with engine.connect() as conn:
        # Check if columns exist
        result = conn.execute(text("PRAGMA table_info(startups)"))
        existing_columns = {row[1] for row in result}
        
        columns_to_add = {
            'extracted_product': 'TEXT',
            'extracted_market': 'TEXT',
            'extracted_technologies': 'TEXT',
            'extracted_competitors': 'TEXT'
        }
        
        for col_name, col_type in columns_to_add.items():
            if col_name not in existing_columns:
                logger.info(f"Adding column {col_name}...")
                conn.execute(text(f"ALTER TABLE startups ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                logger.info(f"✓ Added {col_name}")
            else:
                logger.info(f"Column {col_name} already exists")

def populate_from_csv():
    """Populate extracted fields from CSV"""
    csv_path = '../startups_extracted_data.csv'
    
    db = SessionLocal()
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            updated = 0
            not_found = 0
            
            for row in reader:
                company_name = row.get('company_name', '').strip()
                if not company_name:
                    continue
                
                # Find startup by name
                startup = db.query(Startup).filter(
                    Startup.company_name == company_name
                ).first()
                
                if startup:
                    # Update extracted fields
                    startup.extracted_product = row.get('extracted_product', '').strip() or None
                    startup.extracted_market = row.get('extracted_market', '').strip() or None
                    startup.extracted_technologies = row.get('extracted_technologies', '').strip() or None
                    startup.extracted_competitors = row.get('extracted_competitors', '').strip() or None
                    
                    updated += 1
                    if updated % 100 == 0:
                        logger.info(f"Updated {updated} startups...")
                        db.commit()
                else:
                    not_found += 1
            
            db.commit()
            logger.info(f"✓ Updated {updated} startups with extracted data")
            logger.info(f"  {not_found} companies from CSV not found in database")
            
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Adding extracted fields columns...")
    add_columns_if_not_exist()
    
    logger.info("\nPopulating extracted data from CSV...")
    populate_from_csv()
    
    logger.info("\n✓ Migration complete!")
