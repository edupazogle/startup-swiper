#!/usr/bin/env python3
"""
Import Slush events from JSON file into the database
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

import models
import crud
from database import engine, SessionLocal

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("✅ Tables created")

def parse_datetime(dt_string: str) -> datetime:
    """Parse datetime from scraped_at field"""
    try:
        return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    except:
        return datetime.utcnow()

def import_events_from_json(json_file_path: str, db: Session, clear_existing: bool = False):
    """Import events from JSON file"""
    
    # Load JSON file
    json_path = Path(json_file_path)
    if not json_path.exists():
        print(f"❌ File not found: {json_file_path}")
        return 0
    
    print(f"Reading events from {json_file_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
    
    print(f"Found {len(events_data)} events in JSON file")
    
    # Clear existing events if requested
    if clear_existing:
        print("Clearing existing events...")
        deleted_count = crud.delete_all_slush_events(db)
        print(f"✅ Deleted {deleted_count} existing events")
    
    # Prepare events for bulk insert
    events_to_insert = []
    for event_data in events_data:
        event_dict = {
            'title': event_data['title'],
            'organizer': event_data['organizer'],
            'datetime': event_data['datetime'],
            'location': event_data.get('location'),
            'categories': event_data.get('categories', []),
            'status': event_data.get('status', []),
            'scraped_at': parse_datetime(event_data['scraped_at']),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        events_to_insert.append(event_dict)
    
    # Bulk insert
    print(f"Inserting {len(events_to_insert)} events into database...")
    inserted_count = crud.create_slush_events_bulk(db, events_to_insert)
    print(f"✅ Successfully inserted {inserted_count} events")
    
    return inserted_count

def main():
    """Main import function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import Slush events from JSON into database")
    parser.add_argument(
        'json_file',
        nargs='?',
        default='../scrapper/slush_events_data/slush_events_full.json',
        help='Path to JSON file (default: ../scrapper/slush_events_data/slush_events_full.json)'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing events before importing'
    )
    
    args = parser.parse_args()
    
    # Resolve path relative to script location
    script_dir = Path(__file__).parent
    json_path = script_dir / args.json_file
    
    print("="*70)
    print("Slush Events Database Import")
    print("="*70)
    
    # Create tables
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Import events
        count = import_events_from_json(str(json_path), db, clear_existing=args.clear)
        
        # Show summary
        print("\n" + "="*70)
        print("Import Summary")
        print("="*70)
        total_events = len(crud.get_slush_events(db, limit=10000))
        print(f"Total events in database: {total_events}")
        
        # Show sample events
        print("\nSample events:")
        sample_events = crud.get_slush_events(db, limit=5)
        for event in sample_events:
            print(f"  • {event.title} by {event.organizer}")
            print(f"    {event.datetime} | {event.location}")
            if event.status:
                print(f"    Status: {', '.join(event.status)}")
            print()
        
        print("="*70)
        print(f"✅ Import completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
