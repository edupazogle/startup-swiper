#!/usr/bin/env python3
"""
Update AXA Evaluation Data from Checkpoint

Reads axa_enhanced_checkpoint_1000.json.backup and updates the database
with new AXA evaluation data, replacing old evaluation with new one.

Usage:
    python3 api/update_axa_evaluation.py
    python3 api/update_axa_evaluation.py --dry-run  (to preview without updating)
    python3 api/update_axa_evaluation.py --verbose  (detailed progress)
"""

import json
import sys
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Configuration
DB_PATH = "startup_swiper.db"
CHECKPOINT_PATH = "downloads/axa_enhanced_checkpoint_1000.json.backup"


def load_checkpoint(checkpoint_path: str) -> Dict[str, Any]:
    """Load the AXA checkpoint JSON file"""
    path = Path(checkpoint_path)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")
    
    print(f"📖 Loading checkpoint from {checkpoint_path}...")
    with open(path, 'r') as f:
        data = json.load(f)
    
    print(f"✓ Checkpoint loaded")
    print(f"  - Total IDs evaluated: {len(data.get('evaluated_ids', []))}")
    print(f"  - Results records: {len(data.get('results', []))}")
    print(f"  - Last updated: {data.get('last_updated')}")
    print(f"  - Stats: {data.get('stats')}")
    
    return data


def create_connection(db_path: str):
    """Create database connection"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"✗ Connection failed: {e}")
        return None


def validate_database(conn):
    """Verify database connection and schema"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM startups")
        count = cursor.fetchone()[0]
        print(f"✓ Database connected - {count} startups in database")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def ensure_columns_exist(conn):
    """Ensure all required AXA columns exist in database"""
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(startups)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    # Required columns mapping
    required_columns = {
        'axa_evaluation_date': 'DATETIME',
        'axa_overall_score': 'REAL',
        'axa_priority_tier': 'TEXT',
        'axa_categories_matched': 'JSON',
        'axa_fit_summary': 'TEXT',
        'axa_can_use_as_provider': 'BOOLEAN',
        'axa_business_leverage': 'TEXT',
        'axa_matched_rules': 'JSON',
        'axa_rule_scores': 'JSON',
    }
    
    # Add missing columns
    added_count = 0
    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            print(f"  Adding column: {col_name}")
            try:
                cursor.execute(f"ALTER TABLE startups ADD COLUMN {col_name} {col_type}")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"    Warning: {e}")
    
    if added_count > 0:
        print(f"✓ Added {added_count} missing columns")
        conn.commit()
    else:
        print(f"✓ All required columns exist")


