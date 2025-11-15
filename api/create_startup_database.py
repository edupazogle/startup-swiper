#!/usr/bin/env python3
"""
Create and populate the startups database table
Imports enriched startup data into SQLite database
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models_startup import Base, Startup

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def parse_datetime(date_str):
    """Parse ISO datetime string"""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return None

def parse_float(value):
    """Parse float value safely"""
    if value is None or value == '':
        return None
    try:
        return float(value)
    except:
        return None

def parse_int(value):
    """Parse integer value safely"""
    if value is None or value == '':
        return None
    try:
        return int(value)
    except:
        return None

def create_database(db_path: str):
    """Create database and tables"""
    logger.info(f"Creating database at {db_path}")
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine

def load_startup_data(json_path: str) -> list:
    """Load enriched startup data from JSON"""
    logger.info(f"Loading startup data from {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def import_startups(engine, startups_data):
    """Import startups into database"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    logger.info(f"Importing {len(startups_data)} startups...")
    
    imported = 0
    skipped = 0
    errors = 0
    
    for idx, data in enumerate(startups_data):
        try:
            # Skip records without company name (required field)
            company_name = data.get('company_name')
            if not company_name or company_name.strip() == '':
                skipped += 1
                continue
            
            # Check if startup already exists
            existing = session.query(Startup).filter_by(
                company_name=company_name
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            # Create startup record
            startup = Startup(
                # ID and basic info
                id=data.get('id'),
                company_name=company_name,
                company_type=data.get('company_type'),
                company_country=data.get('company_country'),
                company_city=data.get('company_city'),
                website=data.get('website', ''),  # Provide empty string if None
                company_linked_in=data.get('company_linked_in'),
                company_description=data.get('company_description'),
                founding_year=parse_int(data.get('founding_year')),
                
                # Industry
                primary_industry=data.get('primary_industry'),
                secondary_industry=data.get('secondary_industry'),
                focus_industries=data.get('focus_industries'),
                business_types=data.get('business_types'),
                
                # Categories
                curated_collections_tags=data.get('curated_collections_tags'),
                topics=data.get('topics'),
                tech=data.get('tech'),
                
                # Funding
                prominent_investors=data.get('prominent_investors'),
                currentInvestmentStage=data.get('currentInvestmentStage'),
                totalFunding=parse_float(data.get('totalFunding')),
                originalTotalFunding=parse_float(data.get('originalTotalFunding')),
                originalTotalFundingCurrency=data.get('originalTotalFundingCurrency'),
                lastFundingDate=parse_datetime(data.get('lastFundingDate')),
                lastFunding=parse_float(data.get('lastFunding')),
                originalLastFunding=parse_float(data.get('originalLastFunding')),
                originalLastFundingCurrency=data.get('originalLastFundingCurrency'),
                fundingIsUndisclosed=data.get('fundingIsUndisclosed', False),
                
                # Company details
                employees=data.get('employees'),
                legalEntity=data.get('legalEntity'),
                shortDescription=data.get('shortDescription'),
                description=data.get('description'),
                technologyReadiness=data.get('technologyReadiness'),
                pricingModel=data.get('pricingModel'),
                maturity=data.get('maturity'),
                maturity_score=parse_int(data.get('maturity_score')),
                
                # Location
                billingCountry=data.get('billingCountry'),
                billingState=data.get('billingState'),
                billingCity=data.get('billingCity'),
                billingStreet=data.get('billingStreet'),
                billingPostalCode=data.get('billingPostalCode'),
                
                # External IDs
                sfId=data.get('sfId'),
                pitchbookId=data.get('pitchbookId'),
                mainContactId=parse_int(data.get('mainContactId')),
                parentCompanyId=parse_int(data.get('parentCompanyId')),
                profile_link=data.get('profile_link'),
                
                # Assets
                logoUrl=data.get('logoUrl'),
                files=data.get('files'),
                
                # Platform
                featuredLists=data.get('featuredLists'),
                opportunities=data.get('opportunities'),
                leadOpportunities=data.get('leadOpportunities'),
                
                # Quality
                isMissingValidation=data.get('isMissingValidation', False),
                isQualityChecked=data.get('isQualityChecked'),
                qualityChecks=data.get('qualityChecks'),
                lastQualityCheckDate=parse_datetime(data.get('lastQualityCheckDate')),
                lastQualityCheckById=parse_int(data.get('lastQualityCheckById')),
                lastQualityCheckBy=json.dumps(data.get('lastQualityCheckBy')) if isinstance(data.get('lastQualityCheckBy'), dict) else data.get('lastQualityCheckBy'),
                
                # Enrichment
                is_enriched=data.get('is_enriched', False),
                last_enriched_date=parse_datetime(data.get('last_enriched_date')),
                enrichment=data.get('enrichment'),
                
                # Timestamps
                dateCreated=parse_datetime(data.get('dateCreated')),
                dateFounded=parse_datetime(data.get('dateFounded')),
                lastModifiedDate=parse_datetime(data.get('lastModifiedDate')),
                lastModifiedById=parse_int(data.get('lastModifiedById')),
                lastPitchbookSync=parse_datetime(data.get('lastPitchbookSync'))
            )
            
            session.add(startup)
            imported += 1
            
            # Commit in batches to avoid large memory usage
            if imported % 100 == 0:
                try:
                    session.commit()
                    logger.info(f"Imported {imported} startups...")
                except Exception as batch_error:
                    logger.warning(f"Batch commit error, rolling back: {batch_error}")
                    session.rollback()
                    errors += 100  # Count the batch that failed
                
        except Exception as e:
            logger.error(f"Error importing startup {data.get('company_name', 'Unknown')}: {e}")
            errors += 1
            # Don't rollback on individual errors, just skip the record
    
    # Final commit
    try:
        session.commit()
    except Exception as e:
        logger.error(f"Final commit failed: {e}")
        session.rollback()
    finally:
        session.close()
    
    return imported, skipped, errors

def main():
    base_path = Path(__file__).parent.parent
    
    # Paths
    db_path = base_path / "startup_swiper.db"
    json_path = base_path / "docs/architecture/ddbb/slush_full_list.json"
    
    logger.info("="*70)
    logger.info("STARTUP DATABASE CREATION")
    logger.info("="*70)
    
    # Create database
    engine = create_database(str(db_path))
    
    # Load data
    startups_data = load_startup_data(str(json_path))
    
    # Import
    imported, skipped, errors = import_startups(engine, startups_data)
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("IMPORT COMPLETE")
    logger.info("="*70)
    logger.info(f"Total startups:    {len(startups_data)}")
    logger.info(f"Imported:          {imported}")
    logger.info(f"Skipped:           {skipped} (already exist)")
    logger.info(f"Errors:            {errors}")
    logger.info(f"Database:          {db_path}")
    logger.info("="*70)
    
    # Show enrichment stats
    from sqlalchemy import func
    Session = sessionmaker(bind=engine)
    session = Session()
    
    total = session.query(func.count(Startup.id)).scalar()
    enriched = session.query(func.count(Startup.id)).filter(Startup.is_enriched == True).scalar()
    with_funding = session.query(func.count(Startup.id)).filter(Startup.totalFunding != None).scalar()
    with_logo = session.query(func.count(Startup.id)).filter(Startup.logoUrl != None).scalar()
    
    logger.info("\nENRICHMENT STATISTICS")
    logger.info("="*70)
    logger.info(f"Total startups:           {total}")
    logger.info(f"Enriched (web data):      {enriched} ({enriched/total*100:.1f}%)")
    logger.info(f"With funding info:        {with_funding} ({with_funding/total*100:.1f}%)")
    logger.info(f"With logo:                {with_logo} ({with_logo/total*100:.1f}%)")
    logger.info("="*70)
    
    session.close()
    
    logger.info("\n✓ Database created successfully!")

if __name__ == "__main__":
    main()
