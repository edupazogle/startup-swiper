#!/usr/bin/env python3
"""
Migration script to add AXA evaluation columns to the startup database.
Adds:
  - axa_evaluation_date
  - axa_overall_score
  - axa_priority_tier
  - axa_categories_matched (JSON)
  - axa_fit_summary
"""

import sqlite3
import json
from pathlib import Path

def migrate_axa_columns():
    """Add AXA evaluation columns to startups table"""
    
    db_path = Path(__file__).parent.parent / "startup_swiper.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get current table schema
        cursor.execute("PRAGMA table_info(startups)")
        columns = {row[1] for row in cursor.fetchall()}
        
        print("Current columns in startups table:")
        print(f"  {', '.join(sorted(columns))}")
        print()
        
        # Define new columns to add
        new_columns = [
            ("axa_evaluation_date", "TEXT"),
            ("axa_overall_score", "REAL"),
            ("axa_priority_tier", "TEXT"),
            ("axa_categories_matched", "TEXT"),  # JSON string
            ("axa_fit_summary", "TEXT"),
        ]
        
        # Add columns if they don't exist
        added_count = 0
        for col_name, col_type in new_columns:
            if col_name not in columns:
                print(f"Adding column: {col_name} ({col_type})")
                cursor.execute(f"ALTER TABLE startups ADD COLUMN {col_name} {col_type}")
                added_count += 1
            else:
                print(f"✓ Column already exists: {col_name}")
        
        conn.commit()
        conn.close()
        
        if added_count > 0:
            print(f"\n✅ Successfully added {added_count} columns")
        else:
            print("\n✅ All columns already exist")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def populate_axa_evaluation_data():
    """Populate AXA evaluation data from JSON file"""
    
    db_path = Path(__file__).parent.parent / "startup_swiper.db"
    eval_json = Path(__file__).parent.parent / "downloads" / "axa_evaluation_results.json"
    
    if not eval_json.exists():
        print(f"⚠️  Evaluation file not found: {eval_json}")
        return False
    
    try:
        # Load evaluation data
        with open(eval_json) as f:
            eval_data = json.load(f)
        
        print(f"Loaded {len(eval_data)} evaluation records")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        updated_count = 0
        skipped_count = 0
        
        for entry in eval_data:
            startup_id = entry.get('startup_id')
            eval_date = entry.get('evaluation_date')
            overall_score = entry.get('overall_score')
            priority_tier = entry.get('priority_tier')
            categories = entry.get('categories_matched', [])
            fit_summary = entry.get('axa_fit_summary')
            
            # Convert categories to JSON string
            categories_json = json.dumps(categories)
            
            try:
                cursor.execute("""
                    UPDATE startups 
                    SET 
                        axa_evaluation_date = ?,
                        axa_overall_score = ?,
                        axa_priority_tier = ?,
                        axa_categories_matched = ?,
                        axa_fit_summary = ?
                    WHERE id = ?
                """, (eval_date, overall_score, priority_tier, categories_json, fit_summary, startup_id))
                
                if cursor.rowcount > 0:
                    updated_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                print(f"  Error updating startup {startup_id}: {e}")
                skipped_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Updated {updated_count} startups with AXA evaluation data")
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} startups (not found in database)")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 80)
    print("AXA EVALUATION DATA MIGRATION")
    print("=" * 80)
    print()
    
    print("Step 1: Adding AXA evaluation columns...")
    print("-" * 80)
    if not migrate_axa_columns():
        print("❌ Migration failed")
        return False
    
    print()
    print("Step 2: Populating AXA evaluation data...")
    print("-" * 80)
    if not populate_axa_evaluation_data():
        print("⚠️  Could not populate data (file may not exist)")
        return False
    
    print()
    print("=" * 80)
    print("✅ MIGRATION COMPLETE")
    print("=" * 80)
    print()
    print("New columns added:")
    print("  - axa_evaluation_date: Evaluation timestamp")
    print("  - axa_overall_score: Overall AXA fit score (0-100)")
    print("  - axa_priority_tier: Tier 1/2/3 classification")
    print("  - axa_categories_matched: JSON array of matched categories with reasoning")
    print("  - axa_fit_summary: Summary of AXA fit")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