def update_database(conn, checkpoint_data: Dict[str, Any], dry_run: bool = False, verbose: bool = False):
    """Update database with evaluation results using raw SQL"""
    
    results = checkpoint_data.get('results', [])
    total_count = len(results)
    updated_count = 0
    skipped_count = 0
    error_count = 0
    errors = []
    
    cursor = conn.cursor()
    
    print(f"\n📊 Processing {total_count} evaluation records...")
    
    for idx, evaluation in enumerate(results, 1):
        startup_id = evaluation.get('startup_id')
        startup_name = evaluation.get('startup_name', 'Unknown')
        
        try:
            # Check if startup exists
            cursor.execute("SELECT id FROM startups WHERE id = ?", (startup_id,))
            if not cursor.fetchone():
                skipped_count += 1
                if verbose:
                    print(f"  ⚠ [{idx:4d}/{total_count}] ID {startup_id} not found in database")
                continue
            
            # Prepare update data
            eval_date = evaluation.get('evaluation_date')
            if isinstance(eval_date, str):
                try:
                    eval_date = datetime.fromisoformat(eval_date.replace('Z', '+00:00')).isoformat()
                except:
                    eval_date = None
            
            # Execute update
            cursor.execute("""
                UPDATE startups SET
                    axa_evaluation_date = ?,
                    axa_overall_score = ?,
                    axa_priority_tier = ?,
                    axa_categories_matched = ?,
                    axa_fit_summary = ?,
                    axa_can_use_as_provider = ?,
                    axa_business_leverage = ?,
                    axa_matched_rules = ?,
                    axa_rule_scores = ?
                WHERE id = ?
            """, (
                eval_date,
                evaluation.get('overall_score'),
                evaluation.get('priority_tier'),
                json.dumps(evaluation.get('categories_matched', [])),
                evaluation.get('axa_fit_summary'),
                1 if evaluation.get('can_use_as_provider') else 0,
                evaluation.get('business_leverage'),
                json.dumps(evaluation.get('matched_rules', [])),
                json.dumps(evaluation.get('rule_scores', {})),
                startup_id
            ))
            
            updated_count += 1
            
            if verbose:
                print(f"  ✓ [{idx:4d}/{total_count}] {startup_name} (ID {startup_id}) - Score: {evaluation.get('overall_score'):.1f}% - Tier: {evaluation.get('priority_tier')}")
            elif idx % 50 == 0:
                print(f"  [{idx:4d}/{total_count}] Processing... ({updated_count} updated, {skipped_count} skipped)")
        
        except Exception as e:
            error_count += 1
            error_msg = f"ID {startup_id} ({startup_name}): {str(e)}"
            errors.append(error_msg)
            if verbose:
                print(f"  ✗ [{idx:4d}/{total_count}] Error - {error_msg}")
    
    # Commit if not dry-run
    if not dry_run:
        print(f"\n💾 Committing changes...")
        try:
            conn.commit()
            print(f"✓ Database committed successfully")
        except Exception as e:
            conn.rollback()
            print(f"✗ Commit failed: {e}")
            error_count += 1
    
    # Print summary
    print(f"\n📈 Update Summary:")
    print(f"  ✓ Updated: {updated_count}")
    print(f"  ⚠ Skipped: {skipped_count}")
    print(f"  ✗ Errors: {error_count}")
    print(f"  {'(DRY RUN - no changes made)' if dry_run else '✓ COMMITTED TO DATABASE'}")
    
    if errors and len(errors) <= 10:
        print(f"\n📋 Errors:")
        for error in errors:
            print(f"  - {error}")
    elif errors:
        print(f"\n📋 First 10 errors (of {len(errors)} total):")
        for error in errors[:10]:
            print(f"  - {error}")
    
    return updated_count, skipped_count, error_count


def print_sample_records(conn, count: int = 5):
    """Print sample of updated records"""
    print(f"\n📋 Sample of updated records (top {count} by score):")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, company_name, axa_overall_score, axa_priority_tier, 
               axa_can_use_as_provider, axa_matched_rules, axa_fit_summary
        FROM startups
        WHERE axa_overall_score IS NOT NULL
        ORDER BY axa_overall_score DESC
        LIMIT ?
    """, (count,))
    
    records = cursor.fetchall()
    
    for idx, row in enumerate(records, 1):
        print(f"\n  [{idx}] {row['company_name']} (ID {row['id']})")
        print(f"      Score: {row['axa_overall_score']:.1f}%")
        print(f"      Tier: {row['axa_priority_tier']}")
        print(f"      Provider: {bool(row['axa_can_use_as_provider'])}")
        rules = json.loads(row['axa_matched_rules']) if row['axa_matched_rules'] else []
        print(f"      Rules: {rules}")
        summary = row['axa_fit_summary']
        if summary:
            print(f"      Summary: {summary[:80]}...")


def main():
    parser = argparse.ArgumentParser(
        description='Update AXA Evaluation Data from Checkpoint'
    )
    parser.add_argument('--dry-run', action='store_true', 
                        help='Preview changes without updating database')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed progress for each record')
    parser.add_argument('--no-sample', action='store_true',
                        help='Skip printing sample records')
    
    args = parser.parse_args()
    
    try:
        # Load checkpoint
        checkpoint_data = load_checkpoint(CHECKPOINT_PATH)
        
        # Create database connection
        conn = create_connection(DB_PATH)
        if not conn:
            return 1
        
        # Validate database
        if not validate_database(conn):
            print("✗ Database validation failed")
            return 1
        
        # Ensure all columns exist
        ensure_columns_exist(conn)
        
        # Update database
        updated, skipped, errors = update_database(
            conn, 
            checkpoint_data,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        # Print sample records if update was successful
        if updated > 0 and not args.no_sample:
            print_sample_records(conn, count=3)
        
        conn.close()
        
        print(f"\n✓ Update complete")
        return 0 if errors == 0 else 1
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
