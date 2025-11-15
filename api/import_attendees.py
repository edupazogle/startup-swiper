#!/usr/bin/env python3
"""
Import attendees from slush_people.csv to database
"""

import csv
import json
import sys
import hashlib
from pathlib import Path
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

def parse_json_field(value):
    """Parse JSON string field safely"""
    if not value or value.strip() in ['[]', '']:
        return None
    try:
        return json.loads(value)
    except:
        return None

def parse_occupations(value):
    """Parse occupation field which is a JSON array of strings"""
    if not value or value.strip() in ['[]', '']:
        return None
    try:
        occupations = json.loads(value)
        if isinstance(occupations, list):
            return occupations
    except:
        pass
    return None

def parse_industries(value):
    """Parse industry field which is a JSON array of strings"""
    if not value or value.strip() in ['[]', '']:
        return None
    try:
        industries = json.loads(value)
        if isinstance(industries, list):
            return industries
    except:
        pass
    return None

def generate_id(name, email_or_index):
    """Generate a unique ID based on name and email/index"""
    return hashlib.md5(f"{name}-{email_or_index}".encode()).hexdigest()

def import_attendees(csv_path: str):
    """Import attendees from CSV file"""
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return False
    
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    imported_count = 0
    skipped_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:  # Use utf-8-sig to handle BOM
            reader = csv.DictReader(f)
            
            for idx, row in enumerate(reader, 1):
                try:
                    name = row.get('name', '').strip()
                    
                    # Skip empty rows
                    if not name:
                        skipped_count += 1
                        continue
                    
                    # Generate unique ID
                    attendee_id = generate_id(name, idx)
                    
                    # Check if already exists
                    existing = db.query(models.Attendee).filter(
                        models.Attendee.id == attendee_id
                    ).first()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Parse occupations field
                    occupations = parse_occupations(row.get('user_occupation', ''))
                    
                    # Parse industries field
                    industries = parse_industries(row.get('user_industry', ''))
                    
                    # Create attendee
                    attendee = models.Attendee(
                        id=attendee_id,
                        name=name,
                        title=row.get('title', '').strip() or None,
                        country=row.get('user_country', '').strip() or None,
                        city=row.get('user_city', '').strip() or None,
                        linkedin=row.get('user_linked_in', '').strip() or None,
                        twitter=row.get('twitter', '').strip() or None,
                        bio=row.get('user_bio', '').strip() or None,
                        industry=industries,
                        occupation=occupations,
                        company_name=row.get('company_name', '').strip() or None,
                        company_type=row.get('company_type', '').strip() or None,
                        company_country=row.get('company_country', '').strip() or None,
                        company_city=row.get('company_city', '').strip() or None,
                        website=row.get('website', '').strip() or None,
                        company_linkedin=row.get('company_linked_in', '').strip() or None,
                        company_description=row.get('company_description', '').strip() or None,
                        profile_link=row.get('profile_link', '').strip() or None,
                    )
                    
                    db.add(attendee)
                    imported_count += 1
                    
                    if imported_count % 100 == 0:
                        print(f"  ✓ Imported {imported_count} attendees...")
                        db.commit()
                
                except Exception as e:
                    print(f"⚠️  Error importing row {idx}: {e}")
                    skipped_count += 1
                    continue
            
            # Final commit
            db.commit()
        
        print(f"\n✅ Import complete!")
        print(f"   Total imported: {imported_count}")
        print(f"   Total skipped: {skipped_count}")
        
        # Print statistics
        total = db.query(models.Attendee).count()
        print(f"\n📊 Database statistics:")
        print(f"   Total attendees: {total}")
        
        # Sample some attendees
        samples = db.query(models.Attendee).limit(5).all()
        print(f"\n📝 Sample attendees:")
        for attendee in samples:
            company = f" @ {attendee.company_name}" if attendee.company_name else ""
            print(f"   • {attendee.name}{company} ({attendee.country})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    csv_file = Path(__file__).parent.parent / "downloads" / "slush_people.csv"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    print(f"🔄 Importing attendees from: {csv_file}\n")
    import_attendees(str(csv_file))
